import asyncio
import logging
import os
import os.path
import posixpath
import subprocess
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    NoReturn,
    Optional,
    Tuple,
    Union,
)
from uuid import uuid4

import sqlalchemy as sa
import yaml
from attrs import asdict
from fsspec.implementations.local import LocalFileSystem
from tqdm import tqdm

from dql.cache import DQLCache
from dql.client import Client
from dql.data_storage import AbstractDataStorage
from dql.data_storage.schema import DATASET_CORE_COLUMN_NAMES
from dql.data_storage.schema import DatasetRow as DatasetRowSchema
from dql.dataset import (
    DATASET_PREFIX,
    DatasetDependency,
    DatasetRecord,
    DatasetRow,
    DatasetStats,
    create_dataset_uri,
    parse_dataset_uri,
)
from dql.dataset import Status as DatasetStatus
from dql.error import (
    ClientError,
    DatasetNotFoundError,
    DQLError,
    InconsistentSignalType,
    PendingIndexingError,
    QueryScriptCancelError,
    QueryScriptCompileError,
    QueryScriptDatasetNotFound,
    QueryScriptRunError,
)
from dql.listing import Listing
from dql.node import DirType, Node, NodeWithPath
from dql.nodes_thread_pool import NodesThreadPool
from dql.remote.studio import DATASET_ROWS_CHUNK_SIZE, StudioClient
from dql.storage import Status, Storage, StorageURI
from dql.utils import (
    DQLDir,
    dql_paths_join,
    get_remote_config,
    import_object,
    parse_params_string,
    read_config,
)
from dql.vendored import ast
from dql.vendored.ast import Attribute, Call, Expr, Import, Load, Name, alias

from .datasource import DataSource
from .formats import IndexingFormat, apply_processors

logger = logging.getLogger("dql")

DEFAULT_DATASET_DIR = "dataset"
DATASET_FILE_SUFFIX = ".edql"

TTL_INT = 4 * 60 * 60
PYTHON_SCRIPT_WRAPPER_CODE = "__ds__"

INDEX_INTERNAL_ERROR_MESSAGE = "Internal error on indexing"
DATASET_INTERNAL_ERROR_MESSAGE = "Internal error on creating dataset"
# exit code we use if last statement in query script is not instance of DatasetQuery
QUERY_SCRIPT_INVALID_LAST_STATEMENT_EXIT_CODE = 10
MAX_THREADS_DATASET_ROWS_FETCHER = 4
# exit code we use if query script was canceled
QUERY_SCRIPT_CANCELED_EXIT_CODE = 11


def _raise_remote_error(error_message: str) -> NoReturn:
    raise DQLError(f"Error from server: {error_message}")


class DatasetRowsFetcher(NodesThreadPool):
    def __init__(
        self,
        data_storage: AbstractDataStorage,
        studio_client: StudioClient,
        remote_dataset_name: str,
        remote_dataset_version: int,
        shadow_dataset_name: str,
        max_threads: int = MAX_THREADS_DATASET_ROWS_FETCHER,
    ):
        super().__init__(max_threads)
        self.data_storage = data_storage
        self.studio_client = studio_client
        self.remote_dataset_name = remote_dataset_name
        self.remote_dataset_version = remote_dataset_version
        self.shadow_dataset_name = shadow_dataset_name

    def done_task(self, done):
        for task in done:
            task.result()

    def _clean_up(self, data_storage):
        shadow_dataset = data_storage.get_dataset(self.shadow_dataset_name)
        data_storage.remove_shadow_dataset(shadow_dataset)

    def do_task(self, chunk):
        data_storage = self.data_storage.clone()  # data storage is not thread safe
        try:
            rows_response = self.studio_client.dataset_rows_chunk(
                self.remote_dataset_name, self.remote_dataset_version, chunk
            )
            if not rows_response.ok:
                _raise_remote_error(rows_response.message)
        except:
            self._clean_up(data_storage)
            raise

        data_storage.insert_dataset_rows(self.shadow_dataset_name, rows_response.data)

        self.increase_counter(len(rows_response.data))  # type: ignore [arg-type]


@dataclass
class NodeGroup:
    """Class for a group of nodes from the same source"""

    listing: Listing
    sources: List[DataSource]

    # The source path within the bucket
    # (not including the bucket name or s3:// prefix)
    source_path: str = ""
    is_edql: bool = False
    dataset_name: Optional[str] = None
    dataset_version: Optional[int] = None
    instantiated_nodes: Optional[List[NodeWithPath]] = None

    @property
    def is_dataset(self) -> bool:
        return bool(self.dataset_name)

    def iternodes(self, recursive: bool = False):
        for src in self.sources:
            if recursive and src.is_container():
                for nwp in src.find():
                    yield nwp.n
            else:
                yield src.node

    def download(self, recursive: bool = False, pbar=None) -> None:
        """
        Download this node group to cache.
        """
        if self.sources:
            self.listing.client.fetch_nodes(
                self.iternodes(recursive), shared_progress_bar=pbar
            )


def check_output_dataset_file(
    output: str,
    force: bool = False,
    dataset_filename: Optional[str] = None,
    skip_check_edql: bool = False,
) -> str:
    """
    Checks the dataset filename for existence or if it should be force-overwritten.
    """
    dataset_file = (
        dataset_filename if dataset_filename else output + DATASET_FILE_SUFFIX
    )
    if not skip_check_edql:
        if os.path.exists(dataset_file):
            if force:
                os.remove(dataset_file)
            else:
                raise RuntimeError(
                    f"Output dataset file already exists: {dataset_file}"
                )
    return dataset_file


def parse_edql_file(filename: str) -> List[Dict[str, Any]]:
    with open(filename, encoding="utf-8") as f:
        contents = yaml.safe_load(f)

    if not isinstance(contents, list):
        contents = [contents]

    for entry in contents:
        if not isinstance(entry, dict):
            raise ValueError(
                "Failed parsing EDQL file, "
                "each data source entry must be a dictionary"
            )
        if "data-source" not in entry or "files" not in entry:
            raise ValueError(
                "Failed parsing EDQL file, "
                "each data source entry must contain the "
                '"data-source" and "files" keys'
            )

    return contents


def prepare_output_for_cp(
    node_groups: List[NodeGroup],
    output: str,
    force: bool = False,
    edql_only: bool = False,
    no_edql_file: bool = False,
) -> Tuple[bool, Optional[str]]:
    total_node_count = 0
    for node_group in node_groups:
        if not node_group.sources:
            raise FileNotFoundError(
                f"No such file or directory: {node_group.source_path}"
            )
        total_node_count += len(node_group.sources)

    always_copy_dir_contents = False
    copy_to_filename = None

    if edql_only:
        return always_copy_dir_contents, copy_to_filename

    if not os.path.isdir(output):
        if all(n.is_dataset for n in node_groups):
            os.mkdir(output)
        elif total_node_count == 1:
            first_source = node_groups[0].sources[0]
            if first_source.is_container():
                if os.path.exists(output):
                    if force:
                        os.remove(output)
                    else:
                        raise FileExistsError(f"Path already exists: {output}")
                always_copy_dir_contents = True
                os.mkdir(output)
            else:  # Is a File
                if os.path.exists(output):
                    if force:
                        os.remove(output)
                    else:
                        raise FileExistsError(f"Path already exists: {output}")
                copy_to_filename = output
        else:
            raise FileNotFoundError(f"Is not a directory: {output}")

    if copy_to_filename and not no_edql_file:
        raise RuntimeError("File to file cp not supported with .edql files!")

    return always_copy_dir_contents, copy_to_filename


def collect_nodes_for_cp(
    node_groups: Iterable[NodeGroup],
    recursive: bool = False,
) -> Tuple[int, int]:
    total_size: int = 0
    total_files: int = 0

    # Collect all sources to process
    for node_group in node_groups:
        listing: Listing = node_group.listing
        valid_sources: List[DataSource] = []
        for dsrc in node_group.sources:
            if dsrc.is_single_object():
                total_size += dsrc.node.size
                total_files += 1
                valid_sources.append(dsrc)
            else:
                node = dsrc.node
                if not recursive:
                    print(f"{node.full_path} is a directory (not copied).")
                    continue
                add_size, add_files = listing.du(node, count_files=True)
                total_size += add_size
                total_files += add_files
                valid_sources.append(dsrc)

        node_group.sources = valid_sources

    return total_size, total_files


def get_download_bar(bar_format: str, total_size: int):
    return tqdm(
        desc="Downloading files: ",
        unit="B",
        bar_format=bar_format,
        unit_scale=True,
        unit_divisor=1000,
        total=total_size,
    )


def instantiate_node_groups(
    node_groups: Iterable[NodeGroup],
    output: str,
    bar_format: str,
    total_files: int,
    force: bool = False,
    recursive: bool = False,
    virtual_only: bool = False,
    always_copy_dir_contents: bool = False,
    copy_to_filename: Optional[str] = None,
) -> None:
    instantiate_progress_bar = (
        None
        if virtual_only
        else tqdm(
            desc=f"Instantiating {output}: ",
            unit=" f",
            bar_format=bar_format,
            unit_scale=True,
            unit_divisor=1000,
            total=total_files,
        )
    )

    output_dir = output
    if copy_to_filename:
        output_dir = os.path.dirname(output)
        if not output_dir:
            output_dir = "."

    # Instantiate these nodes
    for node_group in node_groups:
        if not node_group.sources:
            continue
        listing: Listing = node_group.listing
        source_path: str = node_group.source_path

        copy_dir_contents = always_copy_dir_contents or source_path.endswith("/")
        instantiated_nodes = listing.collect_nodes_to_instantiate(
            node_group.sources,
            copy_to_filename,
            recursive,
            copy_dir_contents,
            source_path,
            node_group.is_edql,
            node_group.is_dataset,
        )
        if not virtual_only:
            listing.instantiate_nodes(
                instantiated_nodes,
                output_dir,
                total_files,
                force=force,
                shared_progress_bar=instantiate_progress_bar,
            )
        node_group.instantiated_nodes = instantiated_nodes
    if instantiate_progress_bar:
        instantiate_progress_bar.close()


def compute_metafile_data(node_groups) -> List[Dict[str, Any]]:
    metafile_data = []
    for node_group in node_groups:
        if not node_group.sources:
            continue
        listing: Listing = node_group.listing
        source_path: str = node_group.source_path
        metafile_group = {
            "data-source": (
                listing.storage.to_dict(source_path)
                if not node_group.is_dataset
                else {"uri": listing.data_storage.uri}
            ),
            "files": [],
        }
        for node in node_group.instantiated_nodes:
            if not node.n.is_dir:
                metafile_group["files"].append(node.get_metafile_data())
        if metafile_group["files"]:
            metafile_data.append(metafile_group)

    return metafile_data


def find_column_to_str(  # noqa: PLR0911
    row: Tuple[Any, ...], field_lookup: Dict[str, int], src: DataSource, column: str
) -> str:
    if column == "du":
        return str(
            src.listing.du(
                {
                    f: row[field_lookup[f]]
                    for f in ["dir_type", "size", "parent", "name"]
                }
            )[0]
        )
    if column == "name":
        return row[field_lookup["name"]] or ""
    if column == "owner":
        return row[field_lookup["owner_name"]] or ""
    if column == "path":
        is_dir = row[field_lookup["dir_type"]] == DirType.DIR
        parent = row[field_lookup["parent"]]
        name = row[field_lookup["name"]]
        path = f"{parent}/{name}" if parent else name
        if is_dir and path:
            full_path = path + "/"
        else:
            full_path = path
        return src.get_node_full_path_from_path(full_path)
    if column == "size":
        return str(row[field_lookup["size"]])
    if column == "type":
        dt = row[field_lookup["dir_type"]]
        if dt == DirType.DIR:
            return "d"
        elif dt == DirType.FILE:
            return "f"
        elif dt == DirType.TAR_ARCHIVE:
            return "t"
        # Unknown - this only happens if a type was added elsewhere but not here
        return "u"
    return ""


class Catalog:
    def __init__(
        self,
        data_storage: AbstractDataStorage,
        cache_dir=None,
        tmp_dir=None,
        client_config: Optional[Dict[str, Any]] = None,
    ):
        dql_dir = DQLDir(cache=cache_dir, tmp=tmp_dir)
        dql_dir.init()
        self.data_storage = data_storage
        self.cache = DQLCache(dql_dir.cache, dql_dir.tmp)
        self.client_config = client_config if client_config is not None else {}
        self._init_params = {
            "cache_dir": cache_dir,
            "tmp_dir": tmp_dir,
        }

    def get_init_params(self) -> Dict[str, Any]:
        return {
            **self._init_params,
            "client_config": self.client_config,
        }

    def compile_query_script(self, script: str) -> str:
        code_ast = ast.parse(script)
        if code_ast.body:
            last_expr = code_ast.body[-1]
            if isinstance(last_expr, Expr):
                new_expressions = [
                    Import(names=[alias(name="dql.query.dataset", asname=None)]),
                    Expr(
                        value=Call(
                            func=Attribute(
                                value=Attribute(
                                    value=Attribute(
                                        value=Name(id="dql", ctx=Load()),
                                        attr="query",
                                        ctx=Load(),
                                    ),
                                    attr="dataset",
                                    ctx=Load(),
                                ),
                                attr="return_ds",
                                ctx=Load(),
                            ),
                            args=[last_expr],
                            keywords=[],
                        )
                    ),
                ]
                code_ast.body[-1:] = new_expressions
            else:
                raise Exception("Last line in a script was not an expression")

        return ast.unparse(code_ast)

    def add_storage(self, source: str) -> None:
        path = LocalFileSystem._strip_protocol(source)
        if not os.path.isdir(path):
            raise RuntimeError(f"{path} is not a directory")
        uri = StorageURI(Path(path).resolve().as_uri())
        print(f"Registering storage {uri}")
        self.data_storage.create_storage_if_not_registered(uri)

    def parse_url(self, uri: str, **config: Any) -> Tuple[Client, str]:
        config = config or self.client_config
        return Client.parse_url(uri, self.data_storage, self.cache, **config)

    def get_client(self, uri: StorageURI, **config: Any) -> Client:
        """
        Return the client corresponding to the given source `uri`.
        """
        config = config or self.client_config
        cls = Client.get_implementation(uri)
        return cls.from_source(uri, self.data_storage, self.cache, **config)

    def enlist_source(
        self,
        source: str,
        ttl: int,
        force_update=False,
        skip_indexing=False,
        client_config=None,
        index_processors: Optional[List[IndexingFormat]] = None,
    ) -> Tuple[Listing, str]:
        if force_update and skip_indexing:
            raise ValueError(
                "Both force_update and skip_indexing flags"
                " cannot be True at the same time"
            )

        client_config = client_config or self.client_config
        client, path = self.parse_url(source, **client_config)
        prefix = posixpath.dirname(path)
        source_data_storage = self.data_storage.clone(client.uri)

        partial_id: Optional[int]
        if skip_indexing:
            source_data_storage.create_storage_if_not_registered(client.uri)
            storage = source_data_storage.get_storage(client.uri)
            source_data_storage.init_id_generator(client.uri)
            partial_id = source_data_storage.get_next_partial_id(client.uri)
            source_data_storage = self.data_storage.clone(
                uri=client.uri, partial_id=partial_id
            )
            source_data_storage.init_db(client.uri, partial_id)
            return (
                Listing(storage, source_data_storage, client),
                path,
            )

        (
            storage,
            need_index,
            in_progress,
            partial_id,
        ) = source_data_storage.register_storage_for_indexing(
            client.uri, force_update, prefix
        )
        if in_progress:
            raise PendingIndexingError(f"Pending indexing operation: uri={storage.uri}")

        if not need_index:
            assert partial_id is not None
            source_data_storage = self.data_storage.clone(
                uri=client.uri, partial_id=partial_id
            )
            lst = Listing(storage, source_data_storage, client)
            logger.debug(  # type: ignore[unreachable]
                f"Using cached listing {storage.uri}."
                + f" Valid till: {storage.expires_to_local}"
            )
            # Listing has to have correct version of data storage
            # initialized with correct Storage
            return lst, path

        source_data_storage.init_id_generator(client.uri)
        partial_id = source_data_storage.get_next_partial_id(client.uri)
        source_data_storage.init_db(client.uri, partial_id)
        source_data_storage = self.data_storage.clone(
            uri=client.uri, partial_id=partial_id
        )
        lst = Listing(storage, source_data_storage, client)
        try:
            lst.fetch(prefix)

            # Apply index processing before marking storage as indexed.
            if index_processors:
                asyncio.run(apply_processors(lst, path, index_processors))

            source_data_storage.mark_storage_indexed(
                storage.uri,
                Status.PARTIAL if prefix else Status.COMPLETE,
                ttl,
                prefix=prefix,
                partial_id=partial_id,
            )
        except InconsistentSignalType as e:
            # handle all custom errors here which messages we want to show
            # directly to the user (user mistake generated error)
            source_data_storage.mark_storage_indexed(
                storage.uri,
                Status.FAILED,
                ttl,
                prefix=prefix,
                error_message=str(e),
                error_stack=traceback.format_exc(),
            )
            raise
        except ClientError as e:
            # for handling cloud errors
            error_message = INDEX_INTERNAL_ERROR_MESSAGE
            if e.error_code in ["InvalidAccessKeyId", "SignatureDoesNotMatch"]:
                error_message = "Invalid cloud credentials"

            source_data_storage.mark_storage_indexed(
                storage.uri,
                Status.FAILED,
                ttl,
                prefix=prefix,
                error_message=error_message,
                error_stack=traceback.format_exc(),
            )
            raise
        except:
            source_data_storage.mark_storage_indexed(
                storage.uri,
                Status.FAILED,
                ttl,
                prefix=prefix,
                error_message=INDEX_INTERNAL_ERROR_MESSAGE,
                error_stack=traceback.format_exc(),
            )
            raise

        lst.storage = storage

        return lst, path

    def enlist_sources(
        self,
        sources: List[str],
        ttl: int,
        update: bool,
        skip_indexing=False,
        client_config=None,
        index_processors: Optional[List[IndexingFormat]] = None,
        only_index=False,
    ) -> Optional[List["DataSource"]]:
        enlisted_sources = []
        for src in sources:  # Opt: parallel
            listing, file_path = self.enlist_source(
                src,
                ttl,
                update,
                skip_indexing=skip_indexing,
                client_config=client_config or self.client_config,
                index_processors=index_processors,
            )
            enlisted_sources.append((listing, file_path))

        if only_index:
            # sometimes we don't really need listing result (e.g on indexing process)
            # so this is to improve performance
            return None

        dsrc_all = []
        for listing, file_path in enlisted_sources:
            nodes = listing.expand_path(file_path)
            dir_only = file_path.endswith("/")
            for node in nodes:
                dsrc_all.append(DataSource(listing, node, dir_only))

        return dsrc_all

    def enlist_sources_grouped(
        self,
        sources: List[str],
        ttl: int,
        update: bool,
        no_glob: bool = False,
        client_config=None,
    ) -> List[NodeGroup]:
        def _ds_row_to_node(dr: DatasetRow) -> Node:
            d = asdict(dr)  # type: ignore [arg-type]
            del d["source"]
            del d["custom"]
            return Node(**d)

        enlisted_sources: List[Tuple[bool, bool, Any]] = []
        client_config = client_config or self.client_config
        for src in sources:  # Opt: parallel
            if src.endswith(DATASET_FILE_SUFFIX) and os.path.isfile(src):
                # TODO: Also allow using EDQL files from cloud locations?
                edql_data = parse_edql_file(src)
                indexed_sources = []
                for ds in edql_data:
                    listing, source_path = self.enlist_source(
                        ds["data-source"]["uri"],
                        ttl,
                        update,
                        client_config=client_config,
                    )
                    paths = dql_paths_join(
                        source_path, (f["name"] for f in ds["files"])
                    )
                    indexed_sources.append((listing, source_path, paths))
                enlisted_sources.append((True, False, indexed_sources))
            elif src.startswith("ds://"):
                ds_name, ds_version = parse_dataset_uri(src)
                dataset_sources = self.data_storage.get_dataset_sources(
                    ds_name, ds_version
                )
                indexed_sources = []
                for source in dataset_sources:
                    client = self.get_client(source, **client_config)
                    uri = client.uri
                    st = self.data_storage.clone(uri, None)
                    listing = Listing(
                        None,  # type: ignore [arg-type]
                        st,
                        client,
                    )
                    rows = st.get_dataset_rows(
                        ds_name, version=ds_version, limit=None, source=source
                    )
                    indexed_sources.append(
                        (
                            listing,
                            source,
                            rows,
                            ds_name,
                            ds_version,
                        )  # type: ignore [arg-type]
                    )

                enlisted_sources.append((False, True, indexed_sources))
            else:
                listing, source_path = self.enlist_source(
                    src, ttl, update, client_config=client_config
                )
                enlisted_sources.append((False, False, (listing, source_path)))

        node_groups = []
        dsrc: List[DataSource] = []
        for is_dql, is_dataset, payload in enlisted_sources:  # Opt: parallel
            if is_dataset:
                for (
                    listing,
                    source_path,
                    dataset_rows,
                    dataset_name,
                    dataset_version,
                ) in payload:
                    nodes = [_ds_row_to_node(row) for row in dataset_rows]
                    dsrc = [DataSource(listing, node) for node in nodes]
                    node_groups.append(
                        NodeGroup(
                            listing,
                            dsrc,
                            source_path,
                            dataset_name=dataset_name,
                            dataset_version=dataset_version,
                        )
                    )
            elif is_dql:
                for listing, source_path, paths in payload:
                    dsrc = [DataSource(listing, listing.resolve_path(p)) for p in paths]
                    node_groups.append(
                        NodeGroup(listing, dsrc, source_path, is_edql=True)
                    )
            else:
                listing, source_path = payload
                as_container = source_path.endswith("/")
                if no_glob:
                    dsrc = [
                        DataSource(
                            listing, listing.resolve_path(source_path), as_container
                        )
                    ]
                else:
                    dsrc = [
                        DataSource(listing, n, as_container)
                        for n in listing.expand_path(source_path)
                    ]
                node_groups.append(NodeGroup(listing, dsrc, source_path))

        return node_groups

    def unlist_source(self, uri: StorageURI) -> None:
        self.data_storage.clone(uri=uri).mark_storage_not_indexed(uri)

    def _get_nodes(self, sources: Iterable[str], client_config) -> list:
        "Gets list of nodes based on sources"
        nodes = []
        for source in sources:
            client, _ = self.parse_url(source, **client_config)
            uri = client.uri
            partial_id = self.data_storage.get_valid_partial_id(uri, "")
            nodes.append(self.data_storage.nodes_table(uri, partial_id))

        return nodes

    def create_shadow_dataset(
        self,
        name: str,
        sources: List[str],
        query_script: str = "",
        client_config=None,
        recursive=False,
        populate=True,
    ) -> DatasetRecord:
        """
        Creates shadow dataset in DB if it doesn't exist and updates it with
        entries from sources.
        Example of sources:
            s3://bucket_name/dir1/dir2/*
            s3://bucket_name/*
            s3://bucket_name/image_*
        """
        error_message = ""
        error_stack = ""
        client_config = client_config or self.client_config

        # get custom columns based on sources
        custom_columns = DatasetRowSchema.calculate_custom_columns(
            self._get_nodes(sources, client_config)
        )
        dataset = self.data_storage.create_shadow_dataset(
            name,
            sources=sources,
            query_script=query_script,
            create_rows=populate,
            custom_columns=custom_columns,
        )
        assert dataset
        if not populate:
            # returning empty dataset without dataset rows table and data inside
            return dataset

        final_status = DatasetStatus.FAILED
        try:
            for source in sources:
                client, path = self.parse_url(source, **client_config)
                uri = client.uri
                partial_id = self.data_storage.get_valid_partial_id(uri, path)
                st = self.data_storage.clone(uri, partial_id)
                st.insert_into_shadow_dataset(name, uri, path, recursive=recursive)
                storage = self.get_storage(uri)
                st.add_storage_dependency(dataset.name, uri, storage.timestamp_str)
            final_status = DatasetStatus.COMPLETE
        except Exception:
            error_message = DATASET_INTERNAL_ERROR_MESSAGE
            error_stack = traceback.format_exc()
            raise
        finally:
            self.data_storage.update_dataset_status(
                dataset,
                final_status,
                error_message=error_message,
                error_stack=error_stack,
            )

        return dataset

    def register_shadow_dataset(
        self,
        shadow_name: str,
        registered_name: Optional[str] = None,
        version: Optional[int] = None,
        description: Optional[str] = None,
        labels: Optional[List[str]] = None,
        validate_version: Optional[bool] = True,
    ) -> DatasetRecord:
        """
        Method for registering shadow dataset as a new dataset with version 1, or
        as a new version of existing registered dataset
        """
        shadow_dataset = self.data_storage.get_dataset(shadow_name)
        if not shadow_dataset.shadow:
            raise ValueError(f"Dataset {shadow_name} must be shadow")

        try:
            registered_dataset = (
                self.data_storage.get_dataset(registered_name)
                if registered_name
                else None
            )
        except DatasetNotFoundError:
            registered_dataset = None

        if registered_dataset:
            # if registered dataset already exists, we are creating new version
            # of it out of shadow dataset
            version = version or registered_dataset.next_version
            if validate_version and not registered_dataset.is_valid_next_version(
                version
            ):
                raise ValueError(
                    f"Version {version} must be higher than the current latest one"
                )

            dataset = self.data_storage.create_dataset_version(
                registered_dataset.name,
                version,
                sources=shadow_dataset.sources,
                query_script=shadow_dataset.query_script,
                create_rows_table=False,
                custom_column_types=shadow_dataset.custom_column_types_serialized,
            )
            # to avoid re-creating rows table, we are just taking shadow one and
            # renaming it for a new version of registered one
            self.data_storage.rename_dataset_table(
                shadow_dataset.name,
                registered_dataset.name,
                old_version=None,
                new_version=version,
            )
            self.data_storage.update_dataset_dependency_source(
                shadow_dataset,
                new_source_dataset=dataset,
                new_source_dataset_version=version,
            )
            # finally, we are removing shadow dataset from datasets table
            self.data_storage.remove_shadow_dataset(shadow_dataset, drop_rows=False)
            return dataset

        version = version or 1
        # if registered dataset doesn't exist we are modifying shadow dataset
        # to become registered one
        update_data = {
            "shadow": False,
            "description": description,
            "labels": labels,
            "sources": "",
            "query_script": "",
        }

        if registered_name:
            update_data["name"] = registered_name

        self.data_storage.update_dataset(shadow_name, **update_data)
        dataset = self.data_storage.create_dataset_version(
            registered_name or shadow_name,
            version,
            sources=shadow_dataset.sources,
            query_script=shadow_dataset.query_script,
            create_rows_table=False,
            custom_column_types=shadow_dataset.custom_column_types_serialized,
        )
        self.data_storage.rename_dataset_table(
            registered_name or shadow_name,
            registered_name or shadow_name,
            old_version=None,
            new_version=version,
        )
        self.data_storage.update_dataset_dependency_source(
            dataset, new_source_dataset_version=version
        )
        return dataset

    def get_dataset(self, name: str) -> DatasetRecord:
        return self.data_storage.get_dataset(name)

    def get_remote_dataset(self, name: str, *, remote_config=None) -> DatasetRecord:
        remote_config = remote_config or get_remote_config(
            read_config(DQLDir.find().root), remote=""
        )
        studio_client = StudioClient(
            remote_config["url"], remote_config["username"], remote_config["token"]
        )

        info_response = studio_client.dataset_info(name)
        if not info_response.ok:
            _raise_remote_error(info_response.message)

        dataset_info = info_response.data
        assert isinstance(dataset_info, dict)
        return DatasetRecord.from_dict(dataset_info)

    def get_dataset_dependencies(
        self, name: str, version: Optional[int] = None, indirect=False
    ) -> List[Optional[DatasetDependency]]:
        dataset = self.get_dataset(name)
        if dataset.registered and not version:
            raise ValueError(f"Missing version for registered dataset {name}")

        direct_dependencies = self.data_storage.get_direct_dataset_dependencies(
            dataset, version
        )

        if not indirect:
            return direct_dependencies

        for d in direct_dependencies:
            if not d:
                # dependency has been removed
                continue
            if d.is_dataset:
                # only datasets can have dependencies
                d.dependencies = self.get_dataset_dependencies(
                    d.name, int(d.version) if d.version else None, indirect=indirect
                )

        return direct_dependencies

    def ls_datasets(self, shadow_only=None) -> Iterator[DatasetRecord]:
        yield from self.data_storage.list_datasets(shadow_only=shadow_only)

    def ls_dataset_rows(
        self, name: str, offset=None, limit=None, version=None, custom_columns=False
    ) -> Iterator[DatasetRow]:
        dataset = self.data_storage.get_dataset(name)
        if not dataset.shadow and not version:
            raise ValueError(
                f"Missing dataset version from input for registered dataset {name}"
            )

        yield from self.data_storage.get_dataset_rows(
            name,
            offset=offset,
            limit=limit,
            version=version,
            custom_columns=custom_columns,
        )

    def signed_url(self, source: str, path: str, client_config=None) -> str:
        client_config = client_config or self.client_config
        client, _ = self.parse_url(source, **client_config)
        return client.url(path)

    def dataset_row(
        self,
        name: str,
        row_id: int,
        dataset_version: Optional[int] = None,
    ) -> Optional[DatasetRow]:
        return self.data_storage.get_dataset_row(
            name, row_id, dataset_version=dataset_version
        )

    def dataset_stats(self, name: str, version: Optional[int] = None) -> DatasetStats:
        dataset = self.data_storage.get_dataset(name)
        if dataset.registered and not version:
            raise ValueError(f"Missing dataset version for registered dataset {name}")
        return DatasetStats(
            num_objects=self.data_storage.dataset_rows_count(name, version),
            size=self.data_storage.dataset_rows_size(name, version),
        )

    def remove_dataset(
        self,
        name: str,
        version: Optional[int] = None,
        force: Optional[bool] = False,
    ):
        dataset = self.data_storage.get_dataset(name)
        if dataset.registered and not version and not force:
            raise ValueError(
                f"Missing dataset version from input for registered dataset {name}"
            )
        if version and not dataset.has_version(version):
            raise RuntimeError(f"Dataset {name} doesn't have version {version}")

        if dataset.registered and version:
            self.data_storage.remove_dataset_version(dataset, version)

        elif dataset.registered and force:
            for version in dataset.versions.copy():  # type: ignore [assignment, union-attr]
                self.data_storage.remove_dataset_version(
                    dataset,
                    version.version,  # type: ignore [union-attr]
                )
        else:
            self.data_storage.remove_shadow_dataset(dataset)

    def edit_dataset(
        self,
        name: str,
        new_name: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ):
        update_data = {}
        if new_name:
            update_data["name"] = new_name
        if description is not None:
            update_data["description"] = description
        if labels is not None:
            update_data["labels"] = labels  # type: ignore[assignment]

        self.data_storage.update_dataset(name, **update_data)

    def merge_datasets(
        self,
        src_name: str,
        dst_name: str,
        src_version: Optional[int] = None,
        dst_version: Optional[int] = None,
    ) -> DatasetRecord:
        """
        Merges records from source to destination dataset.
        If destination dataset is shadow, it will copy all the records from source
        dataset to shadow one
        If destination dataset is registered, it will create a new version
        of dataset with records merged from old version and the source
        """

        src = self.data_storage.get_dataset(src_name)
        dst = self.data_storage.get_dataset(dst_name)

        # validation
        if src.shadow and src_version:
            raise ValueError(
                f"Source dataset {src_name} is shadow, cannot use it with versions"
            )
        if not src.shadow and not src_version:
            raise ValueError(f"Source dataset {src_name} is registered, need a version")
        if dst.shadow and dst_version:
            raise ValueError(
                f"Dataset {dst_name} is shadow, cannot use it with versions"
            )

        if dst_version and not dst.is_valid_next_version(dst_version):
            raise ValueError(
                f"Version {dst_version} must be higher than the current latest one"
            )

        # merge custom column types
        custom_column_types = {
            **src.custom_column_types_serialized,
            **dst.custom_column_types_serialized,
        }

        src_dep = self.get_dataset_dependencies(src_name, src_version)
        dst_dep = self.get_dataset_dependencies(dst_name, dst.latest_version)

        if dst.shadow:
            self.data_storage.merge_dataset_rows(
                src,
                dst,
                src_version,
                dst_version=None,
            )
            self.data_storage.update_dataset(
                dst.name, custom_column_types=custom_column_types
            )
            for dep in src_dep:
                if dep and dep not in dst_dep:
                    self.data_storage.add_dependency(dep, dst.name)
        else:
            dst_version = dst_version or dst.next_version
            self.data_storage.create_dataset_version(
                dst_name, dst_version, custom_column_types=custom_column_types
            )
            self.data_storage.merge_dataset_rows(
                src,
                dst,
                src_version,
                dst_version,
            )
            for dep in set(src_dep + dst_dep):
                if dep:
                    self.data_storage.add_dependency(dep, dst.name, dst_version)

        return dst

    def copy_shadow_dataset(self, src_name: str, dst_name: str) -> DatasetRecord:
        """
        Copy records from source shadow dataset to destination shadow dataset.
        """
        src = self.data_storage.get_dataset(src_name)
        dst = self.data_storage.get_dataset(dst_name)

        # validation
        if not src.shadow:
            raise ValueError(f"Source dataset {src_name} is not shadow")
        if not dst.shadow:
            raise ValueError(f"Dataset {dst_name} is not shadow")

        self.data_storage.copy_shadow_dataset_rows(src, dst)

        return dst

    def open_object(self, row: DatasetRow, use_cache: bool = True, **config: Any):
        config = config or self.client_config
        client = self.get_client(row.source, **config)
        return client.open_object(row.as_uid(), use_cache=use_cache)

    def ls(
        self,
        sources: List[str],
        fields: Iterable[str],
        ttl=TTL_INT,
        update=False,
        skip_indexing=False,
        *,
        client_config=None,
    ) -> Iterator[Tuple[DataSource, Iterable[tuple]]]:
        data_sources = self.enlist_sources(
            sources,
            ttl,
            update,
            skip_indexing=skip_indexing,
            client_config=client_config or self.client_config,
        )

        for source in data_sources:  # type: ignore [union-attr]
            yield source, source.ls(fields)

    def ls_storage_uris(self) -> Iterator[str]:
        yield from self.data_storage.get_all_storage_uris()

    def get_storage(self, uri: StorageURI) -> Storage:
        return self.data_storage.get_storage(uri)

    def ls_storages(self) -> List[Storage]:
        return self.data_storage.list_storages()

    def pull_dataset(  # noqa: PLR0911, C901
        self,
        dataset_uri: str,
        output: Optional[str] = None,
        no_cp: bool = False,
        force: bool = False,
        edql: bool = False,
        edql_file: Optional[str] = None,
        *,
        client_config=None,
        remote_config=None,
    ) -> None:
        # TODO add progress bar https://github.com/iterative/dql/issues/750
        # TODO copy correct remote dates https://github.com/iterative/dql/issues/new
        # TODO compare dataset stats on remote vs local pull to assert it's ok
        def _instantiate_dataset():
            if no_cp:
                return
            self.cp(
                [dataset_uri],
                output,
                force=force,
                no_edql_file=not edql,
                edql_file=edql_file,
                client_config=client_config,
            )
            print(f"Dataset {dataset_uri} instantiated locally to {output}")

        if not output and not no_cp:
            raise ValueError("Please provide output directory for instantiation")

        client_config = client_config or self.client_config
        remote_config = remote_config or get_remote_config(
            read_config(DQLDir.find().root), remote=""
        )

        studio_client = StudioClient(
            remote_config["url"], remote_config["username"], remote_config["token"]
        )

        try:
            remote_dataset_name, version = parse_dataset_uri(dataset_uri)
        except Exception as e:
            raise DQLError("Error when parsing dataset uri") from e

        dataset = None
        try:
            dataset = self.get_dataset(remote_dataset_name)
            if dataset.shadow:
                raise DQLError(
                    "Shadow local dataset already exists with name "
                    f"{remote_dataset_name}"
                )
        except DatasetNotFoundError:
            pass

        remote_dataset = self.get_remote_dataset(remote_dataset_name)
        # if version is not specified in uri, take the latest one
        if not version:
            version = remote_dataset.latest_version
            print(f"Version not specified, pulling the latest one (v{version})")
            # updating dataset uri with latest version
            dataset_uri = create_dataset_uri(remote_dataset_name, version)

        assert version
        if dataset and dataset.has_version(version):
            print(f"Local copy of dataset {dataset_uri} already present")
            _instantiate_dataset()
            return

        try:
            remote_dataset_version = remote_dataset.get_version(version)
        except (ValueError, StopIteration) as exc:
            raise DQLError(
                f"Dataset {remote_dataset_name} doesn't have version {version}"
                " on server"
            ) from exc

        stats_response = studio_client.dataset_stats(remote_dataset_name, version)
        if not stats_response.ok:
            _raise_remote_error(stats_response.message)
        dataset_stats = stats_response.data

        dataset_save_progress_bar = tqdm(
            desc=f"Saving dataset {dataset_uri} locally: ",
            unit=" rows",
            unit_scale=True,
            unit_divisor=1000,
            total=dataset_stats.num_objects,  # type: ignore [union-attr]
        )

        # temp shadow dataset name not to conflict to possibly already existing
        # registered one with the same name - if some other version of it
        # has been pulled from remote before
        shadow_dataset_name = f"shadow_ds_{uuid4().hex}"

        custom_column_types = DatasetRecord.parse_custom_column_types(
            remote_dataset_version.custom_column_types,
        )
        custom_columns = [
            sa.Column(c_name, c_type)
            for c_name, c_type in custom_column_types.items()
            if c_name not in DATASET_CORE_COLUMN_NAMES
        ]

        shadow_dataset = self.data_storage.create_shadow_dataset(
            shadow_dataset_name,
            sources=remote_dataset_version.sources.split(),
            query_script=remote_dataset_version.query_script,
            create_rows=True,
            custom_columns=custom_columns,
        )

        rows_fetcher = DatasetRowsFetcher(
            self.data_storage.clone(),
            studio_client,
            remote_dataset_name,
            version,
            shadow_dataset.name,
        )
        rows_fetcher.run(
            range(
                0,
                dataset_stats.num_objects,  # type: ignore [union-attr]
                DATASET_ROWS_CHUNK_SIZE,
            ),
            dataset_save_progress_bar,
        )

        shadow_dataset = self.data_storage.update_dataset_status(
            shadow_dataset,
            DatasetStatus.COMPLETE,
            error_message=remote_dataset.error_message,
            error_stack=remote_dataset.error_stack,
            script_output=remote_dataset.error_stack,
        )

        self.register_shadow_dataset(
            shadow_dataset.name,
            registered_name=remote_dataset_name,
            version=version,
            description=remote_dataset.description,
            labels=remote_dataset.labels,
            validate_version=False,
        )
        dataset_save_progress_bar.close()
        print(f"Dataset {dataset_uri} saved locally")

        _instantiate_dataset()

    def clone(
        self,
        sources: List[str],
        output: str,
        force: bool = False,
        update: bool = False,
        recursive: bool = False,
        no_glob: bool = False,
        no_cp: bool = False,
        edql: bool = False,
        edql_file: Optional[str] = None,
        ttl: int = TTL_INT,
        *,
        client_config=None,
    ) -> None:
        """
        This command takes cloud path(s) and duplicates files and folders in
        them into the dataset folder.
        It also adds those files to a shadow dataset in database, which is
        created if doesn't exist yet
        Optionally, it creates a .edql file
        """
        if not no_cp or edql:
            self.cp(
                sources,
                output,
                force=force,
                update=update,
                recursive=recursive,
                no_glob=no_glob,
                edql_only=no_cp,
                no_edql_file=not edql,
                edql_file=edql_file,
                ttl=ttl,
                client_config=client_config,
            )
        else:
            # since we don't call cp command, which does listing implicitly,
            # it needs to be done here
            self.enlist_sources(
                sources,
                ttl,
                update,
                client_config=client_config or self.client_config,
            )

        self.create_shadow_dataset(
            output, sources, client_config=client_config, recursive=recursive
        )

    def apply_udf(
        self,
        udf_location: str,
        source: str,
        target_name: str,
        parallel: Optional[int] = None,
        params: Optional[str] = None,
    ):
        from dql.query import DatasetQuery

        if source.startswith(DATASET_PREFIX):
            ds = DatasetQuery(name=source[len(DATASET_PREFIX) :], catalog=self)
        else:
            ds = DatasetQuery(path=source, catalog=self)
        udf = import_object(udf_location)
        if params:
            args, kwargs = parse_params_string(params)
            udf = udf(*args, **kwargs)
        ds.add_signals(udf, parallel=parallel).save(target_name)

    def query_run(
        self,
        query_script: str,
        envs: Optional[Mapping[str, str]] = None,
        python_executable: Optional[str] = None,
    ) -> Tuple[DatasetRecord, str]:
        """
        Method to run custom user Python script to run a query and, as result,
        creates new shadow dataset from the results of a query.
        Returns tuple of result dataset and script output.

        Constraints on query script:
            1. dql.query.DatasetQuery should be used in order to create query
            for a dataset
            2. There should not be any .save() call on DatasetQuery since the idea
            is to create only one shadow dataset as the outcome of the script
            3. Last statement must be an instance of DatasetQuery - this is needed
            so that we can wrap that instance and call .save() on it

        Example of query script:
            from dql.query import DatasetQuery, C
            DatasetQuery('s3://ldb-public/remote/datasets/mnist-tiny/').filter(
                C.size > 1000
            )
        """
        if envs is None:
            envs = os.environ

        try:
            query_script_compiled = self.compile_query_script(query_script)
        except Exception as e:
            raise QueryScriptCompileError(  # noqa: B904
                f"Query script failed to compile, reason: {e}"
            )

        if not python_executable:
            python_executable = sys.executable

        result = subprocess.run(  # noqa: PLW1510
            [python_executable, "-c", query_script_compiled],  # noqa: S603
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # merging stderr to stdout
            env=envs,
        )

        script_output = ""  # stdout + stderr from user script itself

        # finding returning dataset name from script
        returned_dataset_name = None
        if result.stdout:
            for line in result.stdout.decode("utf-8").splitlines():
                if len(line.split(PYTHON_SCRIPT_WRAPPER_CODE)) == 3:
                    returned_dataset_name = line.split(PYTHON_SCRIPT_WRAPPER_CODE)[1]
                else:
                    # collecting script output as well to save it to the database
                    # later on for debugging
                    script_output += line + "\n"

        if result.returncode:
            if result.returncode == QUERY_SCRIPT_CANCELED_EXIT_CODE:
                raise QueryScriptCancelError(
                    "Query script was canceled by user",
                    return_code=result.returncode,
                    output=script_output,
                )
            if result.returncode == QUERY_SCRIPT_INVALID_LAST_STATEMENT_EXIT_CODE:
                raise QueryScriptRunError(
                    "Last line in a script was not an instance of DatasetQuery",
                    return_code=result.returncode,
                    output=script_output,
                )
            else:
                raise QueryScriptRunError(
                    f"Query script exited with error code {result.returncode}",
                    return_code=result.returncode,
                    output=script_output,
                )

        # finding returning dataset
        returned_dataset = None
        if returned_dataset_name:
            try:
                returned_dataset = self.get_dataset(returned_dataset_name)
            except DatasetNotFoundError:
                pass

        if not returned_dataset:
            raise QueryScriptDatasetNotFound(
                "No dataset found after running Query script",
                output=script_output,
            )

        return returned_dataset, script_output

    def query(
        self,
        query_script: str,
        envs: Optional[Mapping[str, str]] = None,
        dataset: Optional[DatasetRecord] = None,
        python_executable: Optional[str] = None,
    ) -> DatasetRecord:
        """
        Method to run custom user Python script to run a query and, as result,
        creates new shadow dataset from the results of a query.
        If dataset is provided, it will merge shadow dataset with it
        and remove created one.
        If dataset is not provided, it returns created shadow dataset.
        """
        if dataset:
            # save query script regardless of query run outcome
            self.data_storage.update_dataset(dataset.name, query_script=query_script)

        def fail(message: str, output: str = ""):
            if dataset:
                self.data_storage.update_dataset_status(
                    dataset,
                    DatasetStatus.FAILED,
                    error_message=message,
                    error_stack=traceback.format_exc(),
                    script_output=output,
                )

        try:
            returned_dataset, script_output = self.query_run(
                query_script,
                envs=envs,
                python_executable=python_executable,
            )
        except QueryScriptCancelError as e:
            if dataset:
                # we use update_dataset instead of update_dataset_status
                # to avoid erasing error_message with empty string
                self.data_storage.update_dataset(
                    dataset.name,
                    status=DatasetStatus.FAILED,
                    script_output=e.output,
                )
            raise e
        except QueryScriptCompileError as e:
            fail(str(e))
            raise e
        except QueryScriptDatasetNotFound as e:
            fail(DATASET_INTERNAL_ERROR_MESSAGE, output=e.output)
            raise e
        except QueryScriptRunError as e:
            fail(str(e), output=e.output)
            raise e

        if dataset:
            dataset = self.merge_datasets(returned_dataset.name, dataset.name)
            self.remove_dataset(returned_dataset.name)
            self.data_storage.update_dataset_status(
                dataset, DatasetStatus.COMPLETE, script_output=script_output
            )
            return dataset
        else:
            self.data_storage.update_dataset(
                returned_dataset.name,
                sources="",
                query_script=query_script,
                script_output=script_output,
            )
            return self.get_dataset(returned_dataset.name)

    def cp(
        self,
        sources: List[str],
        output: str,
        force: bool = False,
        update: bool = False,
        recursive: bool = False,
        edql_file: Optional[str] = None,
        edql_only: bool = False,
        no_edql_file: bool = False,
        no_glob: bool = False,
        ttl: int = TTL_INT,
        *,
        client_config=None,
    ) -> List[Dict[str, Any]]:
        """
        This function copies files from cloud sources to local destination directory
        If cloud source is not indexed, or has expired index, it runs indexing
        It also creates .edql file by default, if not specified differently
        """
        client_config = client_config or self.client_config
        node_groups = self.enlist_sources_grouped(
            sources,
            ttl,
            update,
            no_glob,
            client_config=client_config,
        )

        always_copy_dir_contents, copy_to_filename = prepare_output_for_cp(
            node_groups, output, force, edql_only, no_edql_file
        )
        dataset_file = check_output_dataset_file(output, force, edql_file, no_edql_file)

        total_size, total_files = collect_nodes_for_cp(node_groups, recursive)

        if total_files == 0:
            # Nothing selected to cp
            return []

        desc_max_len = max(len(output) + 16, 19)
        bar_format = (
            "{desc:<"
            f"{desc_max_len}"
            "}{percentage:3.0f}%|{bar}| {n_fmt:>5}/{total_fmt:<5} "
            "[{elapsed}<{remaining}, {rate_fmt:>8}]"
        )

        if not edql_only:
            with get_download_bar(bar_format, total_size) as pbar:
                for node_group in node_groups:
                    node_group.download(recursive=recursive, pbar=pbar)

        instantiate_node_groups(
            node_groups,
            output,
            bar_format,
            total_files,
            force,
            recursive,
            edql_only,
            always_copy_dir_contents,
            copy_to_filename,
        )
        if no_edql_file:
            return []

        metafile_data = compute_metafile_data(node_groups)
        if metafile_data:
            # Don't write the metafile if nothing was copied
            print(f"Creating '{dataset_file}'")
            with open(dataset_file, "w", encoding="utf-8") as fd:
                yaml.dump(metafile_data, fd, sort_keys=False)

        return metafile_data

    def du(
        self,
        sources,
        depth=0,
        ttl=TTL_INT,
        update=False,
        *,
        client_config=None,
    ) -> Iterable[Tuple[str, float]]:
        sources = self.enlist_sources(
            sources,
            ttl,
            update,
            client_config=client_config or self.client_config,
        )

        def du_dirs(src, node, subdepth):
            if subdepth > 0:
                subdirs = src.listing.data_storage.get_nodes_by_parent_path(
                    node.path, type="dir"
                )
                for sd in subdirs:
                    yield from du_dirs(src, sd, subdepth - 1)
            yield (
                src.get_node_full_path(node),
                src.listing.du(node)[0],
            )

        for src in sources:
            yield from du_dirs(src, src.node, depth)

    def find(
        self,
        sources,
        ttl=TTL_INT,
        update=False,
        names=None,
        inames=None,
        paths=None,
        ipaths=None,
        size=None,
        typ=None,
        columns=None,
        *,
        client_config=None,
    ) -> Iterator[str]:
        sources = self.enlist_sources(
            sources,
            ttl,
            update,
            client_config=client_config or self.client_config,
        )
        if not columns:
            columns = ["path"]
        field_set = set()
        for column in columns:
            if column == "du":
                field_set.add("dir_type")
                field_set.add("size")
                field_set.add("parent")
                field_set.add("name")
            elif column == "name":
                field_set.add("name")
            elif column == "owner":
                field_set.add("owner_name")
            elif column == "path":
                field_set.add("dir_type")
                field_set.add("parent")
                field_set.add("name")
            elif column == "size":
                field_set.add("size")
            elif column == "type":
                field_set.add("dir_type")
        fields = list(field_set)
        field_lookup = {f: i for i, f in enumerate(fields)}
        for src in sources:
            results = src.listing.find(
                src.node, fields, names, inames, paths, ipaths, size, typ
            )
            for row in results:
                yield "\t".join(
                    find_column_to_str(row, field_lookup, src, column)
                    for column in columns
                )

    def index(
        self,
        sources,
        ttl=TTL_INT,
        update=False,
        *,
        client_config=None,
        index_processors: Optional[Union[List[IndexingFormat], IndexingFormat]] = None,
    ) -> None:
        root_sources = [
            src for src in sources if Client.get_implementation(src).is_root_url(src)
        ]
        non_root_sources = [
            src
            for src in sources
            if not Client.get_implementation(src).is_root_url(src)
        ]

        client_config = client_config or self.client_config

        # for root sources (e.g s3://) we are just getting all buckets and
        # saving them as storages, without further indexing in each bucket
        for source in root_sources:
            for bucket in Client.get_implementation(source).ls_buckets(**client_config):
                client = self.get_client(bucket.uri, **client_config)
                print(f"Registering storage {client.uri}")
                self.data_storage.create_storage_if_not_registered(client.uri)

        if index_processors and not isinstance(index_processors, list):
            processors = [index_processors]
        else:
            processors = index_processors  # type: ignore
        sources = self.enlist_sources(
            non_root_sources,
            ttl,
            update,
            client_config=client_config,
            index_processors=processors,
            only_index=True,
        )

    def find_stale_storages(self) -> None:
        self.data_storage.find_stale_storages()
