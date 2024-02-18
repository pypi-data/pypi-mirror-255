import json
import logging
import os
import posixpath
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import wraps
from time import sleep
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

import sqlalchemy
from attrs import frozen
from sqlalchemy import MetaData, Table, UniqueConstraint, exists, select
from sqlalchemy.dialects import sqlite
from sqlalchemy.schema import Column as saColumn
from sqlalchemy.schema import CreateIndex, CreateTable, DropTable
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import bindparam, cast

import dql.sql.sqlite
from dql.data_storage.abstract import AbstractDataStorage, DatabaseEngine
from dql.data_storage.schema import (
    DATASET_CORE_COLUMN_NAMES,
    DefaultSchema,
    SignalsTable,
    convert_rows_custom_column_types,
)
from dql.dataset import DatasetRecord
from dql.dataset import Status as DatasetStatus
from dql.error import DQLError, InconsistentSignalType
from dql.sql.sqlite import create_user_defined_sql_functions, sqlite_dialect
from dql.sql.types import SQLType
from dql.storage import Status as StorageStatus
from dql.storage import Storage, StorageURI
from dql.utils import DQLDir

if TYPE_CHECKING:
    from sqlalchemy.schema import SchemaItem
    from sqlalchemy.sql.elements import ColumnClause, ColumnElement, TextClause
    from sqlalchemy.types import TypeEngine

    from dql.data_storage import schema

logger = logging.getLogger("dql")

RETRY_START_SEC = 0.01
RETRY_MAX_TIMES = 10
RETRY_FACTOR = 2
# special string to wrap around dataset name in a user query script stdout, which
# is run in a Python subprocess, so that we can find it later on after script is
# done since there is no other way to return results from it
PYTHON_SCRIPT_WRAPPER_CODE = "__ds__"

Column = Union[str, "ColumnClause[Any]", "TextClause"]

dql.sql.sqlite.setup()

quote_schema = sqlite_dialect.identifier_preparer.quote_schema
quote = sqlite_dialect.identifier_preparer.quote


def get_retry_sleep_sec(retry_count: int) -> int:
    return RETRY_START_SEC * (RETRY_FACTOR**retry_count)


def retry_sqlite_locks(func):
    # This retries the database modification in case of concurrent access
    @wraps(func)
    def wrapper(*args, **kwargs):
        exc = None
        for retry_count in range(RETRY_MAX_TIMES):
            try:
                return func(*args, **kwargs)
            except sqlite3.OperationalError as operror:
                exc = operror
                sleep(get_retry_sleep_sec(retry_count))
        raise exc

    return wrapper


@frozen
class SQLiteDatabaseEngine(DatabaseEngine):
    dialect = sqlite_dialect

    db: sqlite3.Connection

    @retry_sqlite_locks
    def execute(
        self,
        query,
        cursor: Optional[sqlite3.Cursor] = None,
        conn=None,
    ) -> sqlite3.Cursor:
        if cursor is not None:
            result = cursor.execute(*self.compile_to_args(query))
        elif conn is not None:
            result = conn.execute(*self.compile_to_args(query))
        else:
            result = self.db.execute(*self.compile_to_args(query))
        if isinstance(query, CreateTable) and query.element.indexes:
            for index in query.element.indexes:
                self.execute(CreateIndex(index, if_not_exists=True), cursor=cursor)
        return result

    @retry_sqlite_locks
    def executemany(
        self, query, params, cursor: Optional[sqlite3.Cursor] = None
    ) -> sqlite3.Cursor:
        if cursor:
            return cursor.executemany(self.compile(query).string, params)
        return self.db.executemany(self.compile(query).string, params)

    def execute_str(self, sql: str, parameters=None) -> sqlite3.Cursor:
        if parameters is None:
            return self.db.execute(sql)
        return self.db.execute(sql, parameters)

    def cursor(self, factory=None):
        if factory is None:
            return self.db.cursor()
        return self.db.cursor(factory)

    def close(self) -> None:
        self.db.close()

    @contextmanager
    def transaction(self):
        db = self.db
        with db:
            db.execute("begin")
            yield db

    def has_table(self, name: str) -> bool:
        """

        Return True if a table exists with the given name

        We cannot simply use `inspect(engine).has_table(name)` like the
        parent class does because that will return False for a table
        created during a pending transaction. Instead we check the
        sqlite_master table.
        """
        query = select(
            exists(
                select(1)
                .select_from(sqlalchemy.table("sqlite_master"))
                .where(
                    (sqlalchemy.column("type") == "table")
                    & (sqlalchemy.column("name") == name)
                )
            )
        )
        return bool(next(self.execute(query))[0])


class SQLiteDataStorage(AbstractDataStorage):
    """
    SQLite data storage uses SQLite3 for storing indexed data locally.
    This is currently used for the local cli.
    """

    # Cache for our defined column types to dialect specific TypeEngine relations
    _col_python_type: Dict[Type, Type] = {}

    def __init__(
        self,
        db_file: Optional[str] = None,
        uri: StorageURI = StorageURI(""),
        partial_id: Optional[int] = None,
    ):
        self.schema: "DefaultSchema" = DefaultSchema()
        super().__init__(uri, partial_id)
        self.db_file = db_file if db_file else DQLDir.find().db
        detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        self.listing_table_pattern = re.compile(
            f"^{self.BUCKET_TABLE_NAME_PREFIX}[a-z0-9-._]+_[0-9]+$"
        )
        # needed for dropping tables in correct order for tests because of
        # foreign keys
        self.default_table_names: List[str] = []

        try:
            if self.db_file == ":memory:":
                # Enable multithreaded usage of the same in-memory db
                db = sqlite3.connect(
                    "file::memory:?cache=shared", uri=True, detect_types=detect_types
                )
            else:
                db = sqlite3.connect(self.db_file, detect_types=detect_types)
            create_user_defined_sql_functions(db)
            engine = sqlalchemy.create_engine(
                "sqlite+pysqlite:///", creator=lambda: db, future=True
            )

            db.isolation_level = None  # Use autocommit mode
            db.execute("PRAGMA foreign_keys = ON")
            db.execute("PRAGMA cache_size = -102400")  # 100 MiB
            # Enable Write-Ahead Log Journaling
            db.execute("PRAGMA journal_mode = WAL")
            db.execute("PRAGMA synchronous = NORMAL")
            db.execute("PRAGMA case_sensitive_like = ON")
            if os.environ.get("DEBUG_SHOW_SQL_QUERIES"):
                db.set_trace_callback(print)

            db_eng = SQLiteDatabaseEngine(engine, MetaData(), db)
            self.ddb: SQLiteDatabaseEngine = db_eng
            self.mdb: SQLiteDatabaseEngine = db_eng

            self._init_storage_table()
            self._init_datasets_tables()

            self._reflect_tables(
                filter_tables=lambda t, _: bool(self.listing_table_pattern.match(t))
            )
        except RuntimeError:
            raise DQLError("Can't connect to SQLite DB")  # noqa: B904

    @staticmethod
    def buckets_constraints() -> List["SchemaItem"]:
        return [
            UniqueConstraint("uri"),
        ]

    @staticmethod
    def datasets_constraints() -> List["SchemaItem"]:
        return [
            UniqueConstraint("name"),
        ]

    @staticmethod
    def buckets_columns() -> List["SchemaItem"]:
        columns = super(SQLiteDataStorage, SQLiteDataStorage).buckets_columns()
        return columns + SQLiteDataStorage.buckets_constraints()

    @staticmethod
    def datasets_columns() -> List["SchemaItem"]:
        columns = super(SQLiteDataStorage, SQLiteDataStorage).datasets_columns()
        return columns + SQLiteDataStorage.datasets_constraints()

    def _reflect_tables(self, filter_tables=None):
        """
        Since some tables are prone to schema extension, meaning we can add
        additional columns to it, we should reflect changes in metadata
        to have the latest columns when dealing with those tables.
        If filter function is defined, it's used to filter out tables to reflect,
        otherwise all tables are reflected
        """
        self.ddb.metadata.reflect(
            bind=self.ddb.engine,
            extend_existing=True,
            only=filter_tables,
        )

    def _init_storage_table(self):
        """Initialize only tables related to storage, e.g s3"""
        self.mdb.execute(CreateTable(self.storages, if_not_exists=True))
        self.default_table_names.append(self.storages.name)

    def _init_datasets_tables(self) -> None:
        self.ddb.execute(CreateTable(self.datasets, if_not_exists=True))
        self.default_table_names.append(self.datasets.name)
        self.ddb.execute(CreateTable(self.datasets_versions, if_not_exists=True))
        self.default_table_names.append(self.datasets_versions.name)
        self.ddb.execute(CreateTable(self.datasets_dependencies, if_not_exists=True))
        self.default_table_names.append(self.datasets_dependencies.name)

    def init_id_generator(self, uri: str) -> None:
        if not uri:
            raise ValueError("uri for init_id_generator() cannot be empty")
        ig = self.id_generator
        self.mdb.execute(CreateTable(ig, if_not_exists=True))
        self.default_table_names.append(ig.name)
        self.mdb.execute(
            sqlite.insert(ig)
            .values(uri=f"partials:{uri}", last_id=0)
            .on_conflict_do_nothing()
        )

    def init_db(self, uri: StorageURI, partial_id: int) -> None:
        if not uri:
            raise ValueError("uri for init_db() cannot be empty")
        partials_table = self.partials_table(uri)
        nodes_table = self.nodes_table(uri, partial_id).table
        self.mdb.execute(CreateTable(partials_table, if_not_exists=True))
        self.ddb.execute(CreateTable(nodes_table, if_not_exists=True))

    def clone(
        self, uri: StorageURI = StorageURI(""), partial_id: Optional[int] = None
    ) -> "SQLiteDataStorage":
        if not uri:
            if partial_id is not None:
                raise ValueError("if partial_id is used, uri cannot be empty")
            if self.uri:
                uri = self.uri
                if self.partial_id:
                    partial_id = self.partial_id
        return SQLiteDataStorage(db_file=self.db_file, uri=uri, partial_id=partial_id)

    def clone_params(self) -> Tuple[Type[AbstractDataStorage], List, Dict[str, Any]]:
        """
        Returns the class, args, and kwargs needed to instantiate a cloned copy of this
        SQLiteDataStorage implementation, for use in separate processes or machines.
        """
        return (
            SQLiteDataStorage,
            [],
            {"db_file": self.db_file, "uri": self.uri, "partial_id": self.partial_id},
        )

    def close(self) -> None:
        """Closes any active database connections"""
        self.ddb.close()

    def _get_next_ids(self, uri: str, count: int) -> range:
        with self.ddb.transaction():
            # Transactions ensure no concurrency conflicts
            ig = self.id_generator
            self.mdb.execute(
                self.id_generator_update()
                .where(ig.c.uri == uri)
                .values(last_id=ig.c.last_id + count)
            )
            # TODO: RETURNING might be a better option,
            # but is only supported on SQLite 3.35.0 or newer
            last_id = self.mdb.execute(
                self.id_generator_select(ig.c.last_id).where(ig.c.uri == uri)
            ).fetchone()[0]

        return range(last_id - count + 1, last_id + 1)

    def create_dataset_rows_table(
        self,
        name: str,
        custom_columns: Sequence["sqlalchemy.Column"] = (),
        if_not_exists: bool = True,
    ) -> Table:
        table = self.schema.dataset_row_cls.new_table(
            name, custom_columns=custom_columns, metadata=self.ddb.metadata
        )
        q = CreateTable(table, if_not_exists=if_not_exists)
        self.ddb.execute(q)
        return table

    def dataset_rows_select(
        self, select_query: sqlalchemy.sql.selectable.Select, **kwargs
    ):
        rows = self.ddb.execute(select_query, **kwargs)
        yield from convert_rows_custom_column_types(
            select_query.columns, rows, sqlite_dialect
        )

    def get_dataset_sources(
        self, name: str, version: Optional[int]
    ) -> List[StorageURI]:
        dr = self.dataset_rows(name, version)
        query = dr.select(dr.c.source).distinct()
        cur = self.ddb.cursor()
        cur.row_factory = sqlite3.Row  # type: ignore[assignment]

        return [dict(row)["source"] for row in self.ddb.execute(query, cursor=cur)]

    def create_shadow_dataset(
        self,
        name: str,
        sources: Optional[List[str]] = None,
        query_script: str = "",
        create_rows: Optional[bool] = True,
        custom_columns: Sequence["sqlalchemy.Column"] = (),
    ) -> DatasetRecord:
        """Creates new shadow dataset if it doesn't exist yet"""
        custom_column_types = json.dumps(
            {
                c.name: c.type.to_dict()
                for c in self.dataset_row_cls.default_columns() + list(custom_columns)
                if isinstance(c.type, SQLType)
            }
        )

        with self.ddb.transaction():
            d = self.datasets
            self.mdb.execute(
                sqlite.insert(d)
                .values(
                    name=name,
                    shadow=True,
                    status=DatasetStatus.CREATED,
                    created_at=datetime.now(timezone.utc),
                    error_message="",
                    error_stack="",
                    script_output="",
                    sources="\n".join(sources) if sources else "",
                    query_script=query_script,
                    custom_column_types=custom_column_types,
                )
                .on_conflict_do_nothing(index_elements=["name"])
            )
            dataset = self.get_dataset(name)
            assert dataset.shadow

            # Reassign custom columns to the new table.
            custom_cols = [
                saColumn(c.name, c.type, nullable=c.nullable) for c in custom_columns
            ]
            if create_rows:
                table_name = self.dataset_table_name(dataset.name)
                self.create_dataset_rows_table(table_name, custom_cols)
                dataset = self.update_dataset_status(dataset, DatasetStatus.PENDING)

        return dataset  # type: ignore[return-value]

    def insert_into_shadow_dataset(
        self, name: str, uri: str, path: str, recursive=False
    ) -> None:
        dataset = self.get_dataset(name)
        assert dataset.shadow

        dst = self.dataset_rows(dataset.name)
        assert uri == self.uri
        src = self.nodes
        src_cols = {c.name for c in src.c}

        # Not including id
        dst_cols = {c.name for c in dst.c if c.name != "id"}
        cols = src_cols.intersection(dst_cols)
        transfer_fields = list(cols)
        select_query = self.nodes_dataset_query(
            transfer_fields, path=path, recursive=recursive, uri=uri
        )

        insert_query = dst.insert().from_select(transfer_fields, select_query)
        self.ddb.execute(insert_query)

    def _rename_table(self, old_name: str, new_name: str):
        comp_old_name = quote_schema(old_name)
        comp_new_name = quote_schema(new_name)
        self.ddb.execute_str(f"ALTER TABLE {comp_old_name} RENAME TO {comp_new_name}")

    def create_dataset_version(
        self,
        name: str,
        version: int,
        sources="",
        query_script="",
        create_rows_table=True,
        custom_column_types: Optional[Dict[str, Any]] = None,
    ) -> DatasetRecord:
        custom_column_types = custom_column_types or {}
        with self.ddb.transaction():
            dataset = self.get_dataset(name)
            dv = self.datasets_versions
            self.mdb.execute(
                sqlite.insert(dv)
                .values(
                    dataset_id=dataset.id,
                    version=version,
                    created_at=datetime.now(timezone.utc),
                    sources=sources,
                    query_script=query_script,
                    custom_column_types=json.dumps(custom_column_types),
                )
                .on_conflict_do_nothing(index_elements=["dataset_id", "version"])
            )

            if create_rows_table:
                table_name = self.dataset_table_name(dataset.name, version)
                self.create_dataset_rows_table(table_name)

        return self.get_dataset(name)

    def merge_dataset_rows(
        self,
        src: DatasetRecord,
        dst: DatasetRecord,
        src_version: Optional[int] = None,
        dst_version: Optional[int] = None,
    ) -> None:
        dst_empty = False

        if not self.ddb.has_table(self.dataset_table_name(src.name, src_version)):
            # source table doesn't exist, nothing to do
            return

        if not self.ddb.has_table(self.dataset_table_name(dst.name, dst_version)):
            # destination table doesn't exist, create it
            self.create_dataset_rows_table(self.dataset_table_name(dst.name))
            dst_empty = True

        src_dr = self.dataset_rows(src.name, src_version).table
        dst_dr = self.dataset_rows(dst.name, dst_version).table
        dst_dr_latest = self.dataset_rows(dst.name, dst.latest_version).table

        # Not including id
        merge_fields = [c for c in DATASET_CORE_COLUMN_NAMES if c != "id"]

        select_src = select(*(getattr(src_dr.c, f) for f in merge_fields))
        select_dst_latest = select(*(getattr(dst_dr_latest.c, f) for f in merge_fields))

        union_query = sqlalchemy.union(select_src, select_dst_latest)

        if dst_empty:
            # we don't need union, but just select from source to destination
            insert_query = sqlite.insert(dst_dr).from_select(merge_fields, select_src)
        else:
            insert_query = (
                sqlite.insert(dst_dr)
                .from_select(merge_fields, union_query)
                .prefix_with("OR IGNORE")
            )

        self.ddb.execute(insert_query)

    def copy_shadow_dataset_rows(self, src: DatasetRecord, dst: DatasetRecord) -> None:
        assert src.shadow
        assert dst.shadow

        if not self.ddb.has_table(self.dataset_table_name(src.name)):
            # source table doesn't exist, nothing to do
            return

        src_dr = self.dataset_rows(src.name).table

        if not self.ddb.has_table(self.dataset_table_name(dst.name)):
            # Destination table doesn't exist, create it
            custom_columns = [
                c
                for c in src_dr.c
                if c.name not in [c.name for c in DATASET_CORE_COLUMN_NAMES]
            ]
            self.create_dataset_rows_table(
                self.dataset_table_name(dst.name), custom_columns=custom_columns
            )

        dst_dr = self.dataset_rows(dst.name).table

        # Not including id
        src_fields = [c.name for c in src_dr.c if c.name != "id"]
        select_src = select(*(getattr(src_dr.c, f) for f in src_fields))
        insert_query = sqlite.insert(dst_dr).from_select(src_fields, select_src)

        self.ddb.execute(insert_query)

    def remove_shadow_dataset(self, dataset: DatasetRecord, drop_rows=True) -> None:
        with self.ddb.transaction():
            self.remove_dataset_dependencies(dataset)
            self.remove_dataset_dependants(dataset)

            d = self.datasets
            self.mdb.execute(self.datasets_delete().where(d.c.id == dataset.id))
            if drop_rows:
                table_name = self.dataset_table_name(dataset.name)
                self.ddb.execute(DropTable(Table(table_name, MetaData())))

    async def insert_node(self, entry: Dict[str, Any]) -> int:
        return (
            self.ddb.execute(
                self.nodes.insert().values(self._prepare_node(entry))
            ).lastrowid
            or 0
        )

    async def insert_nodes(self, entries: Iterable[Dict[str, Any]]) -> None:
        self.ddb.executemany(
            self.nodes.insert().values({f: bindparam(f) for f in self.node_fields[1:]}),
            map(self._prepare_node, entries),
        )

    def insert_rows(self, table: Table, rows: Iterable[Dict[str, Any]]) -> None:
        rows = list(rows)
        if not rows:
            return
        self.ddb.executemany(
            table.insert().values({f: bindparam(f) for f in rows[0].keys()}),
            rows,
        )

    def insert_dataset_rows(
        self, name: str, rows: Optional[Iterable[Dict[str, Any]]]
    ) -> None:
        def _prepare_row(row):
            if "id" in row:
                del row["id"]  # id will be implicitly created by SQLite
            row["parent_id"] = None  # parent_id is deprecated and not used any more
            return row

        if not rows:
            return

        dataset = self.get_dataset(name)
        assert dataset.shadow

        dst = self.dataset_rows(dataset.name)
        self.ddb.executemany(
            dst.insert().values(
                {f: bindparam(f) for f in [c.name for c in dst.c if c.name != "id"]}
            ),
            map(_prepare_row, rows),
        )

    def create_storage_if_not_registered(self, uri: StorageURI) -> None:
        s = self.storages
        self.ddb.execute(
            sqlite.insert(s)
            .values(
                uri=uri,
                status=StorageStatus.CREATED,
                error_message="",
                error_stack="",
            )
            .on_conflict_do_nothing()
        )

    def find_stale_storages(self):
        """
        Finds all pending storages for which the last inserted node has happened
        before STALE_HOURS_LIMIT hours, and marks it as STALE
        """
        with self.ddb.transaction():
            s = self.storages
            pending_storages = map(
                Storage._make,
                self.mdb.execute(
                    self.storages_select().where(s.c.status == StorageStatus.PENDING)
                ),
            )
            for storage in pending_storages:
                if storage.is_stale:
                    print(f"Marking storage {storage.uri} as stale")
                    self._mark_storage_stale(storage.id)

    def register_storage_for_indexing(
        self,
        uri: StorageURI,
        force_update: bool = True,
        prefix: str = "",
    ) -> Tuple[Storage, bool, bool, Optional[int]]:
        """
        Prepares storage for indexing operation.
        This method should be called before index operation is started
        It returns:
            - storage, prepared for indexing
            - boolean saying if indexing is needed
            - boolean saying if indexing is currently pending (running)
            - int or None - partial_id
        """
        # This ensures that all calls to the DB are in a single transaction
        # and commit is automatically called once this function returns
        with self.ddb.transaction():
            # Create storage if it doesn't exist
            self.create_storage_if_not_registered(uri)
            storage = self.get_storage(uri)

            if storage.status == StorageStatus.PENDING:
                return storage, False, True, None

            elif storage.is_expired or storage.status == StorageStatus.STALE:
                storage = self.mark_storage_pending(storage)
                return storage, True, False, None
            elif (
                storage.status in (StorageStatus.PARTIAL, StorageStatus.COMPLETE)
                and not force_update
            ):
                partial_id = self.get_valid_partial_id(uri, prefix, raise_exc=False)
                if partial_id is not None:
                    return storage, False, False, partial_id
                return storage, True, False, None
            else:
                storage = self.mark_storage_pending(storage)
                return storage, True, False, None

    def mark_storage_indexed(
        self,
        uri: str,
        status: int,
        ttl: int,
        end_time: Optional[datetime] = None,
        prefix: str = "",
        partial_id: int = 0,
        error_message: str = "",
        error_stack: str = "",
    ) -> None:
        if status == StorageStatus.PARTIAL and not prefix:
            raise AssertionError("Partial indexing requires a prefix")

        if end_time is None:
            end_time = datetime.now(timezone.utc)
        expires = Storage.get_expiration_time(end_time, ttl)

        with self.ddb.transaction():
            s = self.storages
            self.mdb.execute(
                self.storages_update()
                .where(s.c.uri == uri)
                .values(  # type: ignore [attr-defined]
                    timestamp=end_time,
                    expires=expires,
                    status=status,
                    last_inserted_at=end_time,
                    error_message=error_message,
                    error_stack=error_stack,
                )
            )

            if not self.current_bucket_table_name:
                # This only occurs in tests
                return

            if status in (StorageStatus.PARTIAL, StorageStatus.COMPLETE):
                p = self.partials
                dirprefix = posixpath.join(prefix, "")
                self.mdb.execute(
                    sqlite.insert(p).values(
                        path_str=dirprefix,
                        timestamp=end_time,
                        expires=expires,
                        partial_id=partial_id,
                    )
                )

    def mark_storage_not_indexed(self, uri: str) -> None:
        s = self.storages
        self.mdb.execute(self.storages_delete().where(s.c.uri == uri))

    def instr(self, source, target) -> "ColumnElement":
        return cast(func.instr(source, target), sqlalchemy.Boolean)

    def get_table(self, name: str) -> sqlalchemy.Table:
        # load table with latest schema to metadata
        self._reflect_tables(filter_tables=lambda t, _: t == name)
        return self.ddb.metadata.tables[name]

    def return_ds_hook(self, name: str) -> None:
        print(f"{PYTHON_SCRIPT_WRAPPER_CODE}{name}{PYTHON_SCRIPT_WRAPPER_CODE}")

    def python_type(self, col_type: Union["TypeEngine", "SQLType"]) -> Any:
        if isinstance(col_type, SQLType):
            # converting our defined column types to dialect specific TypeEngine
            col_type_cls = type(col_type)
            if col_type_cls not in self._col_python_type:
                self._col_python_type[col_type_cls] = col_type.type_engine(
                    sqlite_dialect
                )
            col_type = self._col_python_type[col_type_cls]

        return col_type.python_type

    def add_column(
        self, table: Table, col_name: str, col_type: Union["TypeEngine", "SQLType"]
    ):
        """Adds a column to a table"""
        # trying to find the same column in a table
        table_col = table.c.get(col_name, None)

        if isinstance(col_type, SQLType):
            # converting our defined column types to dialect specific TypeEngine
            col_type = col_type.type_engine(sqlite_dialect)

        if table_col is not None and table_col.type.python_type != col_type.python_type:
            raise InconsistentSignalType(
                f"Column {col_name} already exists with a type:"
                f" {table_col.type.python_type}"
                f", but trying to create it with different type: {col_type.python_type}"
            )
        if table_col is not None:
            # column with the same name and type already exist, nothing to do
            return

        table_name = quote_schema(table.name)
        col_name_comp = quote(col_name)
        col_type_comp = col_type.compile(dialect=sqlite_dialect)
        q = f"ALTER TABLE {table_name} ADD COLUMN {col_name_comp} {col_type_comp}"
        self.ddb.execute_str(q)

        # reload the table to self.ddb.metadata so the table object
        # self.ddb.metadata.tables[table.name] includes the new column
        self._reflect_tables(filter_tables=lambda t, _: t == table.name)

    def dataset_column_types(
        self, name: str, version=None, custom=False
    ) -> List[Dict[str, str]]:
        dr = self.dataset_rows(name, version)
        columns = dr.custom_columns if custom else dr.columns
        return [{"name": c.name, "type": c.type.python_type.__name__} for c in columns]

    #
    # Signals
    #

    def create_signals_table(self) -> SignalsTable:
        """
        Create an empty signals table for storing signals entries.
        """
        tbl_name = self.signals_table_name(self.uri)
        tbl = SignalsTable(tbl_name, [], self.ddb.metadata)
        q = CreateTable(tbl.table)
        self.ddb.execute(q)
        return tbl

    def extend_index_with_signals(self, index: "schema.Table", signals: SignalsTable):
        """
        Extend a nodes table with a signals table.
        This will result in the original index table being replaced
        with a table that is a join between the signals table and the
        index table (joining on the id column).
        """

        with self.ddb.transaction():
            # Create temporary table.
            join_tbl_name = "tmp_" + index.name

            signal_columns = [c for c in signals.table.c if c.name != "id"]

            join_tbl = self.schema.node_cls.new_table(
                join_tbl_name,
                [self.schema.node_cls.copy_signal_column(c) for c in signal_columns],
                self.ddb.metadata,
            )
            try:
                self.ddb.execute(CreateTable(join_tbl))

                # Query joining original index table and signals table.
                index_cols = {c.name for c in index.table.c}
                duplicate_signal_cols = {
                    c.name
                    for c in signals.table.c
                    if c.name in index_cols and c.name != "id"
                }
                select_cols = [
                    # columns from index table
                    *[c for c in index.table.c if c.name not in duplicate_signal_cols],
                    # coalesce columns already in index table
                    *[
                        func.coalesce(*cc).label(cc[0].name)
                        for cc in zip(
                            [index.table.c[col] for col in duplicate_signal_cols],
                            [signals.table.c[col] for col in duplicate_signal_cols],
                        )
                    ],
                    # columns from signals table
                    *[c for c in signal_columns if c.name not in duplicate_signal_cols],
                ]
                q = sqlalchemy.select(*select_cols).select_from(
                    index.table.outerjoin(
                        signals.table, index.c.id == signals.table.c.id
                    )
                )

                cols = [c.name for c in select_cols]

                # Write results of query to the new index table.
                self.ddb.execute(sqlalchemy.insert(join_tbl).from_select(cols, q))
                # Replace original table with extended one.
                self.ddb.execute(DropTable(index.table))
                self._rename_table(join_tbl_name, index.name)
            finally:
                self.ddb.execute(DropTable(join_tbl, if_exists=True))

    #
    # Dataset dependencies
    #
    def dataset_dependencies_select_columns(self) -> List["SchemaItem"]:
        return [
            self.datasets_dependencies.c.id,
            self.datasets_dependencies.c.dataset_id,
            self.datasets_dependencies.c.dataset_version_id,
            self.datasets_dependencies.c.bucket_id,
            self.datasets_dependencies.c.bucket_version,
            self.datasets.c.name,
            self.datasets.c.created_at,
            self.datasets_versions.c.version,
            self.datasets_versions.c.created_at,
            self.storages.c.uri,
        ]

    def insert_dataset_dependency(self, data: Dict[str, Any]) -> None:
        return self.mdb.execute(
            sqlite.insert(self.datasets_dependencies).values(**data)
        )
