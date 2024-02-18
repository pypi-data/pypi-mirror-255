import os
import posixpath
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from fsspec.implementations.local import LocalFileSystem

from dql.error import StorageNotFoundError

from .fsspec import Client


class FileClient(Client):
    FS_CLASS = LocalFileSystem
    PREFIX = "file://"
    protocol = "file"

    def __init__(
        self, name: str, fs: LocalFileSystem, cache, use_symlinks: bool = False
    ) -> None:
        super().__init__(name, fs, cache)
        self.use_symlinks = use_symlinks

    def url(self, path: str, expires: int = 3600, **kwargs) -> str:
        raise TypeError("Signed urls are not implemented for local file system")

    @classmethod
    def ls_buckets(cls, **kwargs):
        return []

    @classmethod
    def split_url(cls, url: str, data_storage) -> Tuple[str, str]:
        def _storage_exists(uri: str) -> bool:
            try:
                data_storage.get_storage(uri)
            except StorageNotFoundError:
                return False
            return True

        # lowercasing scheme just in case it's uppercase
        scheme, rest = url.split(":", 1)
        url = f"{scheme.lower()}:{rest}"
        if _storage_exists(url):
            return LocalFileSystem._strip_protocol(url), ""
        for pos in range(len(url) - 1, len(cls.PREFIX), -1):
            if url[pos] == "/" and _storage_exists(url[:pos]):
                return LocalFileSystem._strip_protocol(url[:pos]), url[pos + 1 :]
        raise RuntimeError(f"Invalid file path '{url}'")

    @classmethod
    def from_name(cls, name: str, data_storage, cache, kwargs) -> "FileClient":
        use_symlinks = kwargs.pop("use_symlinks", False)
        return cls(name, cls.create_fs(**kwargs), cache, use_symlinks=use_symlinks)

    @classmethod
    def from_source(
        cls, uri: str, data_storage, cache, use_symlinks: bool = False, **kwargs
    ) -> "FileClient":
        fs = cls.create_fs(**kwargs)
        return cls(
            fs._strip_protocol(uri),
            cls.create_fs(**kwargs),
            cache,
            use_symlinks=use_symlinks,
        )

    async def ls_dir(self, path):
        return self.fs.ls(path, detail=True)

    def rel_path(self, path):
        return posixpath.relpath(path, self.name)

    @property
    def uri(self):
        return Path(self.name).as_uri()

    def get_full_path(self, rel_path):
        full_path = Path(self.name, rel_path).as_uri()
        if rel_path.endswith("/") or not rel_path:
            full_path += "/"
        return full_path

    def _dict_from_info(self, v, parent):
        name = posixpath.basename(v["name"])
        return {
            "dir_id": None,
            "parent": parent,
            "name": name,
            "checksum": "",
            "etag": v["mtime"].hex(),
            "version": "",
            "is_latest": True,
            "last_modified": datetime.fromtimestamp(v["mtime"], timezone.utc),
            "size": v.get("size", ""),
            "owner_name": "",
            "owner_id": "",
            "anno": None,
        }

    def fetch_nodes(
        self,
        nodes,
        shared_progress_bar=None,
    ) -> None:
        if not self.use_symlinks:
            super().fetch_nodes(nodes, shared_progress_bar)

    def do_instantiate_object(self, uid, dst):
        if self.use_symlinks:
            os.symlink(Path(self.name, uid.path), dst)
        else:
            super().do_instantiate_object(uid, dst)
