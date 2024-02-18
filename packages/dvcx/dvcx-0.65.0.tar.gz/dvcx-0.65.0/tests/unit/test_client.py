import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from dql.client import Client

from ..utils import uppercase_scheme


def test_bad_url():
    bucket = "whatever"
    path = "my/path"
    with pytest.raises(RuntimeError):
        Client.parse_url(bucket + "/" + path + "/", None, None)


non_null_text = st.text(
    alphabet=st.characters(blacklist_categories=["Cc", "Cs"]), min_size=1
)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(rel_path=non_null_text)
def test_parse_url(cloud_test_catalog, rel_path):
    bucket_uri = cloud_test_catalog.src_uri
    url = f"{bucket_uri}/{rel_path}"
    catalog = cloud_test_catalog.catalog
    client, rel_part = catalog.parse_url(url)
    assert client.uri == bucket_uri
    assert rel_part == rel_path


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(rel_path=non_null_text)
def test_parse_url_uppercase_scheme(cloud_test_catalog, rel_path):
    bucket_uri = cloud_test_catalog.src_uri
    bucket_uri_upper = uppercase_scheme(bucket_uri)
    url = f"{bucket_uri_upper}/{rel_path}"
    catalog = cloud_test_catalog.catalog
    client, rel_part = catalog.parse_url(url)
    assert client.uri == bucket_uri
    assert rel_part == rel_path
