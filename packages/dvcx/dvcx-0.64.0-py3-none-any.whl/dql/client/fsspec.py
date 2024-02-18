import asyncio
import json
import logging
import multiprocessing
import os
import posixpath
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from shutil import copy2
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    ClassVar,
    Dict,
    Iterator,
    NamedTuple,
    Optional,
    Tuple,
    Type,
)

from botocore.exceptions import ClientError
from dvc_objects.fs.system import reflink
from fsspec.asyn import get_loop
from tqdm import tqdm

from dql.cache import DQLCache, UniqueId
from dql.client.fileslice import FileSlice
from dql.error import ClientError as DQLClientError
from dql.nodes_fetcher import NodesFetcher
from dql.nodes_thread_pool import NodeChunk
from dql.storage import StorageURI

if TYPE_CHECKING:
    from fsspec.spec import AbstractFileSystem

    from dql.data_storage import AbstractDataStorage

logger = logging.getLogger("dql")

FETCH_WORKERS = 100
DELIMITER = "/"  # Path delimiter.
TIME_ZERO = datetime.fromtimestamp(0, tz=timezone.utc)


class Bucket(NamedTuple):
    name: str
    uri: StorageURI
    created: Optional[datetime]


class Client(ABC):
    MAX_THREADS = multiprocessing.cpu_count()
    FS_CLASS: ClassVar[Type["AbstractFileSystem"]]
    PREFIX: ClassVar[str]
    protocol: ClassVar[str]

    def __init__(self, name: str, fs: "AbstractFileSystem", cache: DQLCache) -> None:
        self.name = name
        self.fs = fs
        self.cache = cache

    @staticmethod
    def get_implementation(url: str) -> Type["Client"]:
        from .azure import AzureClient
        from .gcs import GCSClient
        from .local import FileClient
        from .s3 import ClientS3

        if url.lower().startswith(ClientS3.PREFIX):
            return ClientS3
        elif url.lower().startswith(GCSClient.PREFIX):
            return GCSClient
        elif url.lower().startswith(AzureClient.PREFIX):
            return AzureClient
        elif url.lower().startswith(FileClient.PREFIX):
            return FileClient
        raise RuntimeError(f"Unsupported data source format '{url}'")

    @staticmethod
    def parse_url(
        source: str,
        data_storage: "AbstractDataStorage",
        cache: DQLCache,
        **kwargs,
    ) -> Tuple["Client", str]:
        cls = Client.get_implementation(source)
        storage_url, rel_path = cls.split_url(source, data_storage)
        client = cls.from_name(storage_url, data_storage, cache, kwargs)
        return client, rel_path

    @classmethod
    def create_fs(cls, **kwargs) -> "AbstractFileSystem":
        kwargs.setdefault("version_aware", True)
        fs = cls.FS_CLASS(**kwargs)
        fs.invalidate_cache()
        return fs

    @classmethod
    def from_name(
        cls,
        name: str,
        data_storage: "AbstractDataStorage",
        cache: DQLCache,
        kwargs: Dict[str, Any],
    ) -> "Client":
        return cls(name, cls.create_fs(**kwargs), cache)

    @classmethod
    def from_source(
        cls,
        uri: StorageURI,
        data_storage: "AbstractDataStorage",
        cache: DQLCache,
        **kwargs,
    ) -> "Client":
        fs = cls.create_fs(**kwargs)
        return cls(fs._strip_protocol(uri), fs, cache)

    @classmethod
    def ls_buckets(cls, **kwargs) -> Iterator[Bucket]:
        for entry in cls.create_fs(**kwargs).ls(cls.PREFIX, detail=True):
            name = entry["name"].rstrip("/")
            yield Bucket(
                name=name,
                uri=StorageURI(f"{cls.PREFIX}{name}"),
                created=entry.get("CreationDate"),
            )

    @classmethod
    def is_root_url(cls, url) -> bool:
        return url == cls.PREFIX

    @property
    def uri(self) -> StorageURI:
        return StorageURI(f"{self.PREFIX}{self.name}")

    @classmethod
    def split_url(
        cls, url: str, data_storage: "AbstractDataStorage"
    ) -> Tuple[str, str]:
        fill_path = url[len(cls.PREFIX) :]
        path_split = fill_path.split("/", 1)
        bucket = path_split[0]
        path = path_split[1] if len(path_split) > 1 else ""
        return bucket, path

    def url(self, path: str, expires: int = 3600, **kwargs) -> str:
        return self.fs.sign(self.get_full_path(path), expiration=expires, **kwargs)

    def get_current_etag(self, uid):
        info = self.fs.info(self.get_full_path(uid.path))
        return self._dict_from_info(info, "")["etag"]

    async def fetch(self, listing, start_prefix="", results=None):
        data_storage = listing.data_storage.clone()
        if start_prefix:
            start_prefix = start_prefix.rstrip("/")
            await listing.insert_dir(
                posixpath.basename(start_prefix),
                TIME_ZERO,
                posixpath.dirname(start_prefix),
                data_storage=data_storage,
            )
        else:
            await listing.insert_root(data_storage=data_storage)

        progress_bar = tqdm(desc=f"Listing {self.uri}", unit=" objects")
        total_count = 0
        loop = get_loop()

        queue = asyncio.Queue()
        queue.put_nowait(start_prefix)

        async def worker(queue, data_storage):
            nonlocal total_count
            while True:
                prefix = await queue.get()
                try:
                    subdirs, found_count = await self._fetch_dir(
                        prefix,
                        progress_bar,
                        listing,
                        data_storage,
                    )
                    total_count += found_count
                    for subdir in subdirs:
                        queue.put_nowait(subdir)
                finally:
                    queue.task_done()

        try:
            workers = []
            for _ in range(FETCH_WORKERS):
                workers.append(loop.create_task(worker(queue, data_storage)))

            # Wait for all fetch tasks to complete
            await queue.join()
            # Stop the workers
            for worker in workers:
                worker.cancel()
            await asyncio.gather(*workers)
        except ClientError as exc:
            raise DQLClientError(
                exc.response.get("Error", {}).get("Message") or exc,
                exc.response.get("Error", {}).get("Code"),
            ) from exc
        finally:
            data_storage.insert_nodes_done()
            # This ensures the progress bar is closed before any exceptions are raised
            progress_bar.close()
            if isinstance(results, dict):
                results["total_count"] = total_count

    async def _fetch_dir(self, prefix, pbar, listing, data_storage):
        path = f"{self.name}/{prefix}"
        infos = await self.ls_dir(path)
        files = []
        subdirs = set()
        for info in infos:
            full_path = info["name"]
            subprefix = self.rel_path(full_path)
            if info["type"] == "directory":
                name = full_path.split(DELIMITER)[-1]
                await listing.insert_dir(
                    name,
                    TIME_ZERO,
                    prefix,
                    data_storage=data_storage,
                )
                subdirs.add(subprefix)
            else:
                files.append(self._dict_from_info(info, prefix))
        if files:
            await data_storage.insert_nodes(files)
            await data_storage.update_last_inserted_at()
        found_count = len(subdirs) + len(files)
        pbar.update(found_count)
        return subdirs, found_count

    async def ls_dir(self, path):
        return await self.fs._ls(path, detail=True, versions=True)

    def rel_path(self, path):
        return self.fs.split_path(path)[1]

    def get_full_path(self, rel_path: str) -> str:
        return f"{self.PREFIX}{self.name}/{rel_path}"

    @abstractmethod
    def _dict_from_info(self, v, parent):
        ...

    def fetch_nodes(
        self,
        nodes,
        shared_progress_bar=None,
    ) -> None:
        fetcher = NodesFetcher(self, self.MAX_THREADS, self.cache)
        chunk_gen = NodeChunk(self.cache, self.uri, nodes)
        fetcher.run(chunk_gen, shared_progress_bar)

    def iter_object_chunks(self, bucket, path, version=None):
        with self.fs.open(f"{bucket}/{path}", version_id=version) as f:
            chunk = f.read()
            while chunk:
                yield chunk
                chunk = f.read()

    def instantiate_object(
        self,
        uid: UniqueId,
        dst: str,
        progress_bar: tqdm,
        force: bool = False,
    ) -> None:
        if os.path.exists(dst):
            if force:
                os.remove(dst)
            else:
                progress_bar.close()
                raise FileExistsError(f"Path {dst} already exists")
        self.do_instantiate_object(uid, dst)

    def do_instantiate_object(self, uid: "UniqueId", dst: str) -> None:
        src = self.cache.get_path(uid)
        assert src is not None

        try:
            reflink(src, dst)
        except OSError:
            # Default to copy if reflinks are not supported
            copy2(src, dst)

    def open_object(self, uid: UniqueId, use_cache: bool = True) -> BinaryIO:
        """Open a file, including files in tar archives."""
        if uid.vtype == "tar":
            return self._open_tar(uid, use_cache=True)
        else:  # noqa: PLR5501
            if use_cache and (cache_path := self.cache.get_path(uid)):
                return open(cache_path, mode="rb")
            else:
                return self.open(uid.path)

    def _open_tar(self, uid: UniqueId, use_cache: bool = True):
        assert uid.location is not None
        loc_stack = json.loads(uid.location)
        if len(loc_stack) > 1:
            raise NotImplementedError("Nested v-objects are not supported yet.")
        obj_location = loc_stack[0]
        tar_path = posixpath.split(obj_location["parent"])
        parent_etag = obj_location["etag"]
        offset = obj_location["offset"]
        size = obj_location["size"]
        parent_uid = UniqueId(
            uid.storage,
            *tar_path,
            etag=parent_etag,
            size=-1,
            vtype="",
            location=None,
        )
        f = self.open_object(parent_uid, use_cache=use_cache)
        return FileSlice(f, offset, size, posixpath.basename(uid.path))

    def open(self, path: str, mode="rb") -> Any:
        return self.fs.open(self.get_full_path(path), mode=mode)

    def download(self, uid: UniqueId, *, callback=None) -> None:
        if self.cache.contains(uid):
            # Already in cache, so there's nothing to do.
            return
        self.put_in_cache(uid, callback=callback)

    def put_in_cache(self, uid: UniqueId, *, callback=None) -> None:
        if uid.vtype == "tar":
            self._download_from_tar(uid, callback=callback)
            return
        etag = self.get_current_etag(uid)
        if uid.etag != etag:
            raise FileNotFoundError(
                f"Invalid etag for {uid.storage}/{uid.path}: "
                f"expected {uid.etag}, got {etag}"
            )
        self.cache.download(uid, self.fs, callback=callback)

    def _download_from_tar(self, uid, *, callback=None):
        with self._open_tar(uid, use_cache=False) as f:
            contents = f.read()
        self.cache.store_data(uid, contents, callback=callback)
