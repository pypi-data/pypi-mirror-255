from datetime import datetime
from typing import Any, Dict, List, Optional

import attrs

from dql.cache import UniqueId
from dql.storage import StorageURI
from dql.utils import time_to_str


class DirType:
    FILE = 0
    DIR = 1
    TAR_ARCHIVE = 5


class DirTypeGroup:
    """
    Groups of DirTypes for selecting storage nodes or dataset entries.

    When filtering with FILE and DIR together or alternatively when
    using SUBOBJ_FILE and SUBOBJ_DIR together, we achieve a
    filesystem-compatible view of a storage location. Such a view
    avoids path conflicts and could be downloaded as a directory tree.

    FILE, DIR
      The respective types which appear on the indexed filesystem or
      object store as a file or directory.

    SUBOBJ_FILE, SUBOBJ_DIR
      The respective types that we want to consider to be a file or
      directory when including subobjects which are generated from other
      files. In this case, we treat tar archives as directories so tar
      subobjects (TAR_FILE) can be viewed under the directory tree of
      the parent tar archive.
    """

    FILE = (DirType.FILE, DirType.TAR_ARCHIVE)
    DIR = (DirType.DIR,)
    SUBOBJ_FILE = (DirType.FILE,)
    SUBOBJ_DIR = (DirType.DIR, DirType.TAR_ARCHIVE)


@attrs.define
class Node:
    id: int = 0
    vtype: str = ""
    dir_type: Optional[int] = None
    parent_id: Optional[int] = None
    parent: str = ""
    name: str = ""
    checksum: str = ""
    etag: str = ""
    version: Optional[str] = None
    is_latest: bool = True
    last_modified: Optional[datetime] = None
    size: int = 0
    owner_name: str = ""
    owner_id: str = ""
    anno: Optional[str] = None
    random: int = -1
    location: Optional[str] = None
    source: StorageURI = StorageURI("")

    @property
    def path(self) -> str:
        return f"{self.parent}/{self.name}" if self.parent else self.name

    @property
    def is_dir(self) -> bool:
        return self.dir_type == DirType.DIR

    @property
    def is_container(self) -> bool:
        return self.dir_type in DirTypeGroup.SUBOBJ_DIR

    @property
    def is_downloadable(self) -> bool:
        return bool(not self.is_dir and self.name)

    def sql_schema(self):
        return ",".join(["?"] * len(self))

    def append_to_file(self, fd, path: str):
        fd.write(f"- name: {path}\n")
        fd.write(f"  etag: {self.etag}\n")
        version = self.version
        if version:
            fd.write(f"  version: {self.version}\n")
        fd.write(f"  last_modified: '{time_to_str(self.last_modified)}'\n")
        size = self.size
        fd.write(f"  size: {self.size}\n")
        return size

    def get_metafile_data(self, path: str):
        data: Dict[str, Any] = {
            "name": path,
            "etag": self.etag,
        }
        version = self.version
        if version:
            data["version"] = version
        data["last_modified"] = time_to_str(self.last_modified)
        data["size"] = self.size
        return data

    @property
    def full_path(self) -> str:
        if self.is_dir and self.path:
            return self.path + "/"
        return self.path

    def as_uid(self, storage: Optional[StorageURI] = None):
        if storage is None:
            storage = self.source
        return UniqueId(
            storage,
            self.parent,
            self.name,
            self.etag,
            self.size,
            self.vtype,
            self.location,
        )


def get_path(parent: str, name: str):
    return f"{parent}/{name}" if parent else name


@attrs.define
class NodeWithPath:
    n: Node
    path: List[str] = []

    def append_to_file(self, fd):
        return self.n.append_to_file(fd, "/".join(self.path))

    def get_metafile_data(self):
        return self.n.get_metafile_data("/".join(self.path))

    @property
    def full_path(self) -> str:
        path = "/".join(self.path)
        if self.n.is_dir and path:
            path += "/"
        return path


TIME_FMT = "%Y-%m-%d %H:%M"


def long_line_str(name: str, timestamp: Optional[datetime], owner: str) -> str:
    if timestamp is None:
        time = "-"
    else:
        time = timestamp.strftime(TIME_FMT)
    return f"{owner: <19} {time: <19} {name}"
