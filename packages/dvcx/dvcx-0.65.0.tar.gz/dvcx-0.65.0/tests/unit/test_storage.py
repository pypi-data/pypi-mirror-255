from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func

from dql import utils
from dql.error import StorageNotFoundError
from dql.storage import STALE_HOURS_LIMIT, Status, Storage

from ..utils import skip_if_not_sqlite

TS = datetime(2022, 8, 1)
EXPIRES = datetime(2022, 8, 2)


def test_human_time():
    assert utils.human_time_to_int("1236") == 1236
    assert utils.human_time_to_int("3h") == 3 * 60 * 60
    assert utils.human_time_to_int("2w") == 2 * 7 * 24 * 60 * 60
    assert utils.human_time_to_int("4M") == 4 * 31 * 24 * 60 * 60

    assert utils.human_time_to_int("bla") is None


def test_storage():
    s = Storage("s3://foo", TS, EXPIRES)

    d = s.to_dict()
    assert d.get("uri") == s.uri


def test_expiration_time():
    assert Storage.get_expiration_time(TS, 12344) == TS + timedelta(seconds=12344)


def test_adding_storage(data_storage):
    uri = "s3://whatever"
    with pytest.raises(StorageNotFoundError):
        data_storage.get_storage(uri)

    storage, _, _, _ = data_storage.register_storage_for_indexing(uri)
    cnt = next(
        data_storage.mdb.execute(data_storage.storages_select(func.count())), (0,)
    )
    assert cnt[0] == 1

    bkt = list(
        data_storage.mdb.execute(
            data_storage.storages_select().where(data_storage.storages.c.uri == uri)
        )
    )
    assert len(bkt) == 1

    assert storage.id == bkt[0][0]
    assert storage.uri == bkt[0][1]
    assert storage.timestamp == bkt[0][2]
    assert storage.expires == bkt[0][3]
    assert storage.started_inserting_at == bkt[0][4]
    assert storage.last_inserted_at == bkt[0][5]
    assert storage.status == bkt[0][6]
    assert storage.error_message == ""
    assert storage.error_stack == ""


def test_storage_status(data_storage):
    uri = "s3://somebucket"

    data_storage.create_storage_if_not_registered(uri)
    storage = data_storage.get_storage(uri)
    assert storage.uri == uri
    assert storage.status == Status.CREATED

    (
        storage,
        need_index,
        in_progress,
        partial_id,
    ) = data_storage.register_storage_for_indexing(uri)
    assert storage.status == Status.PENDING
    assert storage.uri == uri
    assert storage == data_storage.get_storage(uri)
    assert need_index is True
    assert in_progress is False
    assert partial_id is None

    (
        s2,
        need_index,
        in_progress,
        partial_id,
    ) = data_storage.register_storage_for_indexing(uri)
    assert s2.status == Status.PENDING
    assert storage == s2 == data_storage.get_storage(uri)
    assert need_index is False
    assert in_progress is True
    assert partial_id is None

    end_time = datetime.now(timezone.utc)
    data_storage.mark_storage_indexed(uri, Status.COMPLETE, 1000, end_time)
    storage = data_storage.get_storage(uri)
    assert storage.status == Status.COMPLETE


@pytest.mark.parametrize(
    "ttl",
    (-1, 999999999999, 99999999999999, 9999999999999999),
)
def test_max_ttl(ttl):
    uri = "s3://whatever"
    expires = Storage.get_expiration_time(TS, ttl)
    storage = Storage(1, uri, TS, expires)
    assert storage.timestamp == TS
    assert storage.expires == datetime.max
    assert storage.timestamp_str  # no error
    assert storage.timestamp_to_local  # no error
    assert storage.expires_to_local  # no error


def test_storage_without_dates():
    uri = "s3://whatever"
    storage = Storage(1, uri, None, None)
    assert storage.timestamp is None
    assert storage.expires is None
    assert storage.timestamp_str is None  # no error
    assert storage.timestamp_to_local is None  # no error
    assert storage.expires_to_local is None  # no error
    assert storage.to_dict() == {
        "uri": uri,
        "timestamp": None,
        "expires": None,
    }


async def test_storage_update_last_inserted_at(data_storage):
    uri = "s3://bucket_last_inserted"
    data_storage.create_storage_if_not_registered(uri)
    await data_storage.update_last_inserted_at(uri)
    storage = data_storage.get_storage(uri)
    assert storage.last_inserted_at


def test_stale_storage(data_storage):
    uri_stale = "s3://bucket_stale"
    uri_not_stale = "s3://bucket_not_stale"

    data_storage.create_storage_if_not_registered(uri_stale)
    data_storage.create_storage_if_not_registered(uri_not_stale)

    data_storage.mark_storage_pending(data_storage.get_storage(uri_stale))
    data_storage.mark_storage_pending(data_storage.get_storage(uri_not_stale))

    # make storage looks stale
    updates = {
        "last_inserted_at": datetime.now(timezone.utc)
        - timedelta(hours=STALE_HOURS_LIMIT + 1)
    }
    s = data_storage.storages
    data_storage.mdb.execute(s.update().where(s.c.uri == uri_stale).values(**updates))

    data_storage.find_stale_storages()

    stale_storage = data_storage.get_storage(uri_stale)
    assert stale_storage.status == Status.STALE

    not_stale_storage = data_storage.get_storage(uri_not_stale)
    assert not_stale_storage.status == Status.PENDING


def test_failed_storage(data_storage):
    uri = "s3://bucket"
    error_message = "Internal error on indexing"
    error_stack = "error"
    data_storage.create_storage_if_not_registered(uri)

    data_storage.mark_storage_pending(data_storage.get_storage(uri))
    data_storage.mark_storage_indexed(
        uri,
        Status.FAILED,
        1000,
        datetime.now(),
        error_message=error_message,
        error_stack=error_stack,
    )

    storage = data_storage.get_storage(uri)
    assert storage.status == Status.FAILED
    assert storage.error_message == error_message
    assert storage.error_stack == error_stack


def test_unlist_source(
    listed_bucket,
    cloud_test_catalog,
):
    # TODO remove when https://github.com/iterative/dql/pull/868 is merged
    skip_if_not_sqlite()
    source_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog
    partial_id = catalog.data_storage.get_valid_partial_id(source_uri, "")
    data_storage = catalog.data_storage.clone(source_uri, partial_id)
    dataset_name = data_storage.nodes.name

    # list source
    storage = catalog.get_storage(source_uri)
    assert storage.status == Status.COMPLETE
    assert data_storage.ddb.has_table(dataset_name)

    # unlist source
    catalog.unlist_source(source_uri)
    with pytest.raises(StorageNotFoundError):
        catalog.get_storage(source_uri)
    # we preserve the table for dataset lineage
    assert data_storage.ddb.has_table(dataset_name)
