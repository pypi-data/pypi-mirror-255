import uuid
from json import dumps
from unittest.mock import ANY, patch

import pytest
import sqlalchemy as sa
from dateutil.parser import isoparse

from dql.catalog.catalog import DATASET_INTERNAL_ERROR_MESSAGE
from dql.dataset import DatasetDependencyType
from dql.dataset import Status as DatasetStatus
from dql.error import DatasetNotFoundError
from dql.query import DatasetQuery, udf
from dql.sql.types import (
    JSON,
    Array,
    Binary,
    Boolean,
    Float,
    Float32,
    Float64,
    Int,
    Int32,
    Int64,
    SQLType,
    String,
)

from ..utils import dataset_dependency_asdict


def add_column(engine, table_name, column, catalog):
    # Simple method that adds new column to a table, with default value if specified
    column_name = column.compile(dialect=engine.dialect)
    column_type = column.type.compile(engine.dialect)
    if column.default:
        query_str = "ALTER TABLE {} ADD COLUMN {} {} DEFAULT {}".format(
            table_name,
            column_name,
            column_type,
            column.default.arg,
        )
    else:
        query_str = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
    catalog.data_storage.ddb.execute_str(query_str)


@pytest.fixture
def empty_shadow_dataset(listed_bucket, cloud_test_catalog):
    shadow_dataset_name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog
    catalog.create_shadow_dataset(shadow_dataset_name, [], populate=False)
    return catalog.data_storage.get_dataset(shadow_dataset_name)


def test_get_dataset(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    dataset = catalog.get_dataset(dogs_shadow_dataset.name)
    assert dataset.name == dogs_shadow_dataset.name

    with pytest.raises(DatasetNotFoundError):
        catalog.get_dataset("wrong name")


# Returns None if the table does not exist
def get_table_row_count(data_storage, table_name):
    if not data_storage.ddb.has_table(table_name):
        return None
    query = sa.select(sa.func.count()).select_from(sa.table(table_name))
    return next(data_storage.ddb.execute(query), (None,))[0]


def test_creating_shadow_dataset(listed_bucket, cloud_test_catalog):
    shadow_dataset_name = uuid.uuid4().hex
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    dataset = catalog.create_shadow_dataset(
        shadow_dataset_name, [f"{src_uri}/dogs/*"], recursive=True
    )

    assert dataset.name == shadow_dataset_name
    assert dataset.description is None
    assert dataset.versions is None
    assert dataset.labels == []
    assert dataset.shadow is True
    assert dataset.status == DatasetStatus.COMPLETE
    assert dataset.created_at
    assert dataset.finished_at
    assert dataset.error_message == ""
    assert dataset.error_stack == ""
    assert dataset.script_output == ""
    assert dataset.sources == f"{src_uri}/dogs/*"
    assert dataset.query_script == ""

    default_dataset_custom_column_types = {
        c.name: c.type.__class__
        for c in catalog.data_storage.dataset_row_cls.default_columns()
        if isinstance(c.type, SQLType)
    }
    assert dataset.custom_column_types == default_dataset_custom_column_types

    dataset_table_name = catalog.data_storage.dataset_table_name(dataset.name)
    assert get_table_row_count(catalog.data_storage, dataset_table_name)


def test_creating_shadow_dataset_failed(listed_bucket, cloud_test_catalog):
    shadow_dataset_name = uuid.uuid4().hex
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog
    with patch.object(
        catalog.data_storage.__class__,
        "insert_into_shadow_dataset",
        side_effect=RuntimeError("Error"),
    ) as _:
        with pytest.raises(RuntimeError):
            catalog.create_shadow_dataset(
                shadow_dataset_name, [f"{src_uri}/dogs/*"], recursive=True
            )
    dataset = catalog.data_storage.get_dataset(shadow_dataset_name)

    assert dataset.name == shadow_dataset_name
    assert dataset.status == DatasetStatus.FAILED
    assert dataset.created_at
    assert dataset.finished_at
    assert dataset.error_message == DATASET_INTERNAL_ERROR_MESSAGE
    assert dataset.error_stack
    assert dataset.sources == f"{src_uri}/dogs/*"
    assert dataset.query_script == ""

    dataset_table_name = catalog.data_storage.dataset_table_name(dataset.name)
    assert get_table_row_count(catalog.data_storage, dataset_table_name) == 0


def test_creating_empty_dataset(listed_bucket, cloud_test_catalog):
    shadow_dataset_name = uuid.uuid4().hex
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    dataset = catalog.create_shadow_dataset(
        shadow_dataset_name, [f"{src_uri}/dogs/*"], recursive=True, populate=False
    )

    assert dataset.name == shadow_dataset_name
    assert dataset.status == DatasetStatus.CREATED
    assert dataset.shadow is True
    assert dataset.created_at
    assert not dataset.finished_at

    dataset_table_name = catalog.data_storage.dataset_table_name(dataset.name)
    assert get_table_row_count(catalog.data_storage, dataset_table_name) is None


def test_creating_dataset_after_empty(listed_bucket, cloud_test_catalog):
    shadow_dataset_name = uuid.uuid4().hex
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    dataset = catalog.create_shadow_dataset(
        shadow_dataset_name, [f"{src_uri}/dogs/*"], recursive=True, populate=False
    )

    assert dataset.status == DatasetStatus.CREATED

    dataset = catalog.create_shadow_dataset(
        shadow_dataset_name, [f"{src_uri}/dogs/*"], recursive=True
    )

    assert dataset.status == DatasetStatus.COMPLETE
    assert dataset.created_at
    assert dataset.finished_at

    dataset_table_name = catalog.data_storage.dataset_table_name(dataset.name)
    assert get_table_row_count(catalog.data_storage, dataset_table_name)


def test_creating_shadow_dataset_whole_bucket(listed_bucket, cloud_test_catalog):
    shadow_dataset_name_1 = uuid.uuid4().hex
    shadow_dataset_name_2 = uuid.uuid4().hex
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    catalog.create_shadow_dataset(shadow_dataset_name_1, [f"{src_uri}"], recursive=True)
    catalog.create_shadow_dataset(
        shadow_dataset_name_2, [f"{src_uri}/"], recursive=True
    )

    expected_rows = {
        "description",
        "cat1",
        "cat2",
        "dog1",
        "dog2",
        "dog3",
        "dog4",
    }

    assert {
        r.name for r in catalog.ls_dataset_rows(shadow_dataset_name_1)
    } == expected_rows

    assert {
        r.name for r in catalog.ls_dataset_rows(shadow_dataset_name_2)
    } == expected_rows


def test_registering_dataset(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    catalog.register_shadow_dataset(
        dogs_shadow_dataset.name,
        description="dogs dataset",
        labels=["dogs", "dataset"],
    )

    dataset = catalog.data_storage.get_dataset(dogs_shadow_dataset.name)
    dataset_table_name = catalog.data_storage.dataset_table_name(dataset.name, 1)
    assert dataset.name == dogs_shadow_dataset.name
    assert dataset.description == "dogs dataset"
    assert dataset.versions_values == [1]
    assert dataset.labels == ["dogs", "dataset"]
    assert dataset.shadow is False
    assert dataset.status == DatasetStatus.COMPLETE
    assert dataset.sources == ""
    assert dataset.query_script == ""
    assert dataset.versions[0].sources == dogs_shadow_dataset.sources
    assert dataset.versions[0].query_script == dogs_shadow_dataset.query_script
    assert get_table_row_count(catalog.data_storage, dataset_table_name)


def test_registering_dataset_with_new_name(cloud_test_catalog, dogs_shadow_dataset):
    new_dataset_name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog

    catalog.register_shadow_dataset(
        dogs_shadow_dataset.name,
        registered_name=new_dataset_name,
        description="dogs dataset",
        labels=["dogs", "dataset"],
    )
    dataset = catalog.data_storage.get_dataset(new_dataset_name)
    assert dataset
    dataset_table_name = catalog.data_storage.dataset_table_name(dataset.name, 1)
    assert dataset.name == new_dataset_name
    assert get_table_row_count(catalog.data_storage, dataset_table_name)


def test_registering_dataset_with_custom_version(
    cloud_test_catalog, dogs_shadow_dataset
):
    catalog = cloud_test_catalog.catalog

    catalog.register_shadow_dataset(
        dogs_shadow_dataset.name,
        version=5,
        description="dogs dataset",
        labels=["dogs", "dataset"],
    )

    dataset = catalog.data_storage.get_dataset(dogs_shadow_dataset.name)
    assert dataset.versions_values == [5]


def test_registering_dataset_as_version_of_another_registered(
    cloud_test_catalog, dogs_registered_dataset, cats_shadow_dataset
):
    catalog = cloud_test_catalog.catalog

    cats_shadow_dep = catalog.get_dataset_dependencies(cats_shadow_dataset.name)

    catalog.register_shadow_dataset(
        cats_shadow_dataset.name,
        registered_name=dogs_registered_dataset.name,
        version=3,
    )

    dogs_dataset = catalog.data_storage.get_dataset(dogs_registered_dataset.name)
    assert dogs_dataset.versions_values == [1, 3]

    assert dogs_dataset.sources == ""
    assert dogs_dataset.query_script == ""
    dogs_dataset.sort_versions()
    assert dogs_dataset.versions[1].sources == cats_shadow_dataset.sources
    assert dogs_dataset.versions[1].query_script == cats_shadow_dataset.query_script

    # checking newly created dogs version 3 data
    assert {
        r.name for r in catalog.ls_dataset_rows(dogs_registered_dataset.name, version=3)
    } == {
        "cat1",
        "cat2",
    }

    # assert cats shadow dataset is removed
    cats_dataset_name = catalog.data_storage.dataset_table_name(
        cats_shadow_dataset.name
    )
    with pytest.raises(DatasetNotFoundError):
        catalog.data_storage.get_dataset(cats_shadow_dataset.name)
    assert get_table_row_count(catalog.data_storage, cats_dataset_name) is None

    dogs_registered_dep = catalog.get_dataset_dependencies(
        dogs_registered_dataset.name, 3
    )

    assert set(cats_shadow_dep) == set(dogs_registered_dep)


def test_registering_dataset_with_custom_column_types(
    cloud_test_catalog, dogs_shadow_dataset
):
    catalog = cloud_test_catalog.catalog

    catalog.data_storage.update_dataset(
        dogs_shadow_dataset.name, custom_column_types={"name_len": {"type": "Int"}}
    )

    catalog.register_shadow_dataset(
        dogs_shadow_dataset.name,
        description="dogs dataset",
        labels=["dogs", "dataset"],
    )

    dataset = catalog.data_storage.get_dataset(dogs_shadow_dataset.name)
    assert dataset.name == dogs_shadow_dataset.name
    assert dataset.custom_column_types == {"name_len": Int}
    assert dataset.versions[0].custom_column_types == {"name_len": Int}


def test_removing_dataset(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog

    dataset_table_name = catalog.data_storage.dataset_table_name(
        dogs_shadow_dataset.name
    )
    assert get_table_row_count(catalog.data_storage, dataset_table_name)

    catalog.remove_dataset(dogs_shadow_dataset.name)
    with pytest.raises(DatasetNotFoundError):
        catalog.data_storage.get_dataset(dogs_shadow_dataset.name)

    assert get_table_row_count(catalog.data_storage, dataset_table_name) is None

    assert (
        catalog.data_storage.get_direct_dataset_dependencies(dogs_shadow_dataset) == []
    )


def test_edit_dataset(cloud_test_catalog, dogs_registered_dataset):
    dataset_old_name = dogs_registered_dataset.name
    dataset_new_name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog

    catalog.edit_dataset(
        dogs_registered_dataset.name,
        new_name=dataset_new_name,
        description="new description",
        labels=["cats", "birds"],
    )

    dataset = catalog.data_storage.get_dataset(dataset_new_name)
    assert dataset.versions_values == [1]
    assert dataset.name == dataset_new_name
    assert dataset.description == "new description"
    assert dataset.labels == ["cats", "birds"]

    # check if dataset tables are renamed correctly
    old_dataset_table_name = catalog.data_storage.dataset_table_name(
        dataset_old_name, version=1
    )
    new_dataset_table_name = catalog.data_storage.dataset_table_name(
        dataset_new_name, version=1
    )
    assert get_table_row_count(catalog.data_storage, old_dataset_table_name) is None
    assert get_table_row_count(catalog.data_storage, new_dataset_table_name)


def test_edit_dataset_same_name(cloud_test_catalog, dogs_registered_dataset):
    dataset_old_name = dogs_registered_dataset.name
    dataset_new_name = dogs_registered_dataset.name
    catalog = cloud_test_catalog.catalog

    catalog.edit_dataset(dogs_registered_dataset.name, new_name=dataset_new_name)

    dataset = catalog.data_storage.get_dataset(dataset_new_name)
    assert dataset.name == dataset_new_name

    # check if dataset tables are renamed correctly
    old_dataset_table_name = catalog.data_storage.dataset_table_name(
        dataset_old_name, version=1
    )
    new_dataset_table_name = catalog.data_storage.dataset_table_name(
        dataset_new_name, version=1
    )
    assert get_table_row_count(catalog.data_storage, old_dataset_table_name)
    assert get_table_row_count(catalog.data_storage, new_dataset_table_name)


def test_edit_dataset_remove_labels_and_description(
    cloud_test_catalog, dogs_registered_dataset
):
    dataset_new_name = uuid.uuid4().hex
    catalog = cloud_test_catalog.catalog

    catalog.edit_dataset(
        dogs_registered_dataset.name,
        new_name=dataset_new_name,
        description="",
        labels=[],
    )

    dataset = catalog.data_storage.get_dataset(dataset_new_name)
    assert dataset.versions_values == [1]
    assert dataset.name == dataset_new_name
    assert dataset.description == ""
    assert dataset.labels == []


def test_ls_dataset_rows(cloud_test_catalog, dogs_registered_dataset):
    catalog = cloud_test_catalog.catalog

    assert {
        r.name for r in catalog.ls_dataset_rows(dogs_registered_dataset.name, version=1)
    } == {
        "dog1",
        "dog2",
        "dog3",
        "dog4",
    }


def test_ls_dataset_rows_with_limit_offset(cloud_test_catalog, dogs_registered_dataset):
    catalog = cloud_test_catalog.catalog

    # these should be sorted by id already
    all_rows = list(
        catalog.ls_dataset_rows(
            dogs_registered_dataset.name,
            version=1,
        )
    )

    assert {
        r.name
        for r in catalog.ls_dataset_rows(
            dogs_registered_dataset.name,
            version=1,
            offset=2,
            limit=1,
        )
    } == {
        all_rows[2].name,
    }


def test_ls_dataset_rows_with_custom_columns(
    cloud_test_catalog, dogs_registered_dataset
):
    catalog = cloud_test_catalog.catalog
    int_example = 25

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
            int_example.to_bytes(2, "big"),
        )

    (
        DatasetQuery(name=dogs_registered_dataset.name, catalog=catalog)
        .add_signals(test_types)
        .save("dogs_custom_columns")
    )

    catalog.register_shadow_dataset("dogs_custom_columns")

    for r in catalog.ls_dataset_rows(
        "dogs_custom_columns", version=1, custom_columns=True
    ):
        assert r.custom == {
            "int_col": 5,
            "int_col_32": 5,
            "int_col_64": 5,
            "float_col": 0.5,
            "float_col_32": 0.5,
            "float_col_64": 0.5,
            "array_col": [0.5],
            "array_col_nested": [[0.5], [0.5]],
            "array_col_32": [0.5],
            "array_col_64": [0.5],
            "string_col": "s",
            "bool_col": True,
            "json_col": dumps({"a": 1}),
            "binary_col": int_example.to_bytes(2, "big"),
        }


def test_merge_datasets_shadow_to_registered(
    cloud_test_catalog, dogs_registered_dataset, cats_shadow_dataset
):
    catalog = cloud_test_catalog.catalog
    catalog.merge_datasets(
        cats_shadow_dataset.name, dogs_registered_dataset.name, dst_version=2
    )

    dogs_dataset = catalog.data_storage.get_dataset(dogs_registered_dataset.name)
    assert dogs_dataset.versions_values == [1, 2]

    # making sure version 1 is not changed
    assert {
        r.name for r in catalog.ls_dataset_rows(dogs_registered_dataset.name, version=1)
    } == {
        "dog1",
        "dog2",
        "dog3",
        "dog4",
    }

    assert {
        r.name for r in catalog.ls_dataset_rows(dogs_registered_dataset.name, version=2)
    } == {
        "dog1",
        "dog2",
        "dog3",
        "dog4",
        "cat1",
        "cat2",
    }

    cats_dep = catalog.get_dataset_dependencies(cats_shadow_dataset.name)
    dogs_old_dep = catalog.get_dataset_dependencies(dogs_registered_dataset.name, 1)
    dogs_new_dep = catalog.get_dataset_dependencies(dogs_registered_dataset.name, 2)

    assert set(dogs_new_dep) == set(cats_dep + dogs_old_dep)


def test_merge_datasets_registered_to_registered(
    cloud_test_catalog, dogs_registered_dataset, cats_registered_dataset
):
    catalog = cloud_test_catalog.catalog
    catalog.merge_datasets(
        cats_registered_dataset.name,
        dogs_registered_dataset.name,
        src_version=1,
        dst_version=2,
    )

    dogs_dataset = catalog.data_storage.get_dataset(dogs_registered_dataset.name)
    assert dogs_dataset.versions_values == [1, 2]

    assert {
        r.name for r in catalog.ls_dataset_rows(dogs_registered_dataset.name, version=2)
    } == {
        "dog1",
        "dog2",
        "dog3",
        "dog4",
        "cat1",
        "cat2",
    }

    cats_dep = catalog.get_dataset_dependencies(cats_registered_dataset.name, 1)
    dogs_old_dep = catalog.get_dataset_dependencies(dogs_registered_dataset.name, 1)
    dogs_new_dep = catalog.get_dataset_dependencies(dogs_registered_dataset.name, 2)

    assert set(dogs_new_dep) == set(cats_dep + dogs_old_dep)


def test_merge_datasets_shadow_to_shadow(
    cloud_test_catalog, dogs_shadow_dataset, cats_shadow_dataset
):
    catalog = cloud_test_catalog.catalog
    dogs_old_dep = catalog.get_dataset_dependencies(dogs_shadow_dataset.name)
    catalog.merge_datasets(
        cats_shadow_dataset.name,
        dogs_shadow_dataset.name,
    )

    dogs_dataset = catalog.data_storage.get_dataset(dogs_shadow_dataset.name)
    assert dogs_dataset.shadow is True  # dataset stays shadow

    assert {r.name for r in catalog.ls_dataset_rows(dogs_shadow_dataset.name)} == {
        "dog1",
        "dog2",
        "dog3",
        "dog4",
        "cat1",
        "cat2",
    }

    cats_dep = catalog.get_dataset_dependencies(cats_shadow_dataset.name)
    dogs_new_dep = catalog.get_dataset_dependencies(dogs_shadow_dataset.name)

    assert set(dogs_new_dep) == set(cats_dep + dogs_old_dep)


def test_merge_datasets_registered_to_shadow(
    cloud_test_catalog, dogs_shadow_dataset, cats_registered_dataset
):
    catalog = cloud_test_catalog.catalog
    dogs_old_dep = catalog.get_dataset_dependencies(dogs_shadow_dataset.name)
    catalog.merge_datasets(
        cats_registered_dataset.name,
        dogs_shadow_dataset.name,
        src_version=1,
    )

    dogs_dataset = catalog.data_storage.get_dataset(dogs_shadow_dataset.name)
    assert dogs_dataset.shadow is True  # dataset stays shadow

    assert {r.name for r in catalog.ls_dataset_rows(dogs_shadow_dataset.name)} == {
        "dog1",
        "dog2",
        "dog3",
        "dog4",
        "cat1",
        "cat2",
    }

    cats_dep = catalog.get_dataset_dependencies(cats_registered_dataset.name, 1)
    dogs_new_dep = catalog.get_dataset_dependencies(dogs_shadow_dataset.name)

    assert set(dogs_new_dep) == set(cats_dep + dogs_old_dep)


def test_merge_datasets_shadow_to_empty_shadow_without_rows_table(
    cloud_test_catalog, empty_shadow_dataset, cats_shadow_dataset
):
    catalog = cloud_test_catalog.catalog
    catalog.merge_datasets(
        cats_shadow_dataset.name,
        empty_shadow_dataset.name,
    )

    empty_dataset = catalog.data_storage.get_dataset(empty_shadow_dataset.name)
    assert empty_dataset.shadow is True  # dataset stays shadow

    assert {r.name for r in catalog.ls_dataset_rows(empty_shadow_dataset.name)} == {
        "cat1",
        "cat2",
    }

    cats_dep = catalog.get_dataset_dependencies(cats_shadow_dataset.name)
    empty_dataset_dep = catalog.get_dataset_dependencies(empty_shadow_dataset.name)

    assert set(cats_dep) == set(empty_dataset_dep)


def test_merge_datasets_empty_shadow_without_table_to_shadow(
    cloud_test_catalog, empty_shadow_dataset, cats_shadow_dataset
):
    catalog = cloud_test_catalog.catalog
    catalog.merge_datasets(
        empty_shadow_dataset.name,
        cats_shadow_dataset.name,
    )

    cat_dataset = catalog.data_storage.get_dataset(cats_shadow_dataset.name)
    assert cat_dataset.shadow is True  # dataset stays shadow

    assert {r.name for r in catalog.ls_dataset_rows(cats_shadow_dataset.name)} == {
        "cat1",
        "cat2",
    }


def test_dataset_row(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog
    data_storage = catalog.data_storage
    dr = data_storage.dataset_rows(dogs_shadow_dataset.name)
    first_id = next(data_storage.ddb.execute(sa.select(dr.c.id).limit(1)), (None,))[0]
    row = catalog.dataset_row(dogs_shadow_dataset.name, first_id)
    assert row.id == first_id


@pytest.mark.parametrize("tree", [{str(i): str(i) for i in range(50)}], indirect=True)
def test_row_random(cloud_test_catalog):
    # Note: this is technically a probabilistic test, but the probability
    # of accidental failure is < 1e-10
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.index([ctc.src_uri])
    catalog.create_shadow_dataset("test", [ctc.src_uri])
    random_values = [row.random for row in catalog.ls_dataset_rows("test")]

    # Random values are unique
    assert len(set(random_values)) == len(random_values)

    RAND_MAX = 2**63  # noqa: N806
    # Values are drawn uniformly from range(2**63)
    assert 0 <= min(random_values) < 0.4 * RAND_MAX
    assert 0.6 * RAND_MAX < max(random_values) < RAND_MAX

    # Creating a new dataset preserves random values
    catalog.create_shadow_dataset("test2", [ctc.src_uri])
    random_values2 = {row.random for row in catalog.ls_dataset_rows("test2")}
    assert random_values2 == set(random_values)


def test_create_shadow_dataset_from_storage(listed_bucket, cloud_test_catalog):
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    catalog.index([src_uri])

    shadow_dataset_name = uuid.uuid4().hex
    dataset = catalog.create_shadow_dataset(
        shadow_dataset_name, [f"{src_uri}/dogs/*"], recursive=True
    )

    assert dataset.name == shadow_dataset_name
    assert dataset.status == DatasetStatus.COMPLETE
    assert dataset.sources == f"{src_uri}/dogs/*"
    assert dataset.query_script == ""


def test_dataset_stats_shadow_ds(cloud_test_catalog, dogs_shadow_dataset):
    catalog = cloud_test_catalog.catalog
    stats = catalog.dataset_stats(dogs_shadow_dataset.name)
    assert stats.num_objects == 4
    assert stats.size == 15


def test_dataset_stats_registered_ds(cloud_test_catalog, dogs_registered_dataset):
    catalog = cloud_test_catalog.catalog
    stats = catalog.dataset_stats(dogs_registered_dataset.name, 1)
    assert stats.num_objects == 4
    assert stats.size == 15


def test_dataset_stats_missing_version(cloud_test_catalog, dogs_registered_dataset):
    catalog = cloud_test_catalog.catalog
    with pytest.raises(ValueError):
        catalog.dataset_stats(dogs_registered_dataset.name)


@pytest.mark.parametrize("indirect", [False])
def test_dataset_dependencies_shadow(
    listed_bucket, cloud_test_catalog, dogs_shadow_dataset, indirect
):
    catalog = cloud_test_catalog.catalog
    storage = catalog.get_storage(cloud_test_catalog.src_uri)

    assert [
        dataset_dependency_asdict(d)
        for d in catalog.get_dataset_dependencies(
            dogs_shadow_dataset.name, indirect=indirect
        )
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
def test_dataset_dependencies_registered(
    listed_bucket, cloud_test_catalog, dogs_registered_dataset, indirect
):
    catalog = cloud_test_catalog.catalog
    storage = catalog.get_storage(cloud_test_catalog.src_uri)

    assert [
        dataset_dependency_asdict(d)
        for d in catalog.get_dataset_dependencies(
            dogs_registered_dataset.name, 1, indirect=indirect
        )
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
