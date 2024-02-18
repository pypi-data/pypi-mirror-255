import io
import json
import os
import pickle
import uuid
from datetime import datetime, timedelta, timezone
from json import dumps
from random import getrandbits
from textwrap import dedent
from unittest.mock import ANY

import numpy as np
import pytest
import sqlalchemy
from dateutil.parser import isoparse
from sqlalchemy import tuple_

from dql.catalog import indexer_formats
from dql.data_storage.abstract import RANDOM_BITS
from dql.data_storage.schema import DATASET_CORE_COLUMN_NAMES
from dql.dataset import DatasetDependencyType
from dql.dataset import Status as DatasetStatus
from dql.node import Node
from dql.query import C, DatasetQuery, DatasetRow, LocalFilename, Object, Stream, udf
from dql.query.builtins import checksum, index_tar
from dql.sql import functions
from dql.sql.functions.array import cosine_distance, euclidean_distance
from dql.sql.types import (
    JSON,
    Array,
    Binary,
    Boolean,
    DateTime,
    Float,
    Float32,
    Float64,
    Int,
    Int32,
    Int64,
    SQLType,
    String,
)

from ..data import ENTRIES
from ..utils import (
    DEFAULT_TREE,
    NUM_TREE,
    SIMPLE_DS_QUERY_RECORDS,
    TARRED_TREE,
    WEBFORMAT_TREE,
    adjusted_float_diff,
    dataset_dependency_asdict,
    insert_nodes,
    text_embedding,
)


@pytest.fixture
def dogs_cats_shadow_dataset(
    listed_bucket, cloud_test_catalog, dogs_shadow_dataset, cats_shadow_dataset
):
    shadow_dataset_name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog
    (
        DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
        .union(DatasetQuery(name=cats_shadow_dataset.name, catalog=catalog))
        .save(shadow_dataset_name)
    )
    return catalog.data_storage.get_dataset(shadow_dataset_name)


@pytest.mark.parametrize("from_path", [True, False])
@pytest.mark.parametrize("save", [True, False])
@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_filter(cloud_test_catalog, save, from_path):
    catalog = cloud_test_catalog.catalog
    # ensure we can select a subset of a bucket properly
    path = f"{cloud_test_catalog.src_uri}/cats"
    if from_path:
        ds = DatasetQuery(path=path, catalog=catalog)
    else:
        sources = [path]
        globs = [s.rstrip("/") + "/*" for s in sources]
        catalog.index(sources)
        catalog.create_shadow_dataset("animals", globs, recursive=True)
        ds = DatasetQuery(name="animals", catalog=catalog)
    q = ds.filter(C.size < 13).filter(C.parent.glob("cats*") | (C.size < 4))
    if save:
        ds_name = "animals_cats"
        q.save(ds_name)
        q = DatasetQuery(name=ds_name, catalog=catalog)
        dataset_record = catalog.get_dataset(ds_name)
        assert dataset_record.status == DatasetStatus.COMPLETE
    result = q.results()
    count = q.count()
    assert len(result) == 2
    assert count == 2


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_select(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    path = cloud_test_catalog.src_uri
    ds = DatasetQuery(path=path, catalog=catalog)
    q = (
        ds.order_by(C.size.desc(), C.name)
        .limit(6)
        .select(C.name, size10x=C.size * 10, size100x=C.size * 100)
    )
    result = q.results()
    assert result == [
        ("description", 130, 1300),
        ("cat1", 40, 400),
        ("cat2", 40, 400),
        ("dog1", 40, 400),
        ("dog3", 40, 400),
        ("dog4", 40, 400),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_select_missing_column(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    path = cloud_test_catalog.src_uri
    ds = DatasetQuery(path=path, catalog=catalog)
    ds1 = ds.select(C.missing_column_name)
    ds2 = ds.select("missing_column_name")
    # The exception type varies by database backend
    exc1 = pytest.raises(Exception, ds1.results)
    assert "missing_column_name" in str(exc1.value)
    exc2 = pytest.raises(KeyError, ds2.results)
    assert "missing_column_name" in str(exc2.value)


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_select_except(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    path = cloud_test_catalog.src_uri
    ds = DatasetQuery(path=path, catalog=catalog)
    q = (
        ds.order_by(C.size.desc(), C.name)
        .limit(6)
        .select(C.parent, "name", C.size, size10x=C.size * 10, size100x=C.size * 100)
        .select_except(C.parent, C.size10x)
    )
    result = q.results()
    assert result == [
        ("description", 13, 1300),
        ("cat1", 4, 400),
        ("cat2", 4, 400),
        ("dog1", 4, 400),
        ("dog3", 4, 400),
        ("dog4", 4, 400),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_select_default(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    path = cloud_test_catalog.src_uri
    ds = DatasetQuery(path=path, catalog=catalog)
    original_result = ds.order_by(C.size.desc(), C.name).limit(6).results()
    q = (
        ds.order_by(C.size.desc(), C.name)
        .limit(6)
        .mutate(size10x=C.size * 10, size100x=C.size * 100)
        .select_default()
    )
    result = q.results()
    assert result == original_result
    assert len(result[0]) == len(DATASET_CORE_COLUMN_NAMES)


@pytest.mark.parametrize("save", [True, False])
@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_mutate(cloud_test_catalog, save):
    catalog = cloud_test_catalog.catalog
    path = cloud_test_catalog.src_uri
    ds = DatasetQuery(path=path, catalog=catalog)
    q = (
        ds.mutate(size10x=C.size * 10)
        .mutate(size1000x=C.size10x * 100)
        .mutate(
            ("s2", C.size * 2),
            ("s3", C.size * 3),
            s4=C.size * 4,
        )
        .filter((C.size10x < 40) | (C.size10x > 100) | C.name.glob("cat*"))
        .order_by(C.size10x.desc(), C.name)
    )
    if save:
        ds_name = "animals_cats"
        q.save(ds_name)
        new_query = DatasetQuery(name=ds_name, catalog=catalog).order_by(
            C.size10x.desc(), C.name
        )
        result = new_query.results(row_factory=lambda c, v: dict(zip(c, v)))
        dataset_record = catalog.get_dataset(ds_name)
        assert dataset_record.status == DatasetStatus.COMPLETE
    else:
        result = q.results(row_factory=lambda c, v: dict(zip(c, v)))
    assert len(result) == 4
    assert len(result[0]) == 23
    cols = {"size10x", "size1000x", "s2", "s3", "s4"}
    new_data = [[v for k, v in r.items() if k in cols] for r in result]
    assert new_data == [
        [130, 13000, 26, 39, 52],
        [40, 4000, 8, 12, 16],
        [40, 4000, 8, 12, 16],
        [30, 3000, 6, 9, 12],
    ]


@pytest.mark.parametrize("save", [True, False])
@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_order_by_limit(cloud_test_catalog, save):
    catalog = cloud_test_catalog.catalog
    path = cloud_test_catalog.src_uri
    ds = DatasetQuery(path=path, catalog=catalog)
    q = ds.order_by(C.name.desc()).limit(5)
    if save:
        ds_name = "animals_cats"
        q.save(ds_name)
        new_query = DatasetQuery(name=ds_name, catalog=catalog).order_by(C.name.desc())
        result = new_query.results()
        dataset_record = catalog.get_dataset(ds_name)
        assert dataset_record.status == DatasetStatus.COMPLETE
    else:
        result = q.results()
    assert [r[5] for r in result] == ["dog4", "dog3", "dog2", "dog1", "description"]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_number_without_explicit_order_by(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    path = cloud_test_catalog.src_uri
    ds_name = uuid.uuid4().hex

    DatasetQuery(path=path, catalog=catalog, client_config=conf).filter(
        C.size > 0
    ).save(ds_name)

    results = DatasetQuery(name=ds_name, catalog=catalog).to_records()
    assert len(results) == 7  # unordered, just checking num of results


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_number_with_order_by_name_descending(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    path = cloud_test_catalog.src_uri
    ds_name = uuid.uuid4().hex

    DatasetQuery(path=path, catalog=catalog, client_config=conf).order_by(
        C.name.desc()
    ).save(ds_name)

    results = DatasetQuery(name=ds_name, catalog=catalog).to_records()
    results_name_id = [
        {k: v for k, v in r.items() if k in ["id", "name"]} for r in results
    ]
    assert sorted(results_name_id, key=lambda k: k["id"]) == [
        {"id": 1, "name": "dog4"},
        {"id": 2, "name": "dog3"},
        {"id": 3, "name": "dog2"},
        {"id": 4, "name": "dog1"},
        {"id": 5, "name": "description"},
        {"id": 6, "name": "cat2"},
        {"id": 7, "name": "cat1"},
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_number_with_order_by_name_ascending(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    path = cloud_test_catalog.src_uri
    ds_name = uuid.uuid4().hex

    DatasetQuery(path=path, catalog=catalog, client_config=conf).order_by(
        C.name.asc()
    ).save(ds_name)

    results = DatasetQuery(name=ds_name, catalog=catalog).to_records()
    results_name_id = [
        {k: v for k, v in r.items() if k in ["id", "name"]} for r in results
    ]
    assert sorted(results_name_id, key=lambda k: k["id"]) == [
        {"id": 1, "name": "cat1"},
        {"id": 2, "name": "cat2"},
        {"id": 3, "name": "description"},
        {"id": 4, "name": "dog1"},
        {"id": 5, "name": "dog2"},
        {"id": 6, "name": "dog3"},
        {"id": 7, "name": "dog4"},
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_number_with_order_by_name_len_desc_and_name_asc(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    path = cloud_test_catalog.src_uri
    ds_name = uuid.uuid4().hex

    @udf(("name",), {"name_len": Int})
    def name_len(name):
        return (len(name),)

    DatasetQuery(path=path, catalog=catalog, client_config=conf).add_signals(
        name_len
    ).order_by(C.name_len.desc(), C.name.asc()).save(ds_name)

    results = DatasetQuery(name=ds_name, catalog=catalog).to_records()
    results_name_id = [
        {k: v for k, v in r.items() if k in ["id", "name"]} for r in results
    ]
    assert sorted(results_name_id, key=lambda k: k["id"]) == [
        {"id": 1, "name": "description"},
        {"id": 2, "name": "cat1"},
        {"id": 3, "name": "cat2"},
        {"id": 4, "name": "dog1"},
        {"id": 5, "name": "dog2"},
        {"id": 6, "name": "dog3"},
        {"id": 7, "name": "dog4"},
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_number_with_order_by_before_add_signals(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    path = cloud_test_catalog.src_uri
    ds_name = uuid.uuid4().hex

    @udf(("name",), {"name_len": Int})
    def name_len(name):
        return (len(name),)

    DatasetQuery(path=path, catalog=catalog, client_config=conf).order_by(
        C.name.asc()
    ).add_signals(name_len).save(ds_name)

    results = DatasetQuery(name=ds_name, catalog=catalog).to_records()
    results_name_id = [
        {k: v for k, v in r.items() if k in ["id", "name"]} for r in results
    ]
    # we should preserve order in final result based on order by which was added
    # before add_signals
    assert sorted(results_name_id, key=lambda k: k["id"]) == [
        {"id": 1, "name": "cat1"},
        {"id": 2, "name": "cat2"},
        {"id": 3, "name": "description"},
        {"id": 4, "name": "dog1"},
        {"id": 5, "name": "dog2"},
        {"id": 6, "name": "dog3"},
        {"id": 7, "name": "dog4"},
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_udf(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    sources = [cloud_test_catalog.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources)
    catalog.create_shadow_dataset("animals", globs, recursive=True)

    @udf(("name",), {"name_len": Int})
    def name_len(name):
        # A very simple udf.
        return (len(name),)

    q = (
        DatasetQuery(name="animals", catalog=catalog)
        .filter(C.size < 13)
        .filter(C.parent.glob("cats*") | (C.size < 4))
        .add_signals(name_len)
    )
    result1 = q.select(C.name, C.name_len).results()
    # ensure that we're able to run with same query multiple times
    result2 = q.select(C.name, C.name_len).results()
    count = q.count()
    # ensure that temporary tables are cleaned up
    assert [
        t
        for t in sqlalchemy.inspect(catalog.data_storage.ddb.engine).get_table_names()
        if t.startswith("udf_")
    ] == []
    assert len(result1) == 3
    assert len(result2) == 3
    assert count == 3

    for r1, r2 in zip(result1, result2):
        # Check that the UDF ran successfully
        assert len(r1[0]) == r1[1]
        assert len(r2[0]) == r2[1]

    q.save("test_udf")
    dataset = catalog.get_dataset("test_udf")
    default_dataset_custom_column_types = {
        c.name: c.type.__class__
        for c in catalog.data_storage.dataset_row_cls.default_columns()
        if isinstance(c.type, SQLType)
    }
    assert dataset.custom_column_types == {
        **default_dataset_custom_column_types,
        "name_len": Int,
    }


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_udf_different_types(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    sources = [cloud_test_catalog.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources)
    catalog.create_shadow_dataset("animals", globs, recursive=True)

    obj = {"name": "John", "age": 30}

    @udf(
        (),
        {
            "int_col": Int,
            "int_col_32": Int32,
            "int_col_64": Int64,
            "float_col": Float,
            "float_col_32": Float32,
            "float_col_64": Float64,
            "array_col": Array(Float),
            "array_col_nested": Array(Array(Float)),
            "array_col_32": Array(Float32),
            "array_col_64": Array(Float64),
            "string_col": String,
            "bool_col": Boolean,
            "json_col": JSON,
            "binary_col": Binary,
        },
    )
    def test_types():
        return (
            5,
            5,
            5,
            0.5,
            0.5,
            0.5,
            [0.5],
            [[0.5], [0.5]],
            [0.5],
            [0.5],
            "s",
            True,
            dumps({"a": 1}),
            pickle.dumps(obj),
        )

    q = (
        DatasetQuery(name="animals", catalog=catalog)
        .filter(C.name == "cat1")
        .add_signals(test_types)
    )

    results = q.select().to_records()
    col_values = [
        (
            r["int_col"],
            r["int_col_32"],
            r["int_col_64"],
            r["float_col"],
            r["float_col_32"],
            r["float_col_64"],
            r["array_col"],
            r["array_col_nested"],
            r["array_col_32"],
            r["array_col_64"],
            r["string_col"],
            r["bool_col"],
            r["json_col"],
            pickle.loads(r["binary_col"]),  # noqa: S301
        )
        for r in results
    ]

    assert col_values == [
        (
            5,
            5,
            5,
            0.5,
            0.5,
            0.5,
            [0.5],
            [[0.5], [0.5]],
            [0.5],
            [0.5],
            "s",
            True,
            dumps({"a": 1}),
            obj,
        )
    ]

    q.save("test_udf")
    dataset = catalog.get_dataset("test_udf")
    default_dataset_custom_column_types = {
        c.name: c.type.__class__
        for c in catalog.data_storage.dataset_row_cls.default_columns()
    }

    custom_dataset_custom_column_types = {
        "int_col": Int,
        "int_col_32": Int32,
        "int_col_64": Int64,
        "float_col": Float,
        "float_col_32": Float32,
        "float_col_64": Float64,
        "array_col": Array(Float()),
        "array_col_nested": Array(Array(Float())),
        "array_col_32": Array(Float32()),
        "array_col_64": Array(Float64()),
        "string_col": String,
        "bool_col": Boolean,
        "json_col": JSON,
        "binary_col": Binary,
    }

    expected_column_types = {
        **default_dataset_custom_column_types,
        **custom_dataset_custom_column_types,
    }

    for c_name, c_type in dataset.custom_column_types.items():
        assert c_name in expected_column_types
        c_type_expected = expected_column_types[c_name]
        if not isinstance(c_type, SQLType):
            c_type = c_type()
            c_type_expected = c_type_expected()

        assert c_type.to_dict() == c_type_expected.to_dict()


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
@pytest.mark.parametrize("batch", [1, 4])
def test_class_udf(cloud_test_catalog, batch):
    catalog = cloud_test_catalog.catalog
    sources = [cloud_test_catalog.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources)
    catalog.create_shadow_dataset("animals", globs, recursive=True)

    @udf(("size",), {"total": Int}, method="sum", batch=batch)
    class MyUDF:
        def __init__(self, constant, multiplier=1):
            self.constant = constant
            self.multiplier = multiplier
            self.batch = batch

        def sum(self, size):
            if self.batch > 1:
                return [(self.constant + size_ * self.multiplier,) for (size_,) in size]
            return (self.constant + size * self.multiplier,)

    q = (
        DatasetQuery(name="animals", catalog=catalog)
        .filter(C.size < 13)
        .add_signals(MyUDF(5, multiplier=2))
    )
    results = q.select(C.size, C.total).order_by(C.size).results()
    assert results == [
        (3, 11),
        (4, 13),
        (4, 13),
        (4, 13),
        (4, 13),
        (4, 13),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
@pytest.mark.parametrize("batch", [False, True])
def test_udf_parallel(cloud_test_catalog_tmpfile, batch):
    catalog = cloud_test_catalog_tmpfile.catalog
    sources = [cloud_test_catalog_tmpfile.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources)
    catalog.create_shadow_dataset("animals", globs, recursive=True)

    @udf(("name",), {"name_len": Int})
    def name_len_local(name):
        # A very simple udf.
        return (len(name),)

    @udf(("name",), {"name_len": Int}, batch=2)
    def name_len_batch(names):
        # A very simple udf.
        return [(len(name),) for (name,) in names]

    if batch:
        # Batching is enabled, we need a udf that acts on
        # lists of inputs.
        udf_func = name_len_batch
    else:
        udf_func = name_len_local

    q = (
        DatasetQuery(name="animals", catalog=catalog)
        .filter(C.size < 13)
        .filter(C.parent.glob("cats*") | (C.size < 4))
        .add_signals(udf_func, parallel=-1)
        .select(C.name, C.name_len)
    )
    result = q.results()

    assert len(result) == 3
    for r in result:
        # Check that the UDF ran successfully
        assert len(r[0]) == r[1]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_udf_parallel_exec_error(cloud_test_catalog_tmpfile):
    catalog = cloud_test_catalog_tmpfile.catalog
    sources = [cloud_test_catalog_tmpfile.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources)
    catalog.create_shadow_dataset("animals", globs, recursive=True)

    @udf((C.name,), {"name_len": Int})
    def name_len_error(_name):
        # A udf that raises an exception
        raise RuntimeError("Test Error!")

    q = (
        DatasetQuery(name="animals", catalog=catalog)
        .filter(C.size < 13)
        .filter(C.parent.glob("cats*") | (C.size < 4))
        .add_signals(name_len_error, parallel=-1)
    )
    with pytest.raises(RuntimeError, match="UDF Execution Failed!"):
        q.results()


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
@pytest.mark.parametrize("batch", [False, True])
@pytest.mark.parametrize("workers", (1, 2))
def test_udf_distributed(cloud_test_catalog_tmpfile, batch, workers):
    if not os.environ.get("DVCX_DISTRIBUTED"):
        pytest.skip(
            "Set the DVCX_DISTRIBUTED environment variable to test distributed UDFs"
        )
    catalog = cloud_test_catalog_tmpfile.catalog
    sources = [cloud_test_catalog_tmpfile.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources)
    catalog.create_shadow_dataset("animals", globs, recursive=True)

    @udf(("name",), {"name_len": Int, "blank": String})
    def name_len_local(name):
        # A very simple udf.
        return (len(name), None)

    @udf(("name",), {"name_len": Int, "blank": String}, batch=2)
    def name_len_batch(names):
        # A very simple udf.
        return [(len(name), None) for (name,) in names]

    if batch:
        # Batching is enabled, we need a udf that acts on lists of inputs.
        udf_func = name_len_batch
    else:
        udf_func = name_len_local

    q = (
        DatasetQuery(name="animals", catalog=catalog)
        .filter(C.size < 13)
        .filter(C.parent.glob("cats*") | (C.size < 4))
        .add_signals(udf_func, parallel=2, workers=workers)
        .select(C.name, C.name_len, C.blank)
    )
    result = q.results()

    assert len(result) == 3
    for r in result:
        # Check that the UDF ran successfully
        assert len(r[0]) == r[1]
        assert r[2] == String.default_value()


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
@pytest.mark.parametrize("workers", (1, 2))
def test_udf_distributed_exec_error(cloud_test_catalog_tmpfile, workers):
    if not os.environ.get("DVCX_DISTRIBUTED"):
        pytest.skip(
            "Set the DVCX_DISTRIBUTED environment variable to test distributed UDFs"
        )
    catalog = cloud_test_catalog_tmpfile.catalog
    sources = [cloud_test_catalog_tmpfile.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources)
    catalog.create_shadow_dataset("animals", globs, recursive=True)

    @udf((C.name,), {"name_len": Int})
    def name_len_error(_name):
        # A udf that raises an exception
        raise RuntimeError("Test Error!")

    q = (
        DatasetQuery(name="animals", catalog=catalog)
        .filter(C.size < 13)
        .filter(C.parent.glob("cats*") | (C.size < 4))
        .add_signals(name_len_error, parallel=2, workers=workers)
    )
    with pytest.raises(RuntimeError, match="Test Error!"):
        q.results()


def test_apply_udf(cloud_test_catalog, tmp_path):
    catalog = cloud_test_catalog.catalog
    sources = [cloud_test_catalog.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources)
    catalog.create_shadow_dataset("animals", globs, recursive=True)

    code = """\
        from dql.query import C, udf
        from dql.sql.types import Int

        @udf((C.name,), {"name_len": Int})
        def name_len(name):
            # A very simple udf.
            return (len(name),)
    """
    script = tmp_path / "foo.py"
    script.write_text(dedent(code))

    catalog.apply_udf(f"{script}:name_len", cloud_test_catalog.src_uri, "from-storage")
    q = DatasetQuery(name="from-storage", catalog=catalog).filter(C.name_len == 4)
    assert len(q.results()) == 6

    catalog.apply_udf(f"{script}:name_len", "ds://animals", "from-dataset")
    q = DatasetQuery(name="from-dataset", catalog=catalog).filter(C.name_len == 4)
    assert len(q.results()) == 6


def to_str(buf) -> str:
    return io.TextIOWrapper(buf, encoding="utf8").read()


@pytest.mark.parametrize("param", [LocalFilename(), Object(to_str)])
@pytest.mark.parametrize("use_cache", [False, True])
def test_udf_object_param(cloud_test_catalog, dogs_shadow_dataset, param, use_cache):
    catalog = cloud_test_catalog.catalog
    if isinstance(param, Object):

        @udf((C.name, param), {"signal": String})
        def signal(name, obj):
            # A very simple udf.
            return (name + " -> " + obj,)

    else:

        @udf(("name", param), {"signal": String})
        def signal(name, local_filename):
            with open(local_filename, encoding="utf8") as f:
                obj = f.read()
            return (name + " -> " + obj,)

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).add_signals(
        signal, cache=use_cache
    )
    result = q.results()

    assert len(result) == 4
    signals = {r[-1] for r in result}
    assert signals == {"dog1 -> woof", "dog2 -> arf", "dog3 -> bark", "dog4 -> ruff"}

    uid = Node(*result[0][:-1]).as_uid()
    assert catalog.cache.contains(uid) is (
        use_cache or isinstance(param, LocalFilename)
    )


@pytest.mark.parametrize("use_cache", [False, True])
def test_udf_stream_param(cloud_test_catalog, dogs_shadow_dataset, use_cache):
    catalog = cloud_test_catalog.catalog

    @udf((C.name, Stream()), {"signal": String})
    def signal(name, stream):
        with stream as buf:
            return (name + " -> " + buf.read().decode("utf-8"),)

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).add_signals(
        signal, cache=use_cache
    )
    result = q.results()

    assert len(result) == 4
    signals = {r[-1] for r in result}
    assert signals == {"dog1 -> woof", "dog2 -> arf", "dog3 -> bark", "dog4 -> ruff"}

    uid = Node(*result[0][:-1]).as_uid()
    assert catalog.cache.contains(uid) is use_cache


def test_extract(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog
    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
    results = set()
    for name, stream in q.extract("name", Stream()):
        with stream:
            value = stream.read().decode("utf-8")
        results.add((name, value))
    assert results == {
        ("dog1", "woof"),
        ("dog2", "arf"),
        ("dog3", "bark"),
        ("dog4", "ruff"),
    }


def test_extract_object(cloud_test_catalog, dogs_shadow_dataset):
    ctc = cloud_test_catalog
    ds = DatasetQuery(name=dogs_shadow_dataset.name, catalog=ctc.catalog)
    data = ds.extract(Object(to_str), "name")
    assert set(data) == {
        ("woof", "dog1"),
        ("arf", "dog2"),
        ("bark", "dog3"),
        ("ruff", "dog4"),
    }


def test_extract_chunked(cloud_test_catalog, dogs_shadow_dataset):
    ctc = cloud_test_catalog
    n = 5
    all_data = []
    ds = DatasetQuery(name=dogs_shadow_dataset.name, catalog=ctc.catalog)
    for i in range(n):
        data = ds.chunk(i, n).extract(Object(to_str), "name")
        all_data.extend(data)

    assert set(all_data) == {
        ("woof", "dog1"),
        ("arf", "dog2"),
        ("bark", "dog3"),
        ("ruff", "dog4"),
    }


@pytest.mark.parametrize(
    "cloud_type, version_aware",
    [("file", False)],
    indirect=True,
)
def test_extract_limit(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog
    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
    results = list(q.limit(2).extract("name"))
    assert len(results) == 2


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_union(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    sources = [str(cloud_test_catalog.src_uri)]
    catalog.index(sources)

    src = cloud_test_catalog.src_uri
    catalog.create_shadow_dataset("dogs", [f"{src}/dogs/*"], recursive=True)
    catalog.create_shadow_dataset("cats", [f"{src}/cats/*"], recursive=True)

    dogs = DatasetQuery(name="dogs", catalog=catalog)
    cats = DatasetQuery(name="cats", catalog=catalog)

    (dogs | cats).save("dogs_cats")

    q = DatasetQuery(name="dogs_cats", catalog=catalog)
    result = q.results()
    count = q.count()
    assert len(result) == 6
    assert count == 6


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
@pytest.mark.parametrize("predicates", ["name", C.name])
def test_join_left_one_column_predicate(
    cloud_test_catalog,
    dogs_shadow_dataset,
    cats_shadow_dataset,
    dogs_cats_shadow_dataset,
    predicates,
):
    catalog = cloud_test_catalog.catalog

    @udf((), {"sig1": Int})
    def signals1():
        return (1,)

    @udf((), {"sig2": Int})
    def signals2():
        return (2,)

    dogs_cats = DatasetQuery(
        name=dogs_cats_shadow_dataset.name, catalog=catalog
    ).add_signals(signals1)
    dogs = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).add_signals(
        signals2
    )

    joined_records = dogs_cats.join(dogs, predicates).to_records()
    assert len(joined_records) == 6

    cat_records_names = ["cat1", "cat2"]

    dogs_cats_records = DatasetQuery(
        name=dogs_cats_shadow_dataset.name, catalog=catalog
    ).to_records()

    # rows that found match have both signals
    assert all(
        r["sig1"] == 1 and r["sig2"] == 2
        for r in joined_records
        if r["name"] not in cat_records_names
    )
    # rows from the left that didn't find match (cats) don't have sig2
    assert all(
        r["sig1"] == 1 and r["sig2"] == Int.default_value()
        for r in joined_records
        if r["name"] in cat_records_names
    )
    # check core duplicated columns
    for r in joined_records:
        dog_r = next(dr for dr in dogs_cats_records if dr["name"] == r["name"])
        assert all([r[f"{k}_right"] == dog_r[k]] for k in dog_r.keys())


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
@pytest.mark.parametrize(
    "predicates", [["name", "parent"], [C.name, C.parent], ["name", C.parent]]
)
def test_join_left_multiple_column_pedicates(
    cloud_test_catalog,
    dogs_shadow_dataset,
    cats_shadow_dataset,
    dogs_cats_shadow_dataset,
    predicates,
):
    catalog = cloud_test_catalog.catalog

    @udf((), {"sig1": Int})
    def signals1():
        return (1,)

    @udf((), {"sig2": Int})
    def signals2():
        return (2,)

    dogs_cats = DatasetQuery(
        name=dogs_cats_shadow_dataset.name, catalog=catalog
    ).add_signals(signals1)
    dogs = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).add_signals(
        signals2
    )

    cat_records_names = ["cat1", "cat2"]

    dogs_cats_records = DatasetQuery(
        name=dogs_cats_shadow_dataset.name, catalog=catalog
    ).to_records()

    joined_records = dogs_cats.join(dogs, predicates).to_records()
    assert len(joined_records) == 6

    # rows that found match have both signals
    assert all(
        r["sig1"] == 1 and r["sig2"] == 2
        for r in joined_records
        if r["name"] not in cat_records_names
    )
    # rows from the left that didn't find match (cats) don't have sig2
    assert all(
        r["sig1"] == 1 and r["sig2"] == Int.default_value()
        for r in joined_records
        if r["name"] in cat_records_names
    )
    # check core duplicated columns
    for r in joined_records:
        dog_r = next(dr for dr in dogs_cats_records if dr["name"] == r["name"])
        assert all([r[f"{k}_right"] == dog_r[k]] for k in dog_r.keys())


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
@pytest.mark.parametrize("inner", [True, False])
def test_join_with_binary_expression_on_one_column(
    cloud_test_catalog,
    dogs_shadow_dataset,
    cats_shadow_dataset,
    dogs_cats_shadow_dataset,
    inner,
):
    catalog = cloud_test_catalog.catalog
    dogs = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
    cats = DatasetQuery(name=cats_shadow_dataset.name, catalog=catalog)
    dogs_cats = dogs.union(cats)

    res = dogs_cats.join(
        dogs, dogs_cats.c("name") == dogs.c("name"), inner=inner
    ).to_records()

    if inner:
        expected = [
            ("dog1", "dog1"),
            ("dog2", "dog2"),
            ("dog3", "dog3"),
            ("dog4", "dog4"),
        ]
    else:
        expected = [
            ("cat1", String.default_value()),
            ("cat2", String.default_value()),
            ("dog1", "dog1"),
            ("dog2", "dog2"),
            ("dog3", "dog3"),
            ("dog4", "dog4"),
        ]

    assert (
        sorted([(r["name"], r["name_right"]) for r in res], key=lambda x: x[0])
        == expected
    )


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
@pytest.mark.parametrize("inner", [True, False])
def test_join_with_binary_expression_on_multiple_columns(
    cloud_test_catalog,
    dogs_shadow_dataset,
    cats_shadow_dataset,
    dogs_cats_shadow_dataset,
    inner,
):
    catalog = cloud_test_catalog.catalog
    dogs = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
    dogs_cats = DatasetQuery(name=dogs_cats_shadow_dataset.name, catalog=catalog)

    res = dogs_cats.join(
        dogs,
        (
            (dogs_cats.c("name") == dogs.c("name"))
            & (dogs_cats.c("parent") == dogs.c("parent"))
        ),
        inner=inner,
    ).to_records()

    if inner:
        expected = [
            ("dog1", "dog1"),
            ("dog2", "dog2"),
            ("dog3", "dog3"),
            ("dog4", "dog4"),
        ]
    else:
        expected = [
            ("cat1", String.default_value()),
            ("cat2", String.default_value()),
            ("dog1", "dog1"),
            ("dog2", "dog2"),
            ("dog3", "dog3"),
            ("dog4", "dog4"),
        ]

    assert (
        sorted([(r["name"], r["name_right"]) for r in res], key=lambda x: x[0])
        == expected
    )


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
@pytest.mark.parametrize("inner", [True, False])
@pytest.mark.parametrize("column_predicate", ["name", C.name])
def test_join_with_combination_binary_expression_and_column_predicates(
    cloud_test_catalog,
    dogs_shadow_dataset,
    cats_shadow_dataset,
    dogs_cats_shadow_dataset,
    inner,
    column_predicate,
):
    catalog = cloud_test_catalog.catalog
    dogs = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
    dogs_cats = DatasetQuery(name=dogs_cats_shadow_dataset.name, catalog=catalog)

    res = dogs_cats.join(
        dogs,
        [column_predicate, dogs_cats.c("parent") == dogs.c("parent")],
        inner=inner,
    ).to_records()

    if inner:
        expected = [
            ("dog1", "dog1"),
            ("dog2", "dog2"),
            ("dog3", "dog3"),
            ("dog4", "dog4"),
        ]
    else:
        expected = [
            ("cat1", String.default_value()),
            ("cat2", String.default_value()),
            ("dog1", "dog1"),
            ("dog2", "dog2"),
            ("dog3", "dog3"),
            ("dog4", "dog4"),
        ]

    assert (
        sorted([(r["name"], r["name_right"]) for r in res], key=lambda x: x[0])
        == expected
    )


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
@pytest.mark.parametrize("inner", [True, False])
def test_join_with_binary_expression_with_arithmetics(
    cloud_test_catalog,
    dogs_shadow_dataset,
    cats_shadow_dataset,
    inner,
):
    catalog = cloud_test_catalog.catalog
    dogs = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
    cats = DatasetQuery(name=cats_shadow_dataset.name, catalog=catalog)

    res = cats.join(
        dogs, cats.c("size") == dogs.c("size") + 1, inner=inner
    ).to_records()

    assert sorted([(r["name"], r["name_right"]) for r in res], key=lambda x: x[0]) == [
        ("cat1", "dog2"),
        ("cat2", "dog2"),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_join_conflicting_custom_columns(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    @udf((), {"sig1": Int})
    def signals1():
        return (1,)

    @udf((), {"sig1": Int})
    def signals2():
        return (2,)

    ds1 = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).add_signals(
        signals1
    )
    ds2 = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).add_signals(
        signals2
    )

    joined_records = ds1.join(ds2, "name").to_records()
    assert len(joined_records) == 4

    # check custom columns
    assert all(r["sig1"] == 1 and r["sig1_right"] == 2 for r in joined_records)

    joined_records = ds1.join(ds2, "name", rname="{name}_dupl").to_records()
    assert len(joined_records) == 4

    # check custom columns
    assert all(r["sig1"] == 1 and r["sig1_dupl"] == 2 for r in joined_records)


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_join_inner(
    cloud_test_catalog,
    dogs_shadow_dataset,
    cats_shadow_dataset,
    dogs_cats_shadow_dataset,
):
    catalog = cloud_test_catalog.catalog

    @udf((), {"sig1": Int})
    def signals1():
        return (1,)

    @udf((), {"sig2": Int})
    def signals2():
        return (2,)

    dogs_cats = DatasetQuery(
        name=dogs_cats_shadow_dataset.name, catalog=catalog
    ).add_signals(signals1)
    dogs = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).add_signals(
        signals2
    )

    joined_records = dogs_cats.join(dogs, "name", inner=True).to_records()
    assert len(joined_records) == 4

    dogs_records = DatasetQuery(
        name=dogs_shadow_dataset.name, catalog=catalog
    ).to_records()

    # check custom columns
    assert all(r["sig1"] == 1 and r["sig2"] == 2 for r in joined_records)
    for r in joined_records:
        dog_r = next(dr for dr in dogs_records if dr["name"] == r["name"])
        assert all([r[f"{k}_right"] == dog_r[k]] for k in dog_r.keys())

    # joining on multiple fields
    joined_records = dogs_cats.join(dogs, ["parent", "name"], inner=True).to_records()
    assert len(joined_records) == 4

    # check custom columns
    assert all(r["sig1"] == 1 and r["sig2"] == 2 for r in joined_records)
    # check core duplicated columns
    for r in joined_records:
        dog_r = next(dr for dr in dogs_records if dr["name"] == r["name"])
        assert all([r[f"{k}_right"] == dog_r[k]] for k in dog_r.keys())


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_join_with_self(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    @udf((), {"sig1": Int})
    def signals1():
        return (1,)

    dogs_records = DatasetQuery(
        name=dogs_shadow_dataset.name, catalog=catalog
    ).to_records()

    dogs = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).add_signals(
        signals1
    )

    joined_records = dogs.join(dogs, "name").to_records()
    assert len(joined_records) == 4

    # check custom columns
    assert all(r["sig1"] == 1 and r["sig1_right"] == 1 for r in joined_records)
    # check core duplicated columns
    for r in joined_records:
        dog_r = next(dr for dr in dogs_records if dr["name"] == r["name"])
        assert all([r[f"{k}_right"] == dog_r[k]] for k in dog_r.keys())


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_join_with_missing_predicates(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    @udf((), {"sig1": Int})
    def signals1():
        return (1,)

    @udf((), {"sig2": Int})
    def signals2():
        return (1,)

    dogs1 = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).add_signals(
        signals1
    )
    dogs2 = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).add_signals(
        signals2
    )

    with pytest.raises(ValueError) as excinfo:
        dogs1.join(dogs2, "sig1").to_records()
    assert str(excinfo.value) == "Column sig1 was not found in right part of the join"

    with pytest.raises(ValueError) as excinfo:
        dogs1.join(dogs2, "sig2").to_records()
    assert str(excinfo.value) == "Column sig2 was not found in left part of the join"


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_join_with_wrong_predicates(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    dogs1 = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
    dogs2 = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)

    with pytest.raises(ValueError) as excinfo:
        dogs1.join(dogs2, []).to_records()
    assert str(excinfo.value) == "Missing predicates"

    with pytest.raises(ValueError) as excinfo:
        dogs1.join(dogs2, [[]]).to_records()
    assert str(excinfo.value) == "Unsupported predicate [] for join expression"


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_join_with_missing_columns_in_expression(
    cloud_test_catalog, dogs_shadow_dataset, cats_shadow_dataset
):
    catalog = cloud_test_catalog.catalog

    dogs1 = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
    dogs2 = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
    cats = DatasetQuery(name=cats_shadow_dataset.name, catalog=catalog)

    with pytest.raises(ValueError) as excinfo:
        dogs1.join(dogs2, dogs1.c("wrong") == dogs2.c("name")).to_records()
    assert str(excinfo.value) == "Column wrong was not found in left part of the join"

    with pytest.raises(ValueError) as excinfo:
        dogs1.join(dogs2, dogs1.c("name") == dogs2.c("wrong")).to_records()
    assert str(excinfo.value) == "Column wrong was not found in right part of the join"

    with pytest.raises(ValueError) as excinfo:
        dogs1.join(dogs2, dogs1.c("name") == cats.c("name")).to_records()
    assert str(excinfo.value) == (
        "Column name was not found in left or right part of the join"
    )


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
@pytest.mark.parametrize("inner", [True, False])
def test_join_with_using_functions_in_expression(
    cloud_test_catalog, dogs_shadow_dataset, dogs_cats_shadow_dataset, inner
):
    catalog = cloud_test_catalog.catalog
    dogs = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
    dogs_cats = DatasetQuery(name=dogs_cats_shadow_dataset.name, catalog=catalog)

    res = dogs_cats.join(
        dogs,
        (
            sqlalchemy.func.upper(dogs_cats.c("name"))
            == sqlalchemy.func.upper(dogs.c("name"))
        ),
        inner=inner,
    ).to_records()

    if inner:
        expected = [
            ("dog1", "dog1"),
            ("dog2", "dog2"),
            ("dog3", "dog3"),
            ("dog4", "dog4"),
        ]
    else:
        expected = [
            ("cat1", String.default_value()),
            ("cat2", String.default_value()),
            ("dog1", "dog1"),
            ("dog2", "dog2"),
            ("dog3", "dog3"),
            ("dog4", "dog4"),
        ]

    assert (
        sorted([(r["name"], r["name_right"]) for r in res], key=lambda x: x[0])
        == expected
    )


def create_subobject(row, name: str, size: int):
    """Create a subobject with this row as its parent."""
    return {
        # Values that depend on the parent object.
        "vtype": "fake",
        "dir_type": 0,
        "parent_id": None,
        # Inherited values.
        "owner_name": row.owner_name,
        "owner_id": row.owner_id,
        "is_latest": row.is_latest,
        "source": row.source,
        # User-provided values.
        "name": name,
        "parent": row.path,
        "size": size,
        # Unspecified.
        "version": None,
        "etag": None,
        # Generated.
        "random": getrandbits(RANDOM_BITS),
    }


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_generator(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    @udf(("name", C.parent), DatasetRow.schema)
    def gen(name, parent):
        # A very simple file row generator.
        parent_path = name if not parent else f"{parent}/{name}"
        yield DatasetRow.create("subobject", size=50, parent=parent_path)
        yield DatasetRow.create("subobject2", size=70, parent=parent_path)

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).generate(gen)
    result = q.to_records()

    parents_names = [(r["parent"], r["name"]) for r in result]
    parents_names.sort(key=lambda x: (x[1], x[0]))

    assert parents_names == [
        ("dogs/dog1", "subobject"),
        ("dogs/dog2", "subobject"),
        ("dogs/dog3", "subobject"),
        ("dogs/others/dog4", "subobject"),
        ("dogs/dog1", "subobject2"),
        ("dogs/dog2", "subobject2"),
        ("dogs/dog3", "subobject2"),
        ("dogs/others/dog4", "subobject2"),
    ]

    q.save("test_generator")
    dataset = catalog.get_dataset("test_generator")
    assert dataset.custom_column_types == {
        c.name: c.type.__class__
        for c in catalog.data_storage.dataset_row_cls.default_columns()
        if isinstance(c.type, SQLType)
    }


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_generator_with_filter(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    @udf(("name", C.parent), DatasetRow.schema)
    def gen(name, parent):
        # A very simple file row generator.
        parent_path = name if not parent else f"{parent}/{name}"
        yield DatasetRow.create("subobject", size=50, parent=parent_path)
        yield DatasetRow.create("subobject2", size=70, parent=parent_path)

    q = (
        DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
        .generate(gen)
        .filter(C.name == "subobject")
    )
    result = q.to_records()

    parents_names = [(r["parent"], r["name"]) for r in result]
    parents_names.sort(key=lambda x: (x[1], x[0]))

    assert len(parents_names) == 4

    assert parents_names == [
        ("dogs/dog1", "subobject"),
        ("dogs/dog2", "subobject"),
        ("dogs/dog3", "subobject"),
        ("dogs/others/dog4", "subobject"),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_generator_with_limit(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    @udf((C.name, C.parent), DatasetRow.schema)
    def gen(name, parent):
        # A very simple file row generator.
        parent_path = name if not parent else f"{parent}/{name}"
        yield DatasetRow.create("subobject", size=50, parent=parent_path)
        yield DatasetRow.create("subobject2", size=70, parent=parent_path)

    q = (
        DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
        .order_by(C.name)
        .limit(1)
        .generate(gen)
    )
    result = q.to_records()

    parents_names = [(r["parent"], r["name"]) for r in result]
    parents_names.sort(key=lambda x: (x[1], x[0]))

    assert parents_names == [
        ("dogs/dog1", "subobject"),
        ("dogs/dog1", "subobject2"),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_generator_parallel(cloud_test_catalog_tmpfile):
    # Setup catalog.
    dogs_dataset_name = uuid.uuid4().hex
    catalog = cloud_test_catalog_tmpfile.catalog
    catalog.index([cloud_test_catalog_tmpfile.src_uri])
    src_uri = cloud_test_catalog_tmpfile.src_uri

    catalog.create_shadow_dataset(
        dogs_dataset_name, [f"{src_uri}/dogs/*"], recursive=True
    )
    dogs_shadow_dataset = catalog.data_storage.get_dataset(dogs_dataset_name)

    @udf(("name", "parent"), DatasetRow.schema)
    def gen(name, parent):
        # A very simple file row generator.
        parent_path = name if not parent else f"{parent}/{name}"
        yield DatasetRow.create("subobject", size=50, parent=parent_path)
        yield DatasetRow.create("subobject2", size=70, parent=parent_path)

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).generate(
        gen, parallel=-1
    )
    result = q.to_records()

    parents_names = [(r["parent"], r["name"]) for r in result]
    parents_names.sort(key=lambda x: (x[1], x[0]))

    assert parents_names == [
        ("dogs/dog1", "subobject"),
        ("dogs/dog2", "subobject"),
        ("dogs/dog3", "subobject"),
        ("dogs/others/dog4", "subobject"),
        ("dogs/dog1", "subobject2"),
        ("dogs/dog2", "subobject2"),
        ("dogs/dog3", "subobject2"),
        ("dogs/others/dog4", "subobject2"),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_generator_batch(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    @udf(("name", "parent"), DatasetRow.schema, batch=4)
    def gen(inputs):
        for name, parent in inputs:
            parent_path = name if not parent else f"{parent}/{name}"
            yield DatasetRow.create("subobject", size=50, parent=parent_path)
            yield DatasetRow.create("subobject2", size=70, parent=parent_path)

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).generate(gen)
    result = q.to_records()
    parents_names = [(r["parent"], r["name"]) for r in result]
    parents_names.sort(key=lambda x: (x[1], x[0]))

    assert parents_names == [
        ("dogs/dog1", "subobject"),
        ("dogs/dog2", "subobject"),
        ("dogs/dog3", "subobject"),
        ("dogs/others/dog4", "subobject"),
        ("dogs/dog1", "subobject2"),
        ("dogs/dog2", "subobject2"),
        ("dogs/dog3", "subobject2"),
        ("dogs/others/dog4", "subobject2"),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_generator_class(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    @udf(
        params=(C.name, C.parent),
        output=DatasetRow.schema,
        method="generate_subobjects",
    )
    class Subobjects:
        def __init__(self):
            pass

        def generate_subobjects(self, name, parent):
            parent_path = name if not parent else f"{parent}/{name}"
            yield DatasetRow.create("subobject", size=50, parent=parent_path)
            yield DatasetRow.create("subobject2", size=70, parent=parent_path)

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).generate(
        Subobjects
    )
    result = q.to_records()
    parents_names = [(r["parent"], r["name"]) for r in result]
    parents_names.sort(key=lambda x: (x[1], x[0]))

    assert parents_names == [
        ("dogs/dog1", "subobject"),
        ("dogs/dog2", "subobject"),
        ("dogs/dog3", "subobject"),
        ("dogs/others/dog4", "subobject"),
        ("dogs/dog1", "subobject2"),
        ("dogs/dog2", "subobject2"),
        ("dogs/dog3", "subobject2"),
        ("dogs/others/dog4", "subobject2"),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_generator_class_batch(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    @udf(
        params=(C.name, C.parent),
        output=DatasetRow.schema,
        method="generate_subobjects",
        batch=4,
    )
    class Subobjects:
        def __init__(self):
            pass

        def generate_subobjects(self, inputs):
            for name, parent in inputs:
                parent_path = name if not parent else f"{parent}/{name}"
                yield DatasetRow.create("subobject", size=50, parent=parent_path)
                yield DatasetRow.create("subobject2", size=70, parent=parent_path)

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).generate(
        Subobjects
    )
    result = q.to_records()
    parents_names = [(r["parent"], r["name"]) for r in result]
    parents_names.sort(key=lambda x: (x[1], x[0]))

    assert parents_names == [
        ("dogs/dog1", "subobject"),
        ("dogs/dog2", "subobject"),
        ("dogs/dog3", "subobject"),
        ("dogs/others/dog4", "subobject"),
        ("dogs/dog1", "subobject2"),
        ("dogs/dog2", "subobject2"),
        ("dogs/dog3", "subobject2"),
        ("dogs/others/dog4", "subobject2"),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_generator_partition_by(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    @udf(("name", "parent"), DatasetRow.extend(cnt=Int))
    def gen(inputs):
        cnt = len(inputs)
        for name, parent in inputs:
            parent_path = name if not parent else f"{parent}/{name}"
            yield DatasetRow.create("subobject", size=50, parent=parent_path) + (cnt,)
            yield DatasetRow.create("subobject2", size=70, parent=parent_path) + (cnt,)

    result = (
        DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
        .generate(gen, partition_by="parent")
        .to_records()
    )
    parents_names = [(r["parent"], r["name"], r["cnt"]) for r in result]
    parents_names.sort(key=lambda x: (x[1], x[0]))

    assert parents_names == [
        ("dogs/dog1", "subobject", 3),
        ("dogs/dog2", "subobject", 3),
        ("dogs/dog3", "subobject", 3),
        ("dogs/others/dog4", "subobject", 1),
        ("dogs/dog1", "subobject2", 3),
        ("dogs/dog2", "subobject2", 3),
        ("dogs/dog3", "subobject2", 3),
        ("dogs/others/dog4", "subobject2", 1),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_generator_partition_by_parallel(cloud_test_catalog_tmpfile):
    # Setup catalog.
    dogs_dataset_name = uuid.uuid4().hex
    catalog = cloud_test_catalog_tmpfile.catalog
    catalog.index([cloud_test_catalog_tmpfile.src_uri])
    src_uri = cloud_test_catalog_tmpfile.src_uri

    catalog.create_shadow_dataset(
        dogs_dataset_name, [f"{src_uri}/dogs/*"], recursive=True
    )
    dogs_shadow_dataset = catalog.data_storage.get_dataset(dogs_dataset_name)

    @udf(("name", "parent"), DatasetRow.extend(cnt=Int))
    def gen(inputs):
        cnt = len(inputs)
        for name, parent in inputs:
            parent_path = name if not parent else f"{parent}/{name}"
            yield DatasetRow.create("subobject", size=50, parent=parent_path) + (cnt,)
            yield DatasetRow.create("subobject2", size=70, parent=parent_path) + (cnt,)

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).generate(
        gen, partition_by="parent", parallel=-1
    )
    result = q.to_records()

    parents_names = [(r["parent"], r["name"], r["cnt"]) for r in result]
    parents_names.sort(key=lambda x: (x[1], x[0]))

    assert parents_names == [
        ("dogs/dog1", "subobject", 3),
        ("dogs/dog2", "subobject", 3),
        ("dogs/dog3", "subobject", 3),
        ("dogs/others/dog4", "subobject", 1),
        ("dogs/dog1", "subobject2", 3),
        ("dogs/dog2", "subobject2", 3),
        ("dogs/dog3", "subobject2", 3),
        ("dogs/others/dog4", "subobject2", 1),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_generator_partition_by_batch(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    @udf(("name", "parent"), DatasetRow.extend(cnt=Int), batch=2)
    def gen(inputs):
        cnt = len(inputs)
        for name, parent in inputs:
            parent_path = name if not parent else f"{parent}/{name}"
            yield DatasetRow.create("subobject", size=50, parent=parent_path) + (cnt,)
            yield DatasetRow.create("subobject2", size=70, parent=parent_path) + (cnt,)

    result = (
        DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
        .generate(gen, partition_by="parent")
        .to_records()
    )
    parents_names = [(r["parent"], r["name"], r["cnt"]) for r in result]
    parents_names.sort(key=lambda x: (x[1], x[0]))

    assert parents_names == [
        ("dogs/dog1", "subobject", 3),
        ("dogs/dog2", "subobject", 3),
        ("dogs/dog3", "subobject", 3),
        ("dogs/others/dog4", "subobject", 1),
        ("dogs/dog1", "subobject2", 3),
        ("dogs/dog2", "subobject2", 3),
        ("dogs/dog3", "subobject2", 3),
        ("dogs/others/dog4", "subobject2", 1),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_generator_with_new_columns(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog
    now = datetime.now(timezone.utc).replace(microsecond=0)

    int_example = 25

    new_columns = {
        "string_col": String,
        "int_col": Int,
        "int_col_32": Int32,
        "int_col_64": Int64,
        "bool_col": Boolean,
        "float_col": Float,
        "float_col_32": Float32,
        "float_col_64": Float64,
        "json_col": JSON,
        "datetime_col": DateTime,
        "binary_col": Binary,
        "array_col": Array(Float),
        "array_col_nested": Array(Array(Float)),
        "array_col_32": Array(Float32),
        "array_col_64": Array(Float64),
    }

    @udf(
        params=(C.name, C.parent),
        output={**DatasetRow.schema, **new_columns},
        method="generate_subobjects",
    )
    class Subobjects:
        def __init__(self):
            pass

        def generate_subobjects(self, name, parent):
            parent_path = name if not parent else f"{parent}/{name}"
            yield DatasetRow.create("subobject", size=50, parent=parent_path) + (
                "some_string",
                10,
                11,
                12,
                True,
                0.5,
                0.5,
                0.5,
                dumps({"a": 1}),
                now,
                int_example.to_bytes(2, "big"),
                [0.5, 0.5],
                [[0.5], [0.5]],
                [0.5, 0.5],
                [0.5, 0.5],
            )

    DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).generate(
        Subobjects
    ).save("dogs_with_rows_and_signals")

    q = DatasetQuery(name="dogs_with_rows_and_signals", catalog=catalog)
    result = q.select().to_records()

    col_values = [
        (
            r["parent"],
            r["name"],
            r["string_col"],
            r["int_col"],
            r["int_col_32"],
            r["int_col_64"],
            r["bool_col"],
            r["float_col"],
            r["float_col_32"],
            r["float_col_64"],
            r["json_col"],
            r["datetime_col"].astimezone(timezone.utc) if r["datetime_col"] else None,
            int.from_bytes(r["binary_col"], "big"),  # converting from binary to int
            r["array_col"],
            r["array_col_nested"],
            r["array_col_32"],
            r["array_col_64"],
        )
        for r in result
    ]

    col_values.sort(key=lambda x: (x[1], x[0]))

    new_col_values = (
        "some_string",
        10,
        11,
        12,
        True,
        0.5,
        0.5,
        0.5,
        dumps({"a": 1}),
        now,
        int_example,
        [0.5, 0.5],
        [[0.5], [0.5]],
        [0.5, 0.5],
        [0.5, 0.5],
    )

    assert col_values == [
        ("dogs/dog1", "subobject") + new_col_values,
        ("dogs/dog2", "subobject") + new_col_values,
        ("dogs/dog3", "subobject") + new_col_values,
        ("dogs/others/dog4", "subobject") + new_col_values,
    ]

    dataset = catalog.get_dataset("dogs_with_rows_and_signals")
    default_dataset_custom_column_types = {
        c.name: c.type.__class__
        for c in catalog.data_storage.dataset_row_cls.default_columns()
        if isinstance(c.type, SQLType)
    }
    custom_dataset_custom_column_types = {
        "string_col": String,
        "int_col": Int,
        "int_col_32": Int32,
        "int_col_64": Int64,
        "float_col": Float,
        "float_col_32": Float32,
        "float_col_64": Float64,
        "array_col": Array(Float()),
        "array_col_nested": Array(Array(Float())),
        "array_col_32": Array(Float32()),
        "array_col_64": Array(Float64()),
        "bool_col": Boolean,
        "json_col": JSON,
        "binary_col": Binary,
        "datetime_col": DateTime,
    }

    expected_column_types = {
        **default_dataset_custom_column_types,
        **custom_dataset_custom_column_types,
    }

    for c_name, c_type in dataset.custom_column_types.items():
        assert c_name in expected_column_types
        c_type_expected = expected_column_types[c_name]
        if not isinstance(c_type, SQLType):
            c_type = c_type()
            c_type_expected = c_type_expected()

        assert c_type.to_dict() == c_type_expected.to_dict()


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_generator_with_new_columns_empty_values(
    cloud_test_catalog, dogs_shadow_dataset
):
    catalog = cloud_test_catalog.catalog

    new_columns = {
        "int_col": Int,
        "int_col_32": Int32,
        "int_col_64": Int64,
        "bool_col": Boolean,
        "float_col": Float,
        "float_col_32": Float32,
        "float_col_64": Float64,
        "json_col": JSON,
        "datetime_col": DateTime,
        "binary_col": Binary,
        "array_col": Array(Float),
        "array_col_nested": Array(Array(Float)),
        "array_col_32": Array(Float32),
        "array_col_64": Array(Float64),
    }
    new_col_values_empty = tuple(t.default_value() for t in new_columns.values())

    @udf(
        params=(C.name, C.parent),
        output={**DatasetRow.schema, **new_columns},
        method="generate_subobjects",
    )
    class Subobjects:
        def __init__(self):
            pass

        def generate_subobjects(self, name, parent):
            parent_path = name if not parent else f"{parent}/{name}"
            yield (
                DatasetRow.create("subobject", size=50, parent=parent_path)
                + new_col_values_empty
            )

    DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).generate(
        Subobjects
    ).save("dogs_with_rows_and_signals")

    q = DatasetQuery(name="dogs_with_rows_and_signals", catalog=catalog)
    result = q.to_records()

    col_values = [
        (
            r["parent"],
            r["name"],
            r["int_col"],
            r["int_col_32"],
            r["int_col_64"],
            r["bool_col"],
            r["float_col"],
            r["float_col_32"],
            r["float_col_64"],
            r["json_col"],
            r["datetime_col"],
            r["binary_col"],
            r["array_col"],
            r["array_col_nested"],
            r["array_col_32"],
            r["array_col_64"],
        )
        for r in result
    ]

    col_values.sort(key=lambda x: (x[1], x[0]))

    assert col_values == [
        ("dogs/dog1", "subobject") + new_col_values_empty,
        ("dogs/dog2", "subobject") + new_col_values_empty,
        ("dogs/dog3", "subobject") + new_col_values_empty,
        ("dogs/others/dog4", "subobject") + new_col_values_empty,
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_generator_with_new_columns_numpy(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    new_columns = {
        "int_col_32": Int32,
        "int_col_64": Int64,
        "float_col_32": Float32,
        "float_col_64": Float64,
        "int_float_col_32": Float32,
        "array_col_nested": Array(Array(Float32)),
        "array_col_32": Array(Float32),
        "array_col_64": Array(Float64),
        "array_int_float_col_32": Array(Float32),
        "array_empty_col_32": Array(Float32),
    }

    @udf(
        params=(C.name, C.parent),
        output={**DatasetRow.schema, **new_columns},
        method="generate_subobjects",
    )
    class Subobjects:
        def __init__(self):
            pass

        def generate_subobjects(self, name, parent):
            parent_path = name if not parent else f"{parent}/{name}"
            yield DatasetRow.create("subobject", size=50, parent=parent_path) + (
                np.int32(11),
                np.int64(12),
                np.float32(0.5),
                np.float64(0.5),
                np.int32(13),
                np.array([[0.5], [0.5]], dtype=np.float32),
                np.array([0.5, 0.5], dtype=np.float32),
                np.array([0.5, 0.5], dtype=np.float64),
                np.array([14, 15], dtype=np.int32),
                np.array([], dtype=np.float32),
            )

    DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).generate(
        Subobjects
    ).save("dogs_with_rows_and_signals")

    q = DatasetQuery(name="dogs_with_rows_and_signals", catalog=catalog)
    result = q.to_records()

    col_values = [
        (
            r["parent"],
            r["name"],
            r["int_col_32"],
            r["int_col_64"],
            r["float_col_32"],
            r["float_col_64"],
            r["int_float_col_32"],
            r["array_col_nested"],
            r["array_col_32"],
            r["array_col_64"],
            r["array_int_float_col_32"],
            r["array_empty_col_32"],
        )
        for r in result
    ]

    col_values.sort(key=lambda x: (x[1], x[0]))

    new_col_values = (
        11,
        12,
        0.5,
        0.5,
        13.0,
        [[0.5], [0.5]],
        [0.5, 0.5],
        [0.5, 0.5],
        [14.0, 15.0],
        [],
    )

    assert col_values == [
        ("dogs/dog1", "subobject") + new_col_values,
        ("dogs/dog2", "subobject") + new_col_values,
        ("dogs/dog3", "subobject") + new_col_values,
        ("dogs/others/dog4", "subobject") + new_col_values,
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
@pytest.mark.skip(reason="Test fails on other platforms because of db being locked")
def test_row_generator_with_new_columns_wrong_type(
    cloud_test_catalog, dogs_shadow_dataset
):
    catalog = cloud_test_catalog.catalog

    @udf(
        params=(C.name, C.parent),
        output={**DatasetRow.schema, "int_col": Int},
        method="generate_subobjects",
    )
    class Subobjects:
        def __init__(self):
            pass

        def generate_subobjects(self, name, parent):
            parent_path = name if not parent else f"{parent}/{name}"
            yield DatasetRow.create("subobject", size=50, parent=parent_path) + (0.5,)

    with pytest.raises(ValueError):
        DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).generate(
            Subobjects
        ).to_records()


@pytest.mark.parametrize("tree", [TARRED_TREE], indirect=True)
def test_index_tar(cloud_test_catalog):
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.index([ctc.src_uri])
    catalog.create_shadow_dataset("animals", [ctc.src_uri])

    q = DatasetQuery(name="animals", catalog=catalog).generate(index_tar)
    q.save("extracted")

    rows = list(catalog.ls_dataset_rows("extracted"))
    assert {row.name for row in rows} == {
        "animals.tar",
        "cat1",
        "cat2",
        "description",
        "dog1",
        "dog2",
        "dog3",
        "dog4",
    }

    offsets = [
        json.loads(row.location)[0]["offset"]
        for row in rows
        if row.name != "animals.tar"
    ]
    # Check that offsets are unique integers
    assert all(isinstance(offset, int) for offset in offsets)
    assert len(set(offsets)) == len(offsets)

    assert all(row.vtype == "tar" for row in rows if row.name != "animals.tar")


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_checksum_udf(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).add_signals(
        checksum
    )
    result = q.results()

    assert len(result) == 4


@pytest.mark.parametrize("tree", [TARRED_TREE], indirect=True)
def test_tar_loader(cloud_test_catalog):
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.index([ctc.src_uri])
    catalog.create_shadow_dataset("animals", [ctc.src_uri])
    q = DatasetQuery(name="animals", catalog=catalog).generate(index_tar)
    q.save("extracted")

    q = DatasetQuery(name="extracted", catalog=catalog).filter(C.parent.glob("*/cats*"))
    assert len(q.results()) == 2

    ds = q.extract(Object(to_str), "name")
    assert set(ds) == {("meow", "cat1"), ("mrow", "cat2")}


@pytest.mark.parametrize("tree", [{**DEFAULT_TREE, **TARRED_TREE}], indirect=True)
def test_simple_dataset_query(cloud_test_catalog):
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    data_storage = catalog.data_storage
    catalog.index([ctc.src_uri], index_processors=indexer_formats["tar-files"])
    catalog.create_shadow_dataset("ds1", [ctc.src_uri], recursive=True)
    DatasetQuery(ctc.src_uri, catalog=catalog).save("ds2")

    partial_id = data_storage.get_valid_partial_id(ctc.src_uri, "")
    data_storage = data_storage.clone(ctc.src_uri, partial_id)
    n = data_storage.nodes_table(ctc.src_uri, partial_id)
    nq = n.dataset_query().order_by(n.c.parent, n.c.name)
    ds_queries = [nq]
    for ds_name in ("ds1", "ds2"):
        d = data_storage.dataset_rows(ds_name)
        dq = d.select().order_by(d.c.parent, d.c.name)
        ds_queries.append(dq)

    ignore_cols = ["id", "parent_id"]
    node_ds, ds1, ds2 = (
        [
            {k: v for k, v in zip(DATASET_CORE_COLUMN_NAMES, r) if k not in ignore_cols}
            for r in data_storage.ddb.execute(q)
        ]
        for q in ds_queries
    )

    # everything except the id field should match
    assert ds1 == node_ds
    assert ds2 == node_ds
    assert [(r["parent"], r["name"]) for r in node_ds] == [
        ("", "animals.tar"),
        ("", "description"),
        ("animals.tar", "description"),
        ("animals.tar/cats", "cat1"),
        ("animals.tar/cats", "cat2"),
        ("animals.tar/dogs", "dog1"),
        ("animals.tar/dogs", "dog2"),
        ("animals.tar/dogs", "dog3"),
        ("animals.tar/dogs/others", "dog4"),
        ("cats", "cat1"),
        ("cats", "cat2"),
        ("dogs", "dog1"),
        ("dogs", "dog2"),
        ("dogs", "dog3"),
        ("dogs/others", "dog4"),
    ]


@pytest.mark.parametrize("tree", [{**DEFAULT_TREE, **TARRED_TREE}], indirect=True)
def test_similarity_search(cloud_test_catalog):
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.index([ctc.src_uri], index_processors=indexer_formats["tar-files"])

    @udf(
        params=(Object(to_str),),
        output={"embedding": Array(Float32)},
        method="embedding",
    )
    class TextEmbeddingGenerator:
        def embedding(self, text):
            return (text_embedding(text),)

    target_embedding, source, parent, name = (
        DatasetQuery(ctc.src_uri, catalog=catalog)
        .filter(~C.name.glob("*.tar"))
        .order_by(C.source, C.parent, C.name)
        .limit(1)
        .add_signals(TextEmbeddingGenerator())
        .select(C.embedding, C.source, C.parent, C.name)
        .results()[0]
    )
    q = (
        DatasetQuery(ctc.src_uri, catalog=catalog)
        .filter(
            ~C.name.glob("*.tar"),
            tuple_(C.source, C.parent, C.name) != (source, parent, name),
        )
        .add_signals(TextEmbeddingGenerator())
        .mutate(
            cos_dist=cosine_distance(C.embedding, target_embedding),
            eucl_dist=euclidean_distance(C.embedding, target_embedding),
        )
        .select(C.parent, C.name, C.cos_dist, C.eucl_dist)
        .order_by(C.source, C.parent, C.name)
    )
    count = q.count()
    assert count == 13

    result = q.results()
    expected = [
        ("animals.tar", "description", 0.0, 0.0),
        ("animals.tar/cats", "cat1", 0.8508677010357059, 1.9078358385397216),
        ("animals.tar/cats", "cat2", 0.8508677010357059, 1.9078358385397216),
        ("animals.tar/dogs", "dog1", 0.7875133863812602, 1.8750659656122843),
        ("animals.tar/dogs", "dog2", 0.7356502722055684, 1.775619888314893),
        ("animals.tar/dogs", "dog3", 0.7695916496857775, 1.8344983482620636),
        ("animals.tar/dogs/others", "dog4", 0.9789704524691446, 2.0531542018152322),
        ("cats", "cat1", 0.8508677010357059, 1.9078358385397216),
        ("cats", "cat2", 0.8508677010357059, 1.9078358385397216),
        ("dogs", "dog1", 0.7875133863812602, 1.8750659656122843),
        ("dogs", "dog2", 0.7356502722055684, 1.775619888314893),
        ("dogs", "dog3", 0.7695916496857775, 1.8344983482620636),
        ("dogs/others", "dog4", 0.9789704524691446, 2.0531542018152322),
    ]
    expected_diffs = [(p, n, 0.0, 0.0) for p, n, _, _ in expected]

    diffs = [
        (p2, n2, adjusted_float_diff(c1, c2, 1e-8), adjusted_float_diff(e1, e2, 1e-5))
        for (p1, n1, c1, e1), (p2, n2, c2, e2) in zip(result, expected)
    ]
    assert diffs == expected_diffs


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_subtract(cloud_test_catalog):
    from dql.dataset import DatasetRow as Row

    @udf(("name",), {"name_len": Int})
    def name_len(name):
        # A very simple udf.
        return (len(name),)

    catalog = cloud_test_catalog.catalog
    sources = [str(cloud_test_catalog.src_uri)]
    catalog.index(sources)

    src = cloud_test_catalog.src_uri
    catalog.create_shadow_dataset("dogs", [f"{src}/dogs/*"], recursive=True)
    catalog.create_shadow_dataset("cats", [f"{src}/cats/*"], recursive=True)

    dogs = DatasetQuery(name="dogs", catalog=catalog)
    cats = DatasetQuery(name="cats", catalog=catalog)

    (dogs | cats).save("dogs_cats")

    dogs_cats = DatasetQuery(name="dogs_cats", catalog=catalog)

    # subtracting dataset from dataset
    q = dogs_cats.subtract(dogs)
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == ["cat1", "cat2"]

    # subtracting dataset out of index
    q = DatasetQuery(f"{src}", catalog=catalog).subtract(cats)
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == [
        "description",
        "dog1",
        "dog2",
        "dog3",
        "dog4",
    ]

    # subtracting index out of index
    q = DatasetQuery(f"{src}", catalog=catalog).subtract(
        DatasetQuery(f"{src}/dogs/*", catalog=catalog)
    )
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == ["cat1", "cat2", "description"]

    # subtracting with filter
    q = (
        DatasetQuery(f"{src}", catalog=catalog)
        .filter(C.name.glob("dog*"))
        .subtract(cats)
    )
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == ["dog1", "dog2", "dog3", "dog4"]

    # chain subtracting
    q = dogs_cats.subtract(dogs).subtract(cats)
    result = q.results()
    count = q.count()
    assert len(result) == 0
    assert count == 0

    # filtering after subtract
    q = (
        DatasetQuery(f"{src}", catalog=catalog)
        .subtract(cats)
        .filter(C.name.glob("dog*"))
    )
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == ["dog1", "dog2", "dog3", "dog4"]

    # subtract with usage of udfs and union
    # simulates updating dataset with new changes in index and not re-calculating
    # all udfs, but only for those that are new
    cats.add_signals(name_len).save("cats_with_signals")
    cats_with_signals = DatasetQuery(name="cats_with_signals", catalog=catalog)
    q = (
        DatasetQuery(f"{src}", catalog=catalog)
        .subtract(cats_with_signals)
        .add_signals(name_len)
        .union(cats_with_signals)
    )
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == sorted(
        ["description", "dog1", "dog2", "dog3", "dog4", "cat1", "cat2"]
    )
    assert all(r.custom["name_len"] > 0 for r in result)

    # subtracting with source and target filter
    # only dog2 file has size less then 4
    all_except_dog2 = DatasetQuery(f"{src}", catalog=catalog).filter(C.size > 3)
    only_cats = dogs_cats.filter(C.name.glob("cat*"))
    q = all_except_dog2.subtract(only_cats)
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == ["description", "dog1", "dog3", "dog4"]

    # subtracting after union
    q = dogs.union(cats).subtract(dogs)
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == ["cat1", "cat2"]

    # subtract with itself
    q = dogs.subtract(dogs)
    result = q.results()
    count = q.count()
    assert len(result) == 0
    assert count == 0


def test_aggregate(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
    assert q.count() == 4
    assert q.sum(C.size) == 15
    assert q.avg(C.size) == 15 / 4
    assert q.min(C.size) == 3
    assert q.max(C.size) == 4


def test_group_by(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    q = (
        DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog)
        .group_by(C.parent)
        .select(
            C.parent,
            functions.count(),
            functions.sum(C.size),
            functions.avg(C.size),
            functions.min(C.size),
            functions.max(C.size),
        )
    )
    result = q.results()
    assert len(result) == 2

    result_dict = {r[0]: r[1:] for r in result}
    assert result_dict == {
        "dogs": (3, 11, 11 / 3, 3, 4),
        "dogs/others": (1, 4, 4, 4, 4),
    }


@pytest.mark.parametrize("tree", [WEBFORMAT_TREE], indirect=True)
def test_json_loader(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog

    @udf(
        params=(C.name,),
        output={"basename": String, "ext": String},
    )
    def split_name(name):
        return os.path.splitext(name)

    json_output = {"similarity": Float, "md5": String}

    @udf(
        params=("ext", LocalFilename("*.json")),
        output=json_output,
    )
    def attach_json(rows):
        # Locate json row and load its data
        json_data = None
        for ext, file_path in rows:
            if ext == ".json" and file_path:
                with open(file_path, encoding="utf8") as f:
                    json_data = json.load(f)

        # Attach json-loaded signals to all other rows in the group
        signals = []
        for ext, _ in rows:
            if json_data and ext != ".json":
                signals.append([json_data.get(k) for k in json_output])
            else:
                signals.append(None)

        return signals

    col_default_values = tuple(t.default_value() for t in json_output.values())

    expected = [
        ("f1.json", col_default_values[0], col_default_values[1]),
        ("f1.raw", 0.001, "deadbeef"),
        ("f2.json", col_default_values[0], col_default_values[1]),
        ("f2.raw", 0.005, "foobar"),
    ]

    q = (
        DatasetQuery(cloud_test_catalog.src_uri, catalog=catalog)
        .add_signals(split_name)
        .add_signals(attach_json, partition_by=C.basename)
        .select(C.name, C.similarity, C.md5)
        .order_by(C.name)
    )
    assert q.count() == 4
    res = q.results()
    assert len(res) == 4
    assert [r[0] for r in res] == [r[0] for r in expected]
    assert [r[1] for r in res] == pytest.approx([r[1] for r in expected])
    assert [r[2] for r in res] == [r[2] for r in expected]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_changed(cloud_test_catalog):  # noqa: PLR0915
    from dql.dataset import DatasetRow as Row

    now = datetime.now(timezone.utc)

    @udf(("name",), {"name_len": Int})
    def name_len(name):
        # A very simple udf.
        return (len(name),)

    def _index(catalog, uri, entries_updated_last_mod):
        """
        Custom indexing with setting some of the files to future last modified
        to simulate scenario where they are updated in cloud
        """
        from dql.storage import Status

        catalog.data_storage.create_storage_if_not_registered(uri)
        entries = []

        for entry in ENTRIES:
            if entry["name"] in entries_updated_last_mod:
                entry["last_modified"] = now + timedelta(days=2)
            else:
                entry["last_modified"] = now
            entries.append(entry)

        catalog.data_storage.init_id_generator(uri)
        partial_id = catalog.data_storage.get_next_partial_id(uri)
        catalog.data_storage = catalog.data_storage.clone(
            uri=uri, partial_id=partial_id
        )
        catalog.data_storage.init_db(uri, partial_id)
        insert_nodes(catalog.data_storage, entries)
        catalog.data_storage.mark_storage_indexed(
            uri, Status.COMPLETE, 4 * 60 * 60, partial_id=partial_id
        )

    catalog = cloud_test_catalog.catalog
    src = cloud_test_catalog.src_uri

    # first index
    _index(catalog, src, [])

    catalog.create_shadow_dataset("dogs", [f"{src}/dogs/*"], recursive=True)
    catalog.create_shadow_dataset("cats", [f"{src}/cats/*"], recursive=True)

    dogs = DatasetQuery(name="dogs", catalog=catalog)
    cats = DatasetQuery(name="cats", catalog=catalog)

    # re-index with simulating dog2 to be updated
    _index(catalog, src, ["dog2"])

    catalog.create_shadow_dataset("dogs_updated_1", [f"{src}/dogs/*"], recursive=True)

    # re-index with simulating dog1 and dog2 to be updated
    _index(catalog, src, ["dog1", "dog2"])

    catalog.create_shadow_dataset("dogs_updated_2", [f"{src}/dogs/*"], recursive=True)

    dogs_updated_1 = DatasetQuery(name="dogs_updated_1", catalog=catalog)
    dogs_updated_2 = DatasetQuery(name="dogs_updated_2", catalog=catalog)

    # changed between dataset and dataset
    q = dogs_updated_1.changed(dogs)
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == ["dog2"]

    q = dogs_updated_2.changed(dogs)
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == ["dog1", "dog2"]

    # changed between dataset and dataset, no change
    q = dogs.changed(dogs)
    result = q.results()
    count = q.count()
    assert len(result) == 0
    assert count == 0

    # changed between index and dataset
    q = DatasetQuery(f"{src}/dogs/*", catalog=catalog).changed(dogs)
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == ["dog1", "dog2"]

    # changed with filters
    q = (
        DatasetQuery(f"{src}", catalog=catalog)
        .filter(C.name.glob("dog*"))
        .changed(dogs)
    )
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == ["dog1", "dog2"]

    # chain changed
    q = dogs_updated_2.changed(dogs).changed(dogs_updated_1)
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == ["dog1"]

    # filtering after changed
    q = (
        DatasetQuery(f"{src}/dogs/*", catalog=catalog)
        .changed(dogs)
        .filter(C.name.glob("dog1*"))
    )
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == ["dog1"]

    # changed with usage of udfs
    q = (
        DatasetQuery(f"{src}/dogs/*", catalog=catalog)
        .changed(dogs)
        .add_signals(name_len)
    )
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == sorted(["dog1", "dog2"])
    assert all(r.custom["name_len"] > 0 for r in result)

    # changed after union
    q = dogs_updated_2.union(cats).changed(dogs)
    result = q.results(row_factory=Row.from_result_row)
    assert sorted([r.name for r in result]) == ["dog1", "dog2"]

    # changed with itself
    q = dogs.changed(dogs)
    result = q.results()
    count = q.count()
    assert len(result) == 0
    assert count == 0


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_to_records(simple_ds_query):
    assert simple_ds_query.to_records() == SIMPLE_DS_QUERY_RECORDS


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_to_pandas(simple_ds_query):
    import pandas as pd

    df = simple_ds_query.to_pandas()
    expected = pd.DataFrame.from_records(SIMPLE_DS_QUERY_RECORDS)
    assert (df == expected).all(axis=None)


@pytest.mark.parametrize("save", [True, False])
@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_udf_after_union(cloud_test_catalog, save):
    catalog = cloud_test_catalog.catalog
    sources = [cloud_test_catalog.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources)
    catalog.create_shadow_dataset("animals", globs, recursive=True)

    @udf(("name",), {"name_len": Int})
    def name_len(name):
        # A very simple udf.
        return (len(name),)

    ds_cats = DatasetQuery(name="animals", catalog=catalog).filter(
        C.parent.glob("cats*")
    )
    if save:
        ds_cats.save("cats")
        ds_cats = DatasetQuery(name="cats", catalog=catalog)
    ds_dogs = DatasetQuery(name="animals", catalog=catalog).filter(
        C.parent.glob("dogs*")
    )
    if save:
        ds_dogs.save("dogs")
        ds_dogs = DatasetQuery(name="dogs", catalog=catalog)

    def get_result(query):
        result = [(r["name"], r["name_len"]) for r in query.to_records()]
        result.sort()
        return result

    q = ds_cats.union(ds_dogs).add_signals(name_len)
    result1 = get_result(q)
    assert result1 == [
        ("cat1", 4),
        ("cat2", 4),
        ("dog1", 4),
        ("dog2", 4),
        ("dog3", 4),
        ("dog4", 4),
    ]

    result2 = get_result(q.union(q))
    assert result2 == [
        ("cat1", 4),
        ("cat1", 4),
        ("cat2", 4),
        ("cat2", 4),
        ("dog1", 4),
        ("dog1", 4),
        ("dog2", 4),
        ("dog2", 4),
        ("dog3", 4),
        ("dog3", 4),
        ("dog4", 4),
        ("dog4", 4),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_udf_after_union_same_rows_with_mutate(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    sources = [cloud_test_catalog.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources)
    catalog.create_shadow_dataset("animals", globs, recursive=True)

    @udf(("name",), {"name_len": Int})
    def name_len(name):
        # A very simple udf.
        return (len(name),)

    q_base = DatasetQuery(name="animals", catalog=catalog).filter(
        C.parent.glob("dogs*")
    )
    q1 = q_base.mutate(x=sqlalchemy.cast(C.name + "_1", String()))
    q2 = q_base.mutate(x=sqlalchemy.cast(C.name + "_2", String()))

    def get_result(query):
        result = [(r["name"], r["x"], r["name_len"]) for r in query.to_records()]
        result.sort()
        return result

    q = q1.union(q2).add_signals(name_len)
    result1 = get_result(q)
    assert result1 == [
        ("dog1", "dog1_1", 4),
        ("dog1", "dog1_2", 4),
        ("dog2", "dog2_1", 4),
        ("dog2", "dog2_2", 4),
        ("dog3", "dog3_1", 4),
        ("dog3", "dog3_2", 4),
        ("dog4", "dog4_1", 4),
        ("dog4", "dog4_2", 4),
    ]

    result2 = get_result(q.union(q))
    assert result2 == [
        ("dog1", "dog1_1", 4),
        ("dog1", "dog1_1", 4),
        ("dog1", "dog1_2", 4),
        ("dog1", "dog1_2", 4),
        ("dog2", "dog2_1", 4),
        ("dog2", "dog2_1", 4),
        ("dog2", "dog2_2", 4),
        ("dog2", "dog2_2", 4),
        ("dog3", "dog3_1", 4),
        ("dog3", "dog3_1", 4),
        ("dog3", "dog3_2", 4),
        ("dog3", "dog3_2", 4),
        ("dog4", "dog4_1", 4),
        ("dog4", "dog4_1", 4),
        ("dog4", "dog4_2", 4),
        ("dog4", "dog4_2", 4),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware,tree",
    [("s3", True, NUM_TREE)],
    indirect=True,
)
def test_udf_after_limit(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    sources = [cloud_test_catalog.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources)
    catalog.create_shadow_dataset("animals", globs, recursive=True)

    @udf(("name",), {"name_int": Int})
    def name_int(name):
        try:
            return (int(name),)
        except ValueError:
            return 0

    def get_result(query):
        return (
            query.limit(100)
            .add_signals(name_int)
            .select("name", "name_int")
            .to_records()
        )

    expected = [{"name": f"{i:06d}", "name_int": i} for i in range(100)]
    ds = DatasetQuery(name="animals", catalog=catalog)
    # We test a few different orderings here, because we've had strange
    # bugs in the past where calling add_signals() after limit() gave us
    # incorrect results on clickhouse cloud.
    # See https://github.com/iterative/dql/issues/940
    assert get_result(ds.order_by("name")) == expected
    assert len(get_result(ds.order_by("random"))) == 100
    assert len(get_result(ds)) == 100


@pytest.mark.parametrize("indirect", [True, False])
def test_dataset_dependencies_one_storage_as_dependency(
    cloud_test_catalog, listed_bucket, indirect
):
    ds_name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog
    storage = catalog.get_storage(cloud_test_catalog.src_uri)
    path = f"{cloud_test_catalog.src_uri}/cats"

    DatasetQuery(path=path, catalog=catalog).save(ds_name)

    assert [
        dataset_dependency_asdict(d)
        for d in catalog.get_dataset_dependencies(ds_name, indirect=indirect)
    ] == [
        {
            "id": ANY,
            "type": DatasetDependencyType.STORAGE,
            "name": storage.uri,
            "version": storage.timestamp_str,
            "created_at": isoparse(storage.timestamp_str),
            "dependencies": [],
        }
    ]


@pytest.mark.parametrize("indirect", [True, False])
def test_dataset_dependencies_one_shadow_dataset_as_dependency(
    cloud_test_catalog, dogs_shadow_dataset, indirect
):
    ds_name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog
    storage = catalog.get_storage(cloud_test_catalog.src_uri)

    DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).save(ds_name)

    expected = [
        {
            "id": ANY,
            "type": DatasetDependencyType.DATASET,
            "name": dogs_shadow_dataset.name,
            "version": None,
            "created_at": dogs_shadow_dataset.created_at,
            "dependencies": [],
        }
    ]

    if indirect:
        expected[0]["dependencies"] = [
            {
                "id": ANY,
                "type": DatasetDependencyType.STORAGE,
                "name": storage.uri,
                "version": storage.timestamp_str,
                "created_at": isoparse(storage.timestamp_str),
                "dependencies": [],
            }
        ]

    assert [
        dataset_dependency_asdict(d)
        for d in catalog.get_dataset_dependencies(ds_name, indirect=indirect)
    ] == expected

    catalog.remove_dataset(dogs_shadow_dataset.name)
    # None means dependency was there but was removed in the meantime
    assert catalog.get_dataset_dependencies(ds_name) == [None]


@pytest.mark.parametrize("indirect", [True, False])
def test_dataset_dependencies_one_registered_dataset_as_dependency(
    cloud_test_catalog, dogs_registered_dataset, indirect
):
    ds_name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog
    storage = catalog.get_storage(cloud_test_catalog.src_uri)

    DatasetQuery(name=dogs_registered_dataset.name, catalog=catalog).save(ds_name)

    expected = [
        {
            "id": ANY,
            "type": DatasetDependencyType.DATASET,
            "name": dogs_registered_dataset.name,
            "version": str(1),
            "created_at": dogs_registered_dataset.get_version(1).created_at,
            "dependencies": [],
        }
    ]

    if indirect:
        expected[0]["dependencies"] = [
            {
                "id": ANY,
                "type": DatasetDependencyType.STORAGE,
                "name": storage.uri,
                "version": storage.timestamp_str,
                "created_at": isoparse(storage.timestamp_str),
                "dependencies": [],
            }
        ]

    assert [
        dataset_dependency_asdict(d)
        for d in catalog.get_dataset_dependencies(ds_name, indirect=indirect)
    ] == expected

    catalog.remove_dataset(dogs_registered_dataset.name, force=True)
    # None means dependency was there but was removed in the meantime
    assert catalog.get_dataset_dependencies(ds_name) == [None]


@pytest.mark.parametrize("method", ["union", "join"])
def test_dataset_dependencies_multiple_direct_dataset_dependencies(
    cloud_test_catalog, dogs_registered_dataset, cats_registered_dataset, method
):
    # multiple direct dataset dependencies can be achieved with methods that are
    # combining multiple DatasetQuery instances into new one like union or join
    ds_name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog
    storage = catalog.get_storage(cloud_test_catalog.src_uri)

    dogs = DatasetQuery(name=dogs_registered_dataset.name, catalog=catalog)
    cats = DatasetQuery(name=cats_registered_dataset.name, catalog=catalog)

    if method == "union":
        dogs.union(cats).save(ds_name)
    else:
        dogs.join(cats, "name").save(ds_name)

    storage_depenedncy = {
        "id": ANY,
        "type": DatasetDependencyType.STORAGE,
        "name": storage.uri,
        "version": storage.timestamp_str,
        "created_at": isoparse(storage.timestamp_str),
        "dependencies": [],
    }

    expected = [
        {
            "id": ANY,
            "type": DatasetDependencyType.DATASET,
            "name": dogs_registered_dataset.name,
            "version": str(1),
            "created_at": dogs_registered_dataset.get_version(1).created_at,
            "dependencies": [storage_depenedncy],
        },
        {
            "id": ANY,
            "type": DatasetDependencyType.DATASET,
            "name": cats_registered_dataset.name,
            "version": str(1),
            "created_at": cats_registered_dataset.get_version(1).created_at,
            "dependencies": [storage_depenedncy],
        },
    ]

    assert sorted(
        [
            dataset_dependency_asdict(d)
            for d in catalog.get_dataset_dependencies(ds_name, indirect=True)
        ],
        key=lambda d: d["name"],
    ) == sorted(expected, key=lambda d: d["name"])

    # check when removing one dependency
    catalog.remove_dataset(dogs_registered_dataset.name, force=True)
    expected[0] = None
    expected[1]["dependencies"] = []

    assert sorted(
        [
            dataset_dependency_asdict(d)
            for d in catalog.get_dataset_dependencies(ds_name)
        ],
        key=lambda d: d["name"] if d else "",
    ) == sorted(expected, key=lambda d: d["name"] if d else "")

    # check when removing the other dependency
    catalog.remove_dataset(cats_registered_dataset.name, force=True)
    assert catalog.get_dataset_dependencies(ds_name) == [None, None]


def test_dataset_dependencies_multiple_union(
    cloud_test_catalog, dogs_registered_dataset, cats_registered_dataset
):
    ds_name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog
    storage = catalog.get_storage(cloud_test_catalog.src_uri)

    dogs = DatasetQuery(name=dogs_registered_dataset.name, catalog=catalog)
    cats = DatasetQuery(name=cats_registered_dataset.name, catalog=catalog)
    dogs_other = DatasetQuery(name=dogs_registered_dataset.name, catalog=catalog)

    dogs.union(cats).union(dogs_other).save(ds_name)

    storage_depenedncy = {
        "id": ANY,
        "type": DatasetDependencyType.STORAGE,
        "name": storage.uri,
        "version": storage.timestamp_str,
        "created_at": isoparse(storage.timestamp_str),
        "dependencies": [],
    }

    expected = [
        {
            "id": ANY,
            "type": DatasetDependencyType.DATASET,
            "name": dogs_registered_dataset.name,
            "version": str(1),
            "created_at": dogs_registered_dataset.get_version(1).created_at,
            "dependencies": [storage_depenedncy],
        },
        {
            "id": ANY,
            "type": DatasetDependencyType.DATASET,
            "name": cats_registered_dataset.name,
            "version": str(1),
            "created_at": cats_registered_dataset.get_version(1).created_at,
            "dependencies": [storage_depenedncy],
        },
    ]

    assert sorted(
        [
            dataset_dependency_asdict(d)
            for d in catalog.get_dataset_dependencies(ds_name, indirect=True)
        ],
        key=lambda d: d["name"],
    ) == sorted(expected, key=lambda d: d["name"])
