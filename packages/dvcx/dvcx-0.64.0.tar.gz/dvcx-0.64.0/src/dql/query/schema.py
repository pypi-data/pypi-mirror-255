import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from fnmatch import fnmatch
from random import getrandbits
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple, Union

import attrs
from sqlalchemy.sql.elements import ColumnClause
from sqlalchemy.sql.visitors import TraversibleType

from dql.data_storage.abstract import RANDOM_BITS
from dql.sql.types import JSON, Boolean, DateTime, Int, String

if TYPE_CHECKING:
    from dql.catalog import Catalog
    from dql.dataset import DatasetRow as Row


class ColumnMeta(TraversibleType):
    def __getattr__(cls, name: str):  # noqa: N805
        return cls(name)


class Column(ColumnClause, metaclass=ColumnMeta):
    inherit_cache: Optional[bool] = True

    def __init__(self, text, type_=None, is_literal=False, _selectable=None):
        self.name = text
        super().__init__(
            text, type_=type_, is_literal=is_literal, _selectable=_selectable
        )

    def glob(self, glob_str):
        return self.op("GLOB")(glob_str)


class UDFParameter(ABC):
    @abstractmethod
    def get_value(self, catalog: "Catalog", row: "Row", **kwargs) -> Any:
        ...


@attrs.define(slots=False)
class ColumnParameter(UDFParameter):
    name: str

    def get_value(self, catalog, row, **kwargs):
        return row[self.name]


@attrs.define(slots=False)
class Object(UDFParameter):
    """
    Object is used as a placeholder parameter to indicate the actual stored object
    being passed as a parameter to the UDF.
    """

    reader: Callable

    def get_value(
        self, catalog: "Catalog", row: "Row", *, cache: bool = False, **kwargs
    ) -> Any:
        client = catalog.get_client(row.source)
        uid = row.as_uid()
        if cache:
            client.download(uid)
        with client.open_object(uid, use_cache=cache) as f:
            return self.reader(f)


@attrs.define(slots=False)
class Stream(UDFParameter):
    """
    A Stream() parameter receives a binary stream over the object contents.
    """

    def get_value(self, catalog, row, *, cache=False, **kwargs) -> Any:
        client = catalog.get_client(row.source)
        uid = row.as_uid()
        if cache:
            client.download(uid)
        return client.open_object(uid, use_cache=cache)


@attrs.define(slots=False)
class LocalFilename(UDFParameter):
    """
    Placeholder parameter representing the local path to a cached copy of the object.

    If glob is None, then all files will be returned. If glob is specified,
    then only files matching the glob will be returned,
    otherwise None will be returned.
    """

    glob: Optional[str] = None

    def get_value(self, catalog: "Catalog", row: "Row", **kwargs) -> Optional[str]:
        if self.glob:
            if not fnmatch(row.name, self.glob):  # type: ignore[type-var]
                # If the glob pattern is specified and the row filename
                # does not match it, then return None
                return None
        client = catalog.get_client(row.source)
        uid = row.as_uid()
        client.download(uid)
        return client.cache.get_path(uid)


UDFParamSpec = Union[str, Column, UDFParameter]


def normalize_param(param: UDFParamSpec) -> UDFParameter:
    if isinstance(param, str):
        return ColumnParameter(param)
    elif isinstance(param, Column):
        return ColumnParameter(param.name)
    elif isinstance(param, UDFParameter):
        return param
    else:
        raise TypeError("Invalid UDF parameter: {param}")


class DatasetRow:
    schema = {
        "source": String,
        "parent": String,
        "name": String,
        "size": Int,
        "location": JSON,
        "vtype": String,
        "dir_type": Int,
        "owner_name": String,
        "owner_id": String,
        "is_latest": Boolean,
        "last_modified": DateTime,
        "version": String,
        "etag": String,
        "checksum": String,
        "anno": JSON,
        # system column
        "random": Int,
    }

    @staticmethod
    def create(
        name: str,
        source: str = "",
        parent: str = "",
        size: int = 0,
        location: Optional[Dict[str, Any]] = None,
        vtype: str = "",
        dir_type: int = 0,
        owner_name: str = "",
        owner_id: str = "",
        is_latest: bool = True,
        last_modified: Optional[datetime] = None,
        version: str = "",
        etag: str = "",
        checksum: str = "",
        anno: Optional[Dict[str, Any]] = None,
    ) -> Tuple[
        str,
        str,
        str,
        int,
        Optional[str],
        str,
        int,
        str,
        str,
        bool,
        datetime,
        str,
        str,
        str,
        Optional[str],
        int,
    ]:
        if location:
            location = json.dumps([location])  # type: ignore [assignment]

        if anno:
            anno = json.dumps(anno)  # type: ignore [assignment]

        last_modified = last_modified or datetime.now(timezone.utc)

        random = getrandbits(RANDOM_BITS)

        return (  # type: ignore [return-value]
            source,
            parent,
            name,
            size,
            location,
            vtype,
            dir_type,
            owner_name,
            owner_id,
            is_latest,
            last_modified,
            version,
            etag,
            checksum,
            anno,
            random,
        )

    @staticmethod
    def extend(**columns):
        cols = {**DatasetRow.schema}
        cols.update(columns)
        return cols


C = Column
