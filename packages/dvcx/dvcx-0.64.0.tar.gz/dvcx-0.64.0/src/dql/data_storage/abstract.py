import hashlib
import json
import logging
import posixpath
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from functools import reduce
from itertools import groupby
from random import getrandbits
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)
from urllib.parse import urlparse

import sqlalchemy as sa
from attrs import frozen
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    Text,
    UniqueConstraint,
    and_,
    case,
    select,
)
from sqlalchemy.schema import CreateTable, DropTable
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import true
from sqlalchemy.sql.roles import DDLRole

from dql.data_storage.schema import DATASET_CORE_COLUMN_NAMES, SignalsTable
from dql.data_storage.schema import Node as NodeTable
from dql.dataset import DatasetDependency, DatasetRecord, DatasetRow
from dql.dataset import Status as DatasetStatus
from dql.error import DatasetNotFoundError, StorageNotFoundError
from dql.node import DirType, DirTypeGroup, Node, NodeWithPath, get_path
from dql.sql.types import Int, SQLType
from dql.storage import Status as StorageStatus
from dql.storage import Storage, StorageURI
from dql.utils import GLOB_CHARS, is_expired, sql_escape_like

if TYPE_CHECKING:
    from sqlalchemy.engine.base import Engine
    from sqlalchemy.engine.interfaces import Dialect
    from sqlalchemy.schema import SchemaItem
    from sqlalchemy.sql.compiler import Compiled
    from sqlalchemy.sql.elements import ClauseElement, ColumnElement
    from sqlalchemy.types import TypeEngine

    from dql.data_storage import schema

try:
    import numpy as np

    numpy_imported = True
except ImportError:
    numpy_imported = False


logger = logging.getLogger("dql")

RANDOM_BITS = 63  # size of the random integer field

SELECT_BATCH_SIZE = 100_000  # number of rows to fetch at a time


@frozen
class DatabaseEngine(ABC):
    dialect: ClassVar[Optional["Dialect"]] = None

    engine: "Engine"
    metadata: "MetaData"

    @classmethod
    def compile(cls, statement: "ClauseElement", **kwargs) -> "Compiled":
        """
        Compile a sqlalchemy query or ddl object to a Compiled object.

        Use the `string` and `params` properties of this object to get
        the resulting sql string and parameters.
        """
        if not isinstance(statement, DDLRole):
            # render_postcompile is needed for in_ queries to work
            kwargs["compile_kwargs"] = {
                **kwargs.pop("compile_kwargs", {}),
                "render_postcompile": True,
            }
        return statement.compile(dialect=cls.dialect, **kwargs)

    @classmethod
    def compile_to_args(
        cls, statement: "ClauseElement", **kwargs
    ) -> Union[Tuple[str], Tuple[str, Dict[str, Any]]]:
        """
        Compile a sqlalchemy query or ddl object to an args tuple.

        This tuple is formatted specifically for calling
        `cursor.execute(*args)` according to the python DB-API.
        """
        result = cls.compile(statement, **kwargs)
        params = result.params
        if params is None:
            return (result.string,)
        return (result.string, params)

    @abstractmethod
    def execute(
        self,
        query,
        cursor: Optional[Any] = None,
        conn: Optional[Any] = None,
    ) -> Iterator[Tuple[Any, ...]]:
        ...

    @abstractmethod
    def executemany(
        self, query, params, cursor: Optional[Any] = None
    ) -> Iterator[Tuple[Any, ...]]:
        ...

    @abstractmethod
    def execute_str(self, sql: str, parameters=None) -> Iterator[Tuple[Any, ...]]:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    def has_table(self, name: str) -> bool:
        """
        Return True if a table exists with the given name
        """
        return sa.inspect(self.engine).has_table(name)


class AbstractDataStorage(ABC):
    """
    Abstract Data Storage class, to be implemented by any Database Adapters
    for a specific database system. This manages the storing, searching, and
    retrieval of indexed metadata, and has shared logic for all database
    systems currently in use.
    """

    #
    # Constants, Initialization, and Tables
    #

    BUCKET_TABLE_NAME_PREFIX = "src_"
    PARTIALS_TABLE_NAME_PREFIX = "prt_"
    DATASET_TABLE_PREFIX = "ds_"
    SIGNALS_TABLE_PREFIX = "sg_"
    TABLE_NAME_SHA_LIMIT = 12
    STORAGE_TABLE = "buckets"
    DATASET_TABLE = "datasets"
    DATASET_VERSION_TABLE = "datasets_versions"
    DATASET_DEPENDENCY_TABLE = "datasets_dependencies"
    ID_GENERATOR_TABLE = "id_generator"

    schema: "schema.Schema"
    ddb: "DatabaseEngine"  # dataset db
    mdb: "DatabaseEngine"  # metadata db

    storage_class = Storage
    dataset_class = DatasetRecord
    dependency_class = DatasetDependency

    def __init__(
        self, uri: StorageURI = StorageURI(""), partial_id: Optional[int] = None
    ):
        self.uri = uri
        self.partial_id: Optional[int] = partial_id
        self._table: Optional[Table] = None
        self._nodes: Optional["schema.Node"] = None
        self._storages: Optional[Table] = None
        self._partials: Optional[Table] = None
        self._datasets: Optional[Table] = None
        self._datasets_versions: Optional[Table] = None
        self._datasets_dependencies: Optional[Table] = None
        self._id_generator: Optional[Table] = None
        self.dataset_fields = [
            c.name
            for c in self.datasets_columns()
            if c.name  # type: ignore[attr-defined]
        ]
        self.dataset_version_fields = [
            c.name
            for c in self.datasets_versions_columns()
            if c.name  # type: ignore[attr-defined]
        ]
        self.node_fields = [c.name for c in self.schema.node_cls.default_columns()]

    @staticmethod
    def buckets_columns() -> List["SchemaItem"]:
        return [
            Column("id", Integer, primary_key=True, nullable=False),
            Column("uri", Text, nullable=False),
            Column("timestamp", DateTime(timezone=True)),
            Column("expires", DateTime(timezone=True)),
            Column("started_inserting_at", DateTime(timezone=True)),
            Column("last_inserted_at", DateTime(timezone=True)),
            Column("status", Integer, nullable=False),
            Column("error_message", Text, nullable=False, default=""),
            Column("error_stack", Text, nullable=False, default=""),
        ]

    @staticmethod
    def datasets_columns() -> List["SchemaItem"]:
        return [
            Column("id", Integer, primary_key=True),
            Column("name", Text, nullable=False),
            Column("description", Text),
            Column("labels", JSON, nullable=True),
            Column("shadow", Boolean, nullable=False),
            Column("status", Integer, nullable=False),
            Column("created_at", DateTime(timezone=True)),
            Column("finished_at", DateTime(timezone=True)),
            Column("error_message", Text, nullable=False, default=""),
            Column("error_stack", Text, nullable=False, default=""),
            Column("script_output", Text, nullable=False, default=""),
            Column("job_id", Text, nullable=True),
            Column("sources", Text, nullable=False, default=""),
            Column("query_script", Text, nullable=False, default=""),
            Column("custom_column_types", JSON, nullable=True),
        ]

    @staticmethod
    def datasets_versions_columns() -> List["SchemaItem"]:
        return [
            Column("id", Integer, primary_key=True),
            Column(
                "dataset_id",
                Integer,
                ForeignKey("datasets.id", ondelete="CASCADE"),
                nullable=False,
            ),
            Column("version", Integer, nullable=False),
            Column("created_at", DateTime(timezone=True)),
            Column("sources", Text, nullable=False, default=""),
            Column("query_script", Text, nullable=False, default=""),
            Column("custom_column_types", JSON, nullable=True),
            UniqueConstraint("dataset_id", "version"),
        ]

    def datasets_dependencies_columns(self) -> List["SchemaItem"]:
        return [
            Column("id", Integer, primary_key=True),
            # TODO remove when https://github.com/iterative/dql/issues/959 is done
            Column(
                "source_dataset_id",
                Integer,
                ForeignKey(f"{self.DATASET_TABLE}.id"),
                nullable=False,
            ),
            Column(
                "source_dataset_version_id",
                Integer,
                ForeignKey(f"{self.DATASET_VERSION_TABLE}.id"),
                nullable=True,
            ),
            # TODO remove when https://github.com/iterative/dql/issues/959 is done
            Column(
                "dataset_id",
                Integer,
                ForeignKey(f"{self.DATASET_TABLE}.id"),
                nullable=True,
            ),
            Column(
                "dataset_version_id",
                Integer,
                ForeignKey(f"{self.DATASET_VERSION_TABLE}.id"),
                nullable=True,
            ),
            # TODO remove when https://github.com/iterative/dql/issues/1121 is done
            # If we unify datasets and bucket listing then both bucket fields won't
            # be needed
            Column(
                "bucket_id",
                Integer,
                ForeignKey(f"{self.STORAGE_TABLE}.id"),
                nullable=True,
            ),
            Column("bucket_version", Text, nullable=True),
        ]

    @staticmethod
    def storage_partial_columns() -> List["SchemaItem"]:
        return [
            Column("path_str", Text, nullable=False),
            # This is generated before insert and is not the SQLite rowid,
            # so it is not the primary key.
            Column("partial_id", Integer, nullable=False, index=True),
            Column("timestamp", DateTime(timezone=True)),
            Column("expires", DateTime(timezone=True)),
        ]

    @staticmethod
    def id_generator_columns() -> List["SchemaItem"]:
        return [
            Column("uri", Text, primary_key=True, nullable=False),
            # This is the last id used (and starts at zero if no ids have been used)
            Column("last_id", Integer, nullable=False),
        ]

    def convert_type(self, val: Any, col_type: SQLType) -> Any:  # noqa: PLR0911
        """
        Tries to convert value to specific type if needed and if compatible,
        otherwise throws an ValueError.
        If value is a list or some other iterable, it tries to convert sub elements
        as well
        """
        if numpy_imported and isinstance(val, (np.ndarray, np.generic)):
            val = val.tolist()

        col_python_type = self.python_type(col_type)
        value_type = type(val)

        exc = None
        try:
            if col_python_type == list and value_type in (list, tuple, set):
                if len(val) == 0:
                    return []
                item_pyton_type = self.python_type(col_type.item_type)
                if item_pyton_type != list:
                    if isinstance(val[0], item_pyton_type):
                        return val
                    if item_pyton_type == float and isinstance(val[0], int):
                        return [float(i) for i in val]
                return [self.convert_type(i, col_type.item_type) for i in val]
            if isinstance(val, col_python_type):
                return val
            if col_python_type == float and isinstance(val, int):
                return float(val)
            # special use case with JSON type as we save it as string
            if col_python_type == dict and value_type == str:
                return val
        except Exception as e:
            exc = e
        raise ValueError(
            f"Value {val!r} with type {value_type} incompatible for "
            f"column type {type(col_type).__name__}"
        ) from exc

    def get_storage_partial_table(self, name: str) -> Table:
        table = self.mdb.metadata.tables.get(name)
        if table is None:
            table = Table(
                name,
                self.mdb.metadata,
                *self.storage_partial_columns(),
            )
        return table

    @abstractmethod
    def clone(
        self, uri: StorageURI = StorageURI(""), partial_id: Optional[int] = None
    ) -> "AbstractDataStorage":
        """Clones DataStorage implementation for some Storage input"""

    @abstractmethod
    def clone_params(self) -> Tuple[Type["AbstractDataStorage"], List, Dict[str, Any]]:
        """
        Returns the class, args, and kwargs needed to instantiate a cloned copy of this
        AbstractDataStorage implementation, for use in separate processes or machines.
        """

    @abstractmethod
    def close(self) -> None:
        """Closes any active database connections"""

    @abstractmethod
    def init_id_generator(self, uri: str) -> None:
        pass

    @abstractmethod
    def init_db(self, uri: StorageURI, partial_id: int) -> None:
        """Initializes database tables for data storage"""

    @abstractmethod
    def _rename_table(self, old_name: str, new_name: str):
        """Renames a table from old_name to new_name"""

    #
    # Query Tables
    #

    @property
    def nodes(self):
        assert (
            self.current_bucket_table_name
        ), "Nodes can only be used if uri/current_bucket_table_name is set"
        if self._nodes is None:
            self._nodes = self.schema.node_cls(
                self.current_bucket_table_name, self.uri, self.ddb.metadata
            )
        return self._nodes

    def nodes_table(self, source_uri: str, partial_id: Optional[int] = None):
        if partial_id is None:
            raise ValueError("missing partial_id")
        table_name = self.bucket_table_name(source_uri, partial_id)
        return self.schema.node_cls(table_name, source_uri, self.ddb.metadata)

    def partials_table(self, uri: StorageURI):
        return self.get_storage_partial_table(self.partials_table_name(uri))

    def dataset_rows(self, dataset_name: str, version: Optional[int] = None):
        dataset = self.get_dataset(dataset_name)
        name = self.dataset_table_name(dataset_name, version)
        return self.schema.dataset_row_cls(
            name,
            self.ddb.engine,
            self.ddb.metadata,
            dataset.get_custom_column_types(version=version),
        )

    @property
    def storages(self) -> Table:
        if self._storages is None:
            self._storages = Table(
                self.STORAGE_TABLE, self.mdb.metadata, *self.buckets_columns()
            )
        return self._storages

    @property
    def partials(self) -> Table:
        assert (
            self.current_partials_table_name
        ), "Partials can only be used if uri/current_bucket_table_name is set"
        if self._partials is None:
            self._partials = self.get_storage_partial_table(
                self.current_partials_table_name
            )
        return self._partials

    @property
    def datasets(self) -> Table:
        if self._datasets is None:
            self._datasets = Table(
                self.DATASET_TABLE, self.mdb.metadata, *self.datasets_columns()
            )
        return self._datasets

    @property
    def datasets_versions(self) -> Table:
        if self._datasets_versions is None:
            self._datasets_versions = Table(
                self.DATASET_VERSION_TABLE,
                self.mdb.metadata,
                *self.datasets_versions_columns(),
            )
        return self._datasets_versions

    @property
    def datasets_dependencies(self) -> Table:
        if self._datasets_dependencies is None:
            self._datasets_dependencies = Table(
                self.DATASET_DEPENDENCY_TABLE,
                self.mdb.metadata,
                *self.datasets_dependencies_columns(),
            )
        return self._datasets_dependencies

    @property
    def id_generator(self) -> Table:
        if self._id_generator is None:
            self._id_generator = Table(
                self.ID_GENERATOR_TABLE, self.mdb.metadata, *self.id_generator_columns()
            )
        return self._id_generator

    @property
    def dataset_row_cls(self):
        return self.schema.dataset_row_cls

    #
    # Query Starters (These can be overridden by subclasses)
    #

    def storages_select(self, *columns):
        storages = self.storages
        if not columns:
            return storages.select()
        return select(*columns).select_from(storages)

    def storages_update(self):
        return self.storages.update()

    def storages_delete(self):
        return self.storages.delete()

    def partials_select(self, *columns):
        partials = self.partials
        if not columns:
            return partials.select()
        return select(*columns).select_from(partials)

    def partials_update(self):
        return self.partials.update()

    def datasets_select(self, *columns):
        datasets = self.datasets
        if not columns:
            return datasets.select()
        return select(*columns).select_from(datasets)

    def datasets_update(self):
        return self.datasets.update()

    def datasets_delete(self):
        return self.datasets.delete()

    def datasets_versions_select(self, *columns):
        datasets_versions = self.datasets_versions
        if not columns:
            return datasets_versions.select()
        return select(*columns).select_from(datasets_versions)

    def datasets_versions_update(self):
        return self.datasets_versions.update()

    def datasets_versions_delete(self):
        return self.datasets_versions.delete()

    def id_generator_select(self, *columns):
        id_generator = self.id_generator
        if not columns:
            return id_generator.select()
        return select(*columns).select_from(id_generator)

    def id_generator_update(self):
        return self.id_generator.update()

    def id_generator_delete(self):
        return self.id_generator.delete()

    def id_generator_delete_uri(self, uri: str):
        id_generator = self.id_generator
        return id_generator.delete().where(id_generator.c.uri == uri)

    def datasets_dependencies_select(self, *columns):
        datasets_dependencies = self.datasets_dependencies
        if not columns:
            return datasets_dependencies.select()
        return select(*columns).select_from(datasets_dependencies)

    def datasets_dependencies_update(self):
        return self.datasets_dependencies.update()

    def datasets_dependencies_delete(self):
        return self.datasets_dependencies.delete()

    #
    # Query Execution
    #

    def dataset_select_paginated(
        self,
        query,
        limit: Optional[int] = None,
        order_by: Sequence[str] = (),
        page_size: int = SELECT_BATCH_SIZE,
    ) -> Generator[DatasetRow, None, None]:
        """
        This is equivalent to ddb.execute, but for selecting rows in batches
        """
        cols = query.selected_columns
        cols_names = [c.name for c in cols]

        if not order_by:
            ordering = [cols.source, cols.parent, cols.name, cols.version, cols.etag]
        else:
            ordering = [cols[c] for c in order_by]

        # reset query order by and apply new order by id
        paginated_query = query.order_by(None).order_by(*ordering).limit(page_size)

        offset = 0
        num_yielded = 0
        while True:
            if limit:
                limit -= num_yielded
                if limit == 0:
                    break
                if limit < page_size:
                    paginated_query = paginated_query.limit(None).limit(limit)

            results = self.ddb.execute(paginated_query.offset(offset))

            processed = False
            for row in results:
                processed = True
                yield DatasetRow.from_result_row(cols_names, row)
                num_yielded += 1

            if not processed:
                break  # no more results
            offset += page_size

    #
    # ID Generator
    #

    @abstractmethod
    def _get_next_ids(self, uri: str, count: int) -> range:
        ...

    def _get_next_id(self, uri: str) -> int:
        return self._get_next_ids(uri, 1)[0]

    #
    # Table Name Internal Functions
    #
    @staticmethod
    def uri_to_storage_info(uri: str) -> Tuple[str, str]:
        parsed = urlparse(uri)
        name = parsed.path if parsed.scheme == "file" else parsed.netloc
        return parsed.scheme, name

    def bucket_table_name(self, uri: str, version: int) -> str:
        scheme, name = self.uri_to_storage_info(uri)
        return f"{self.BUCKET_TABLE_NAME_PREFIX}{scheme}_{name}_{version}"

    def partials_table_name(self, uri: StorageURI) -> str:
        sha = hashlib.sha256(uri.encode("utf-8")).hexdigest()[:12]
        return f"{self.PARTIALS_TABLE_NAME_PREFIX}_{sha}"

    def signals_table_name(self, uri: str, version: int = 0) -> str:
        parsed = urlparse(uri)
        return f"{self.SIGNALS_TABLE_PREFIX}{parsed.scheme}_{parsed.netloc}_{version}"

    def dataset_table_name(
        self, dataset_name: str, version: Optional[int] = None
    ) -> str:
        name = self.DATASET_TABLE_PREFIX + dataset_name
        if version is not None:
            name += f"_{version}"

        return name

    @property
    def current_bucket_table_name(self) -> Optional[str]:
        if not self.uri:
            return None

        # We want to make sure that partial_id is reused when calling
        # data_storage.clone(). It should only be calculated once per
        # listing, so we don't call get_valid_partial_id here
        if self.partial_id is None:
            raise ValueError("missing partial_id")

        return self.bucket_table_name(self.uri, self.partial_id)

    @property
    def current_partials_table_name(self) -> Optional[str]:
        if not self.uri:
            return None
        return self.partials_table_name(self.uri)

    #
    # Storages
    #

    @abstractmethod
    def create_storage_if_not_registered(self, uri: StorageURI) -> None:
        """
        Saves new storage if it doesn't exist in database
        """

    @abstractmethod
    def register_storage_for_indexing(
        self,
        uri: StorageURI,
        force_update: bool,
        prefix: str = "",
    ) -> Tuple[Storage, bool, bool, Optional[int]]:
        """
        Prepares storage for indexing operation.
        This method should be called before index operation is started
        It returns:
            - storage, prepared for indexing
            - boolean saying if indexing is needed
            - boolean saying if indexing is currently pending (running)
            - boolean saying if this storage is newly created
        """

    @abstractmethod
    def find_stale_storages(self):
        """
        Finds all pending storages for which the last inserted node has happened
        before STALE_HOURS_LIMIT hours, and marks it as STALE
        """

    @abstractmethod
    def mark_storage_indexed(
        self,
        uri: StorageURI,
        status: int,
        ttl: int,
        end_time: Optional[datetime] = None,
        prefix: str = "",
        partial_id: int = 0,
        error_message: str = "",
        error_stack: str = "",
    ) -> None:
        """
        Marks storage as indexed.
        This method should be called when index operation is finished
        """

    @abstractmethod
    def mark_storage_not_indexed(self, uri: StorageURI) -> None:
        """
        Mark storage as not indexed.
        This method should be called when storage index is deleted
        """

    async def update_last_inserted_at(self, uri: Optional[StorageURI] = None) -> None:
        """Updates last inserted datetime in bucket with current time"""
        uri = uri or self.uri
        updates = {"last_inserted_at": datetime.now(timezone.utc)}
        s = self.storages
        self.mdb.execute(
            self.storages_update().where(s.c.uri == uri).values(**updates)  # type: ignore [attr-defined]
        )

    def get_all_storage_uris(self) -> Iterator[StorageURI]:
        s = self.storages
        yield from (r[0] for r in self.mdb.execute(self.storages_select(s.c.uri)))

    def get_storage(self, uri: StorageURI) -> Storage:
        """
        Gets storage representation from database.
        E.g if s3 is used as storage this would be s3 bucket data
        """
        s = self.storages
        result = next(
            self.mdb.execute(self.storages_select().where(s.c.uri == uri)), None
        )
        if not result:
            raise StorageNotFoundError(f"Storage {uri} not found.")

        return self.storage_class._make(result)

    def list_storages(self) -> List[Storage]:
        result = self.mdb.execute(self.storages_select())
        if not result:
            return []

        return [self.storage_class._make(r) for r in result]

    def mark_storage_pending(self, storage: Storage) -> Storage:
        # Update status to pending and dates
        updates = {
            "status": StorageStatus.PENDING,
            "timestamp": None,
            "expires": None,
            "last_inserted_at": None,
            "started_inserting_at": datetime.now(timezone.utc),
        }
        storage = storage._replace(**updates)  # type: ignore [arg-type]
        s = self.storages
        self.mdb.execute(
            self.storages_update().where(s.c.uri == storage.uri).values(**updates)  # type: ignore [attr-defined]
        )
        return storage

    def _mark_storage_stale(self, storage_id: int) -> None:
        # Update status to pending and dates
        updates = {"status": StorageStatus.STALE, "timestamp": None, "expires": None}
        s = self.storages
        self.mdb.execute(
            self.storages.update().where(s.c.id == storage_id).values(**updates)  # type: ignore [attr-defined]
        )

    #
    # Partial Indexes
    #

    def get_next_partial_id(self, uri: StorageURI) -> int:
        if not uri:
            raise ValueError("uri for get_next_partial_id() cannot be empty")
        return self._get_next_id(f"partials:{uri}")

    def get_valid_partial_id(
        self, uri: StorageURI, prefix: str, raise_exc: bool = True
    ) -> Optional[int]:
        # This SQL statement finds all entries that are
        # prefixes of the given prefix, matching this or parent directories
        # that are indexed.
        dir_prefix = posixpath.join(prefix, "")
        p = self.partials_table(uri)
        expire_values = self.mdb.execute(
            select(p.c.expires, p.c.partial_id)
            .select_from(p)
            .where(
                p.c.path_str == func.substr(dir_prefix, 1, func.length(p.c.path_str))
            )
            .order_by(p.c.expires.desc())
        )
        for expires, partial_id in expire_values:
            if not is_expired(expires):
                return partial_id
        if raise_exc:
            raise RuntimeError(f"Unable to get valid partial_id: {uri=}, {prefix=}")
        return None

    #
    # Datasets
    #

    @abstractmethod
    def create_dataset_rows_table(
        self,
        name: str,
        custom_columns: Sequence["sa.Column"] = (),
        if_not_exists: bool = True,
    ) -> Table:
        """Creates a dataset rows table for the given dataset name and columns"""

    @abstractmethod
    def create_shadow_dataset(
        self,
        name: str,
        sources: Optional[List[str]] = None,
        query_script: str = "",
        create_rows: Optional[bool] = True,
        custom_columns: Sequence[Column] = (),
    ) -> "DatasetRecord":
        """
        Creates shadow database record if doesn't exist.
        If create_rows is False, dataset rows table will not be created
        """

    @abstractmethod
    def insert_into_shadow_dataset(
        self, name: str, uri: str, path: str, recursive: bool = False
    ) -> None:
        """Inserts data to shadow dataset based on bucket uri and glob path"""

    @abstractmethod
    def create_dataset_version(
        self,
        name: str,
        version: int,
        sources: str = "",
        query_script: str = "",
        create_rows_table=True,
        custom_column_types: Optional[Dict[str, str]] = None,
    ) -> "DatasetRecord":
        """Creates new dataset version, optionally creating new rows table"""

    @abstractmethod
    def merge_dataset_rows(
        self,
        src: "DatasetRecord",
        dst: "DatasetRecord",
        src_version: Optional[int] = None,
        dst_version: Optional[int] = None,
    ) -> None:
        """
        Merges source dataset rows and current latest destination dataset rows
        into a new rows table created for new destination dataset version.
        Note that table for new destination version must be created upfront.
        Merge results should not contain duplicates.
        """

    @abstractmethod
    def copy_shadow_dataset_rows(
        self,
        src: "DatasetRecord",
        dst: "DatasetRecord",
    ) -> None:
        """
        Copies source shadow dataset rows into a new rows table
        created for new destination dataset.
        Note that table for new destination version must be created upfront.
        Results could contain duplicates.
        """

    @abstractmethod
    def remove_shadow_dataset(self, dataset: "DatasetRecord", drop_rows=True) -> None:
        """
        Removes shadow dataset and it's corresponding rows if needed
        """

    @abstractmethod
    def dataset_rows_select(self, select_query: sa.sql.selectable.Select, **kwargs):
        """
        Method for fetching dataset rows from database. This is abstract since
        in some DBs we need to use special settings
        """

    @abstractmethod
    def get_dataset_sources(
        self, name: str, version: Optional[int]
    ) -> List[StorageURI]:
        """Returns a set of all available sources used in some dataset"""

    def get_dataset_rows(
        self,
        name: str,
        offset: Optional[int] = 0,
        limit: Optional[int] = 20,
        version=None,
        custom_columns=False,
        source: Optional[str] = None,
    ) -> Iterator[DatasetRow]:
        """Gets dataset rows"""
        # if custom_columns are to be returned, we are setting columns to None to
        # retrieve all columns from a table (default ones and custom)
        columns = list(DATASET_CORE_COLUMN_NAMES) if not custom_columns else None
        dr = self.dataset_rows(name, version)

        select_columns = []
        if not columns:
            # fetching all columns if specific columns are not defined
            columns = [c.name for c in dr.c]

        select_columns = [dr.c[c] for c in columns]
        column_index_mapping = {c: i for i, c in enumerate(columns)}

        query = dr.select(*select_columns)
        if source:
            query = query.where(dr.c.source == source)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        # ordering by primary key / index
        query = query.order_by("id")

        def map_row_to_dict(row):
            return {c: row[i] for c, i in column_index_mapping.items()}

        for row in self.dataset_rows_select(query):
            yield DatasetRow.from_dict(map_row_to_dict(row))

    def get_dataset_row(
        self,
        name: str,
        row_id: int,
        dataset_version: Optional[int] = None,
    ) -> Optional[DatasetRow]:
        """Returns one row by id from a defined dataset"""
        dr = self.dataset_rows(name, dataset_version)
        row = next(
            self.ddb.execute(
                select("*").select_from(dr.get_table()).where(dr.c.id == row_id)
            ),
            None,
        )
        if row:
            return DatasetRow(*row)

        return None

    def nodes_dataset_query(
        self,
        column_names: Optional[Iterable[str]] = None,
        path: Optional[str] = None,
        recursive: Optional[bool] = False,
        uri: Optional[str] = None,
    ) -> "sa.Select":
        """
        Provides a query object representing the given `uri` as a dataset.

        If `uri` is not given then `self.uri` is used. The given `column_names`
        will be selected in the order they're given. `path` is a glob which
        will select files in matching directories, or if `recursive=True` is
        set then the entire tree under matching directories will be selected.
        """

        def _is_glob(path: str) -> bool:
            return any(c in path for c in ["*", "?", "[", "]"])

        assert uri == self.uri
        n = self.nodes
        select_query = n.dataset_query(*(column_names or []))
        if path is None:
            return select_query
        if recursive:
            root = False
            if not path or path == "/":
                # root of the bucket, e.g s3://bucket/ -> getting all the nodes
                # in the bucket
                root = True

            if not root and not _is_glob(path):
                # not a root and not a explicit glob, so it's pointing to some directory
                # and we are adding a proper glob syntax for it
                # e.g s3://bucket/dir1 -> s3://bucket/dir1/*
                path = path.rstrip("/") + "/*"

            if not root:
                # not a root, so running glob query
                select_query = select_query.where(self.path_expr(n).op("GLOB")(path))
        else:
            parent = self.get_node_by_path(path.lstrip("/").rstrip("/*"))
            select_query = select_query.where(n.c.parent == parent.path)
        return select_query

    def rename_dataset_table(
        self,
        old_name: str,
        new_name: str,
        old_version: Optional[int] = None,
        new_version: Optional[int] = None,
    ) -> None:
        """
        When registering dataset, we need to rename rows table from
        ds_<id>_shadow to ds_<id>_<version>.
        Example: from ds_24_shadow to ds_24_1
        """
        old_ds_table_name = self.dataset_table_name(old_name, old_version)
        new_ds_table_name = self.dataset_table_name(new_name, new_version)

        self._rename_table(old_ds_table_name, new_ds_table_name)

    def update_dataset(self, dataset_name: str, conn=None, **kwargs) -> None:
        """Updates dataset fields"""
        dataset = self.get_dataset(dataset_name)
        values = {}
        for field, value in kwargs.items():
            if field in self.dataset_fields[1:]:
                if field in ["labels", "custom_column_types"]:
                    values[field] = json.dumps(value) if value else None
                else:
                    values[field] = value

        if not values:
            # Nothing to update
            return

        d = self.datasets
        self.mdb.execute(
            self.datasets_update().where(d.c.name == dataset_name).values(values),
            conn=conn,
        )  # type: ignore [attr-defined]

        if "name" in kwargs and kwargs["name"] != dataset_name:
            # updating name must result in updating dataset table names as well
            old_name = dataset.name
            new_name = kwargs["name"]
            if dataset.shadow:
                self.rename_dataset_table(old_name, new_name)
            else:
                for version in dataset.versions:  # type: ignore [union-attr]
                    self.rename_dataset_table(
                        old_name,
                        new_name,
                        old_version=version.version,
                        new_version=version.version,
                    )

    def _parse_dataset(self, rows) -> Optional[DatasetRecord]:
        versions = []
        for r in rows:
            versions.append(self.dataset_class.parse(*r))
        if not versions:
            return None
        return reduce(lambda ds, version: ds.merge_versions(version), versions)

    def remove_dataset_version(self, dataset: DatasetRecord, version: int) -> None:
        """
        Deletes one single dataset version. If it was last version,
        it removes dataset completely
        """
        if not dataset.has_version(version):
            return

        self.remove_dataset_dependencies(dataset, version)
        self.remove_dataset_dependants(dataset, version)

        d = self.datasets
        dv = self.datasets_versions
        self.mdb.execute(
            self.datasets_versions_delete().where(
                (dv.c.dataset_id == dataset.id) & (dv.c.version == version)
            )
        )

        if dataset.versions and len(dataset.versions) == 1:
            # had only one version, fully deleting dataset
            self.mdb.execute(self.datasets_delete().where(d.c.id == dataset.id))

        dataset.remove_version(version)

        table_name = self.dataset_table_name(dataset.name, version)
        table = Table(table_name, MetaData())
        table.drop(self.ddb.engine)

    def list_datasets(
        self, shadow_only: Optional[bool] = None
    ) -> Iterator["DatasetRecord"]:
        """Lists all datasets (or shadow datasets only)"""
        d = self.datasets
        dv = self.datasets_versions
        query = self.datasets_select(
            *(getattr(d.c, f) for f in self.dataset_fields),
            *(getattr(dv.c, f) for f in self.dataset_version_fields),
        )
        j = d.join(dv, d.c.id == dv.c.dataset_id, isouter=True)

        if shadow_only is not None:
            query = query.where(  # type: ignore [attr-defined]
                d.c.shadow == bool(shadow_only)
            ).order_by("dataset_id")

        query = query.select_from(j)
        rows = self.mdb.execute(query)

        for _, g in groupby(rows, lambda r: r[0]):
            dataset = self._parse_dataset(list(g))
            if dataset:
                dataset.sort_versions()
                yield dataset

    def get_dataset(self, name: str) -> DatasetRecord:
        """Gets a single dataset by name"""
        d = self.datasets
        dv = self.datasets_versions
        query = self.datasets_select(
            *(getattr(d.c, f) for f in self.dataset_fields),
            *(getattr(dv.c, f) for f in self.dataset_version_fields),
        ).where(d.c.name == name)  # type: ignore [attr-defined]
        j = d.join(dv, d.c.id == dv.c.dataset_id, isouter=True)
        query = query.select_from(j)
        ds = self._parse_dataset(self.mdb.execute(query))
        if not ds:
            raise DatasetNotFoundError(f"Dataset {name} not found.")
        return ds

    def update_dataset_status(
        self,
        dataset: DatasetRecord,
        status: int,
        conn=None,
        error_message="",
        error_stack="",
        script_output="",
    ) -> DatasetRecord:
        """
        Updates dataset status and appropriate fields related to status
        """
        update_data: Dict[str, Any] = {"status": status}
        if status in [DatasetStatus.COMPLETE, DatasetStatus.FAILED]:
            # if in final state, updating finished_at datetime
            update_data["finished_at"] = datetime.now(timezone.utc)
            if script_output:
                update_data["script_output"] = script_output

        if status == DatasetStatus.FAILED:
            update_data["error_message"] = error_message
            update_data["error_stack"] = error_stack

        self.update_dataset(dataset.name, conn=conn, **update_data)
        dataset.update(**update_data)
        return dataset

    def dataset_rows_count(self, name: str, version=None) -> int:
        """Returns total number of rows in a dataset"""
        dr = self.dataset_rows(name, version)
        query = select(sa.func.count()).select_from(dr.get_table())
        res = next(self.ddb.execute(query), None)
        if not res:
            return 0

        return res[0]

    def dataset_rows_size(self, name: str, version=None) -> int:
        """Returns total dataset size by summing up size column of each row"""
        dr = self.dataset_rows(name, version)
        query = select(sa.func.sum(dr.c.size)).select_from(dr.get_table())
        res = next(self.ddb.execute(query), None)
        if not res:
            return 0

        return res[0]

    #
    # Nodes
    #

    @abstractmethod
    async def insert_node(self, entry: Dict[str, Any]) -> int:
        """
        Inserts file or directory node into the database
        and returns the id of the newly added node
        """

    @abstractmethod
    async def insert_nodes(self, entries: Iterable[Dict[str, Any]]) -> None:
        """Inserts file or directory nodes into the database"""

    def insert_nodes_done(self):  # noqa: B027
        """
        Only needed for certain implementations
        to signal when node inserts are complete.
        """

    @abstractmethod
    def insert_rows(self, table: Table, rows: Iterable[Dict[str, Any]]) -> None:
        """Does batch inserts of any kind of rows into table"""

    def insert_rows_done(self, table: Table) -> None:  # noqa: B027
        """
        Only needed for certain implementations
        to signal when rows inserts are complete.
        """

    @abstractmethod
    def insert_dataset_rows(
        self, name: str, rows: Optional[Iterable[Dict[str, Any]]]
    ) -> None:
        """Inserts dataset rows directly into dataset table"""

    @abstractmethod
    def instr(self, source, target) -> "ColumnElement":
        """
        Return SQLAlchemy Boolean determining if a target substring is present in
        source string column
        """

    @abstractmethod
    def get_table(self, name: str) -> sa.Table:
        """
        Returns a SQLAlchemy Table object by name. If table doesn't exist, it should
        create it
        """

    @abstractmethod
    def add_column(self, table: Table, col_name: str, col_type: "TypeEngine") -> None:
        """Adds a column with a name and type to a table"""

    @abstractmethod
    def dataset_column_types(
        self, name: str, version=None, custom=False
    ) -> List[Dict[str, str]]:
        """
        Return a list of all column types for a specific dataset.
        For each column it generates dict with name and python type (in string format)
        of the column
        """

    def python_type(self, col_type: Union["TypeEngine", "SQLType"]) -> Any:
        """Returns python type representation of some Sqlalchemy column type"""
        return col_type.python_type

    async def insert_root(self) -> int:
        """
        Inserts root directory and returns the id of the newly added root
        """
        return await self.insert_node(
            {"vtype": "", "dir_type": DirType.DIR, "parent": "", "partial_id": 0}
        )

    def _prepare_node(self, d: Dict[str, Any]) -> Dict[str, Any]:
        if d.get("dir_type") is None:
            if d.get("is_dir"):
                dir_type = DirType.DIR
            else:
                dir_type = DirType.FILE
            d["dir_type"] = dir_type

        if d.get("parent") is None:
            raise RuntimeError(f"No Path for node data: {d}")

        d = {
            "source": self.uri,
            "name": "",
            "vtype": "",
            "is_latest": True,
            "size": 0,
            "valid": True,
            "random": getrandbits(RANDOM_BITS),
            "version": "",
            "parent_id": None,
            **d,
        }
        return {f: d.get(f) for f in self.node_fields[1:]}

    def add_node_type_where(
        self,
        query,
        type: Optional[str],
        include_subobjects: bool = True,
    ):
        if type is None:
            return query

        file_group: Sequence[int]
        if type in {"f", "file", "files"}:
            if include_subobjects:
                file_group = DirTypeGroup.SUBOBJ_FILE
            else:
                file_group = DirTypeGroup.FILE
        elif type in {"d", "dir", "directory", "directories"}:
            if include_subobjects:
                file_group = DirTypeGroup.SUBOBJ_DIR
            else:
                file_group = DirTypeGroup.DIR
        else:
            raise ValueError(f"invalid file type: {type!r}")

        c = query.selected_columns
        q = query.where(c.dir_type.in_(file_group))
        if not include_subobjects:
            q = q.where(c.vtype == "")
        return q

    def get_nodes(self, query) -> Iterator[Node]:
        """
        This gets nodes based on the provided query, and should be used sparingly,
        as it will be slow on any OLAP database systems.
        """
        return (Node(*row) for row in self.ddb.execute(query))

    def get_nodes_by_parent_path(
        self,
        parent_path: str,
        type: Optional[str] = None,
    ) -> Iterator[Node]:
        """Gets nodes from database by parent path, with optional filtering"""
        n = self.nodes
        where_cond = (n.c.parent == parent_path) & (n.c.is_latest == true())
        if parent_path == "":
            # Exclude the root dir
            where_cond = where_cond & (n.c.name != "")
        query = n.select(*n.default_columns()).where(where_cond)
        query = self.add_node_type_where(query, type)
        query = query.order_by(n.c.source, n.c.parent, n.c.name, n.c.version, n.c.etag)
        return self.get_nodes(query)

    def _get_nodes_by_glob_path_pattern(
        self, path_list: List[str], glob_name: str
    ) -> Iterator[Node]:
        """Finds all Nodes that correspond to GLOB like path pattern."""
        n = self.nodes
        path_glob = "/".join(path_list + [glob_name])
        dirpath = path_glob[: -len(glob_name)]
        relpath = func.substr(self.path_expr(n), len(dirpath) + 1)

        return self.get_nodes(
            n.select(*n.default_columns())
            .where(
                (self.path_expr(n).op("GLOB")(path_glob))
                & (n.c.is_latest == true())
                & ~self.instr(relpath, "/")
                & (self.path_expr(n) != dirpath)
            )
            .order_by(n.c.source, n.c.parent, n.c.name, n.c.version, n.c.etag)
        )

    def _get_node_by_path_list(self, path_list: List[str], name: str) -> Node:
        """
        Gets node that correspond some path list, e.g ["data-lakes", "dogs-and-cats"]
        """
        parent = "/".join(path_list)
        n = self.nodes
        row = next(
            self.ddb.execute(
                n.select(*n.default_columns())
                .where(
                    (n.c.parent == parent)
                    & (n.c.name == name)
                    & (n.c.is_latest == true())
                )
                .order_by(n.c.source, n.c.parent, n.c.name, n.c.version, n.c.etag)
            ),
            None,
        )
        if not row:
            path = f"{parent}/{name}"
            raise FileNotFoundError(f"Unable to resolve path {path!r}")
        return Node(*row)

    def _populate_nodes_by_path(self, path_list: List[str]) -> List[Node]:
        """
        Puts all nodes found by path_list into the res input variable.
        Note that path can have GLOB like pattern matching which means that
        res can have multiple nodes as result.
        If there is no GLOB pattern, res should have one node as result that
        match exact path by path_list
        """
        if not path_list:
            return [self._get_node_by_path_list([], "")]
        matched_paths: List[List[str]] = [[]]
        for curr_name in path_list[:-1]:
            if set(curr_name).intersection(GLOB_CHARS):
                new_paths = []
                for path in matched_paths:
                    nodes = self._get_nodes_by_glob_path_pattern(path, curr_name)
                    for node in nodes:
                        if node.is_container:
                            new_paths.append(path + [node.name or ""])
                matched_paths = new_paths
            else:
                for path in matched_paths:
                    path.append(curr_name)
        curr_name = path_list[-1]
        if set(curr_name).intersection(GLOB_CHARS):
            result: List[Node] = []
            for path in matched_paths:
                nodes = self._get_nodes_by_glob_path_pattern(path, curr_name)
                result.extend(nodes)
        else:
            result = [
                self._get_node_by_path_list(path, curr_name) for path in matched_paths
            ]
        return result

    def get_node_by_path(self, path: str) -> Node:
        """Gets node that corresponds to some path"""
        n = self.nodes
        query = n.select(*n.default_columns()).where(
            (self.path_expr(n) == path.strip("/")) & (n.c.is_latest == true())
        )
        if path.endswith("/"):
            query = self.add_node_type_where(query, "dir")

        query = query.order_by(n.c.source, n.c.parent, n.c.name, n.c.version, n.c.etag)
        row = next(self.ddb.execute(query), None)
        if not row:
            raise FileNotFoundError(f"Unable to resolve path {path}")
        return Node(*row)

    def expand_path(self, path: str) -> List[Node]:
        """Simulates Unix-like shell expansion"""
        clean_path = path.strip("/")
        path_list = clean_path.split("/") if clean_path != "" else []
        res = self._populate_nodes_by_path(path_list)
        if path.endswith("/"):
            res = [node for node in res if node.dir_type in DirTypeGroup.SUBOBJ_DIR]
        return res

    def select_node_fields_by_parent_path(
        self,
        parent_path: str,
        fields: Iterable[str],
    ) -> Iterator[Tuple[Any, ...]]:
        """
        Gets latest-version file nodes from the provided parent path
        """
        n = self.nodes
        where_cond = (n.c.parent == parent_path) & (n.c.is_latest == true())
        if parent_path == "":
            # Exclude the root dir
            where_cond = where_cond & (n.c.name != "")
        return self.ddb.execute(
            n.select(*(getattr(n.c, f) for f in fields))
            .where(where_cond)
            .order_by(n.c.source, n.c.parent, n.c.name, n.c.version, n.c.etag)
        )

    def select_node_fields_by_parent_path_tar(
        self, parent_path: str, fields: Iterable[str]
    ) -> Iterator[Tuple[Any, ...]]:
        """
        Gets latest-version file nodes from the provided parent path
        """
        n = self.nodes
        dirpath = f"{parent_path}/"
        relpath = func.substr(self.path_expr(n), len(dirpath) + 1)

        def field_to_expr(f):
            if f == "name":
                return relpath
            return getattr(n.c, f)

        q = (
            select(*(field_to_expr(f) for f in fields))
            .where(
                self.path_expr(n).like(f"{sql_escape_like(dirpath)}%"),
                ~self.instr(relpath, "/"),
                n.c.is_latest == true(),
            )
            .order_by(n.c.source, n.c.parent, n.c.name, n.c.version, n.c.etag)
        )
        return self.ddb.execute(q)

    def size(
        self, node: Union[Node, Dict[str, Any]], count_files: bool = False
    ) -> Tuple[int, int]:
        """
        Calculates size of some node (and subtree below node).
        Returns size in bytes as int and total files as int
        """
        if isinstance(node, dict):
            is_dir = node.get("is_dir", node["dir_type"] in DirTypeGroup.SUBOBJ_DIR)
            node_size = node["size"]
            path = get_path(node["parent"], node["name"])
        else:
            is_dir = node.is_container
            node_size = node.size
            path = node.path
        if not is_dir:
            # Return node size if this is not a directory
            return node_size, 1

        sub_glob = posixpath.join(path, "*")
        n = self.nodes
        selections = [
            func.sum(n.c.size),
        ]
        if count_files:
            selections.append(
                func.sum(n.c.dir_type.in_(DirTypeGroup.FILE)),
            )
        results = next(
            self.ddb.execute(
                n.select(*selections).where(
                    (self.path_expr(n).op("GLOB")(sub_glob)) & (n.c.is_latest == true())
                )
            ),
            (0, 0),
        )
        if count_files:
            return results[0] or 0, results[1] or 0
        else:
            return results[0] or 0, 0

    def path_expr(self, t):
        return case((t.c.parent == "", t.c.name), else_=t.c.parent + "/" + t.c.name)

    def _find_query(
        self,
        node: Node,
        query,
        type: Optional[str] = None,
        conds=None,
        order_by: Optional[Union[str, List[str]]] = None,
    ) -> Any:
        if not conds:
            conds = []

        n = self.nodes
        path = self.path_expr(n)

        if node.path:
            sub_glob = posixpath.join(node.path, "*")
            conds.append(path.op("GLOB")(sub_glob))
        else:
            conds.append(path != "")

        query = query.where(
            and_(
                *conds,
                n.c.is_latest == true(),
            )
        )
        if type is not None:
            query = self.add_node_type_where(query, type)
        if order_by is not None:
            if isinstance(order_by, str):
                order_by = [order_by]
            query = query.order_by(*[getattr(n.c, col) for col in order_by])
        return query

    def get_subtree_files(
        self,
        node: Node,
        sort: Union[List[str], str, None] = None,
        include_subobjects: bool = True,
    ) -> Iterator[NodeWithPath]:
        """
        Returns all file nodes that are "below" some node.
        Nodes can be sorted as well.
        """
        n = self.nodes
        query = self._find_query(node, n.select(n.default_columns()))
        query = self.add_node_type_where(query, "f", include_subobjects)

        if sort is not None:
            if not isinstance(sort, list):
                sort = [sort]
            query = query.order_by(*(sa.text(s) for s in sort))  # type: ignore [attr-defined]

        prefix_len = len(node.path)

        def make_node_with_path(row):
            sub_node = Node(*row)
            return NodeWithPath(
                sub_node, sub_node.path[prefix_len:].lstrip("/").split("/")
            )

        return map(make_node_with_path, self.ddb.execute(query))

    def find(
        self,
        node: Node,
        fields: Iterable[str],
        type=None,
        conds=None,
        order_by=None,
    ) -> Iterator[Tuple[Any, ...]]:
        """
        Finds nodes that match certain criteria and only looks for latest nodes
        under the passed node.
        """
        n = self.nodes
        query = self._find_query(
            node,
            n.select(*(getattr(n.c, f) for f in fields)),
            type,
            conds,
            order_by=order_by,
        )
        return self.ddb.execute(query)

    def update_type(self, node_id: int, dir_type: int) -> None:
        """Updates type of specific node in database"""
        n = self.nodes
        self.ddb.execute(
            self.nodes.update().where(n.c.id == node_id).values(dir_type=dir_type)  # type: ignore [attr-defined]
        )

    def update_node(self, node_id: int, values: Dict[str, Any]) -> None:
        """Update entry of a specific node in the database."""
        n = self.nodes
        self.ddb.execute(self.nodes.update().values(**values).where(n.c.id == node_id))

    def return_ds_hook(self, name: str) -> None:  # noqa: B027
        """
        Hook to be run when a return ds is ready to be saved in a
        DatasetQuery script.
        """

    def create_udf_table(
        self,
        name: str,
        custom_columns: Sequence["sa.Column"] = (),
    ) -> "sa.Table":
        """
        Create a temporary table for storing custom signals generated by a UDF.
        SQLite TEMPORARY tables cannot be directly used as they are process-specific,
        and UDFs are run in other processes when run in parallel.
        """
        tbl = sa.Table(
            name,
            sa.MetaData(),
            sa.Column("id", Int, primary_key=True),
            *custom_columns,
        )
        q = CreateTable(
            tbl,
            if_not_exists=True,
        )
        self.ddb.execute(q)
        return tbl

    def cleanup_temp_tables(self, names: Iterable[str]) -> None:
        """
        Drop tables created temporarily when processing datasets.

        This should be implemented even if temporary tables are used to
        ensure that they are cleaned up as soon as they are no longer
        needed. When running the same `DatasetQuery` multiple times we
        may use the same temporary table names.
        """
        for name in names:
            self.ddb.execute(DropTable(Table(name, self.ddb.metadata), if_exists=True))
            # some temp tables can have related id generator
            self.id_generator_delete_uri(name)

    #
    # Signals
    #
    @abstractmethod
    def create_signals_table(self) -> SignalsTable:
        """
        Create an empty signals table for storing signals entries.
        Signals columns will be added gradually as they are encountered during
        data traversal
        """

    @abstractmethod
    def extend_index_with_signals(self, index: NodeTable, signals: SignalsTable):
        """Extend a nodes table with a signals table."""

    def subtract_query(
        self,
        source_query: sa.sql.selectable.Select,
        target_query: sa.sql.selectable.Select,
    ) -> sa.sql.selectable.Select:
        sq = source_query.alias("source_query")
        tq = target_query.alias("target_query")

        source_target_join = sa.join(
            sq,
            tq,
            (sq.c.source == tq.c.source)
            & (sq.c.parent == tq.c.parent)
            & (sq.c.name == tq.c.name),
            isouter=True,
        )

        return (
            select(sq.c)
            .select_from(source_target_join)
            .where((tq.c.name == None) | (tq.c.name == ""))  # noqa: E711
        )

    def changed_query(
        self,
        source_query: sa.sql.selectable.Select,
        target_query: sa.sql.selectable.Select,
    ) -> sa.sql.selectable.Select:
        sq = source_query.alias("source_query")
        tq = target_query.alias("target_query")

        source_target_join = sa.join(
            sq,
            tq,
            (sq.c.source == tq.c.source)
            & (sq.c.parent == tq.c.parent)
            & (sq.c.name == tq.c.name),
        )

        return (
            select(sq.c)
            .select_from(source_target_join)
            .where(
                (sq.c.last_modified > tq.c.last_modified)
                & (sq.c.is_latest == true())
                & (tq.c.is_latest == true())
            )
        )

    #
    # Dataset dependencies
    #
    @abstractmethod
    def insert_dataset_dependency(self, data: Dict[str, Any]) -> None:
        """Method for inserting dependencies"""

    def add_dependency(
        self,
        dependency: DatasetDependency,
        source_dataset_name: str,
        source_dataset_version: Optional[int] = None,
    ) -> None:
        if dependency.is_dataset:
            self.add_dataset_dependency(
                source_dataset_name,
                dependency.name,
                source_dataset_version,
                int(dependency.version) if dependency.version else None,
            )
        else:
            self.add_storage_dependency(
                source_dataset_name,
                StorageURI(dependency.name),
                dependency.version,
                source_dataset_version,
            )

    def add_storage_dependency(
        self,
        source_dataset_name: str,
        storage_uri: StorageURI,
        storage_timestamp_str: Optional[str] = None,
        source_dataset_version: Optional[int] = None,
    ) -> None:
        source_dataset = self.get_dataset(source_dataset_name)
        storage = self.get_storage(storage_uri)

        self.insert_dataset_dependency(
            {
                "source_dataset_id": source_dataset.id,
                "source_dataset_version_id": (
                    source_dataset.get_version(source_dataset_version).id
                    if source_dataset_version
                    else None
                ),
                "bucket_id": storage.id,
                "bucket_version": storage_timestamp_str,
            }
        )

    def add_dataset_dependency(
        self,
        source_dataset_name: str,
        dataset_name: str,
        source_dataset_version: Optional[int] = None,
        dataset_version: Optional[int] = None,
    ):
        source_dataset = self.get_dataset(source_dataset_name)
        dataset = self.get_dataset(dataset_name)

        self.insert_dataset_dependency(
            {
                "source_dataset_id": source_dataset.id,
                "source_dataset_version_id": (
                    source_dataset.get_version(source_dataset_version).id
                    if source_dataset_version
                    else None
                ),
                "dataset_id": dataset.id,
                "dataset_version_id": (
                    dataset.get_version(dataset_version).id if dataset_version else None
                ),
            }
        )

    def update_dataset_dependency_source(
        self,
        source_dataset: DatasetRecord,
        source_dataset_version: Optional[int] = None,
        new_source_dataset: Optional[DatasetRecord] = None,
        new_source_dataset_version: Optional[int] = None,
    ):
        dd = self.datasets_dependencies

        if not new_source_dataset:
            new_source_dataset = source_dataset

        q = self.datasets_dependencies_update().where(
            dd.c.source_dataset_id == source_dataset.id
        )
        if source_dataset_version:
            q = q.where(
                dd.c.source_dataset_version_id
                == source_dataset.get_version(source_dataset_version).id
            )

        data = {"source_dataset_id": new_source_dataset.id}
        if new_source_dataset_version:
            data["source_dataset_version_id"] = new_source_dataset.get_version(
                new_source_dataset_version
            ).id

        q = q.values(**data)
        self.mdb.execute(q)

    @abstractmethod
    def dataset_dependencies_select_columns(self) -> List["SchemaItem"]:
        """
        Returns a list of columns to select in a query for fetching dataset dependencies
        """

    def get_direct_dataset_dependencies(
        self, dataset: DatasetRecord, version: Optional[int] = None
    ) -> List[Optional[DatasetDependency]]:
        d = self.datasets
        dd = self.datasets_dependencies
        dv = self.datasets_versions
        s = self.storages

        select_cols = self.dataset_dependencies_select_columns()

        query = (
            self.datasets_dependencies_select(*select_cols)
            .where(dd.c.source_dataset_id == dataset.id)
            .select_from(
                dd.join(d, dd.c.dataset_id == d.c.id, isouter=True)
                .join(s, dd.c.bucket_id == s.c.id, isouter=True)
                .join(dv, dd.c.dataset_version_id == dv.c.id, isouter=True)
            )
        )
        if version:
            dataset_version = dataset.get_version(version)
            query = query.where(dd.c.source_dataset_version_id == dataset_version.id)

        return [self.dependency_class.parse(*r) for r in self.mdb.execute(query)]

    def remove_dataset_dependencies(
        self, dataset: DatasetRecord, version: Optional[int] = None
    ):
        """
        When we remove dataset, we need to clean up it's dependencies as well
        """
        dd = self.datasets_dependencies

        q = self.datasets_dependencies_delete().where(
            dd.c.source_dataset_id == dataset.id
        )

        if version:
            q = q.where(
                dd.c.source_dataset_version_id == dataset.get_version(version).id
            )

        self.mdb.execute(q)

    def remove_dataset_dependants(
        self, dataset: DatasetRecord, version: Optional[int] = None
    ):
        """
        When we remove dataset, we need to clear it's references in other dataset
        dependencies
        """
        dd = self.datasets_dependencies

        q = self.datasets_dependencies_update().where(dd.c.dataset_id == dataset.id)
        if version:
            q = q.where(dd.c.dataset_version_id == dataset.get_version(version).id)

        q = q.values(dataset_id=None, dataset_version_id=None)

        self.mdb.execute(q)
