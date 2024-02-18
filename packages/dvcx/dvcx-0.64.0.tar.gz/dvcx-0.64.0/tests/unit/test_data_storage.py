from datetime import datetime
from typing import Any, Dict

import pytest

from dql.catalog import indexer_formats
from dql.sql.types import (
    JSON,
    Array,
    Boolean,
    DateTime,
    Float,
    Float32,
    Float64,
    Int,
    String,
)

from ..utils import DEFAULT_TREE, TARRED_TREE

COMPLEX_TREE: Dict[str, Any] = {
    **TARRED_TREE,
    **DEFAULT_TREE,
    "nested": {"dir": {"path": {"abc.txt": "abc"}}},
}


@pytest.mark.parametrize("use_dataset", [False, True])
@pytest.mark.parametrize("tree", [COMPLEX_TREE], indirect=True)
def test_dir_expansion(cloud_test_catalog, use_dataset, version_aware, cloud_type):
    has_version = version_aware or cloud_type == "gcs"

    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.index([ctc.src_uri], index_processors=indexer_formats["tar-files"])

    partial_id = catalog.data_storage.get_valid_partial_id(ctc.src_uri, "")
    st = catalog.data_storage.clone(ctc.src_uri, partial_id)
    if use_dataset:
        dataset = catalog.create_shadow_dataset("ds1", [ctc.src_uri], recursive=True)
        q = st.dataset_rows(dataset.name).dir_expansion()
    else:
        q = st.nodes.dir_expansion()
    columns = (
        "id",
        "vtype",
        "is_dir",
        "source",
        "parent",
        "name",
        "version",
        "location",
    )
    result = [dict(zip(columns, r)) for r in st.ddb.execute(q)]
    to_compare = [
        (r["parent"], r["name"], r["vtype"], r["is_dir"], r["version"] != "")
        for r in result
    ]

    assert all(r["source"] == ctc.src_uri for r in result)
    # Note, we have both a file and a directory entry for expanded tar files
    assert to_compare == [
        ("", "animals.tar", "", 0, has_version),
        ("", "animals.tar", "", 1, False),
        ("", "cats", "", 1, False),
        ("", "description", "", 0, has_version),
        ("", "dogs", "", 1, False),
        ("", "nested", "", 1, False),
        ("animals.tar", "cats", "", 1, False),
        ("animals.tar", "description", "tar", 0, False),
        ("animals.tar", "dogs", "", 1, False),
        ("animals.tar/cats", "cat1", "tar", 0, False),
        ("animals.tar/cats", "cat2", "tar", 0, False),
        ("animals.tar/dogs", "dog1", "tar", 0, False),
        ("animals.tar/dogs", "dog2", "tar", 0, False),
        ("animals.tar/dogs", "dog3", "tar", 0, False),
        ("animals.tar/dogs", "others", "", 1, False),
        ("animals.tar/dogs/others", "dog4", "tar", 0, False),
        ("cats", "cat1", "", 0, has_version),
        ("cats", "cat2", "", 0, has_version),
        ("dogs", "dog1", "", 0, has_version),
        ("dogs", "dog2", "", 0, has_version),
        ("dogs", "dog3", "", 0, has_version),
        ("dogs", "others", "", 1, False),
        ("dogs/others", "dog4", "", 0, has_version),
        ("nested", "dir", "", 1, False),
        ("nested/dir", "path", "", 1, False),
        ("nested/dir/path", "abc.txt", "", 0, has_version),
    ]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_convert_type(cloud_test_catalog):
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    data_storage = catalog.data_storage
    now = datetime.now()

    # convert int to float
    for f in [Float, Float32, Float64]:
        converted = data_storage.convert_type(1, f())
        assert converted == 1.0
        assert isinstance(converted, float)

    # types match, nothing to convert
    assert data_storage.convert_type(1, Int()) == 1
    assert data_storage.convert_type(1.5, Float()) == 1.5
    assert data_storage.convert_type(True, Boolean()) is True
    assert data_storage.convert_type("s", String()) == "s"
    assert data_storage.convert_type(now, DateTime()) == now
    assert data_storage.convert_type([1, 2], Array(Int)) == [1, 2]
    assert data_storage.convert_type([1.5, 2.5], Array(Float)) == [1.5, 2.5]
    assert data_storage.convert_type(["a", "b"], Array(String)) == ["a", "b"]
    assert data_storage.convert_type([[1, 2], [3, 4]], Array(Array(Int))) == [
        [1, 2],
        [3, 4],
    ]

    # convert array to compatible type
    converted = data_storage.convert_type([1, 2], Array(Float))
    assert converted == [1.0, 2.0]
    assert all(isinstance(c, float) for c in converted)

    # convert nested array to compatible type
    converted = data_storage.convert_type([[1, 2], [3, 4]], Array(Array(Float)))
    assert converted == [[1.0, 2.0], [3.0, 4.0]]
    assert all(isinstance(c, float) for c in converted[0])
    assert all(isinstance(c, float) for c in converted[1])

    # error, float to int
    with pytest.raises(ValueError):
        data_storage.convert_type(1.5, Int())

    # error, float to int in list
    with pytest.raises(ValueError):
        data_storage.convert_type([1.5, 1], Array(Int))

    # error, string to json
    with pytest.raises(ValueError):
        data_storage.convert_type('{"a": 1}', JSON)
