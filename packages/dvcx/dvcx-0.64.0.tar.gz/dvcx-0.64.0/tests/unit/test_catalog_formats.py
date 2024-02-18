import pytest
import sqlalchemy as sa

from dql.catalog.formats import flatten_signals, get_columns, get_union_columns


@pytest.fixture
def signals():
    return {
        "hash": "259e893d3fb7686599003c4e57189479",
        "similarity": 0.34,
        "valid": True,
        "name": None,
        "empty_l": [],
        "empty_d": {},
        "image": {
            "height": 324,
            "length": 555,
            "tags": ["dog", "cat"],
            "nested": [["dog"], ["cat"]],
        },
        "embeddings": {
            "vector": [0.5, 0.54, 0.55],
            "meta": [
                {"name": "emb1", "value": 12},
                {"name": "emb2", "value": 10},
                {"name": "emb3", "value": 4},
            ],
        },
    }


@pytest.fixture
def signals_laion():
    return {
        "punsafe": 3.2040975384006742e-06,
        "pwatermark": 1.0,
        "similarity": 0.31533074378967285,
        "hash": 7379780851511021036,
        "caption": "1984-1996 C4 Corvette,LH Rear Storage Compartment Insert",
        "url": "https://47.cdn.ekm.net/ekmps/shops/b5f6f2/images/1984",
        "key": "0000009981",
        "status": "success",
        "error_message": None,
        "width": 384,
        "height": 256,
        "original_width": 440,
        "original_height": 293,
        "exif": "{}",
        "md5": "4726c5d03919c64373eb255484ed384f",
    }


def test_flatten_signals(signals):
    assert flatten_signals(signals) == {
        "hash": "259e893d3fb7686599003c4e57189479",
        "similarity": 0.34,
        "image.height": 324,
        "image.length": 555,
        "image.tags": ["dog", "cat"],
        "embeddings.vector": [0.5, 0.54, 0.55],
        "valid": True,
    }


def test_flatten_signals_laion(signals_laion):
    assert flatten_signals(signals_laion) == {
        "punsafe": 3.2040975384006742e-06,
        "pwatermark": 1.0,
        "similarity": 0.31533074378967285,
        "hash": 7379780851511021036,
        "caption": "1984-1996 C4 Corvette,LH Rear Storage Compartment Insert",
        "url": "https://47.cdn.ekm.net/ekmps/shops/b5f6f2/images/1984",
        "key": "0000009981",
        "status": "success",
        "width": 384,
        "height": 256,
        "original_width": 440,
        "original_height": 293,
        "exif": "{}",
        "md5": "4726c5d03919c64373eb255484ed384f",
    }


def test_flatten_signals_empty():
    assert flatten_signals({}) == {}


def test_get_columns(signals):
    signals_flattened = flatten_signals(signals)
    columns = get_columns(signals_flattened)
    columns.sort(key=lambda x: x[0])
    assert [(n, type(c)) for n, c in columns] == [
        ("embeddings.vector", sa.JSON),
        ("hash", sa.String),
        ("image.height", sa.Integer),
        ("image.length", sa.Integer),
        ("image.tags", sa.JSON),
        ("similarity", sa.Float),
        ("valid", sa.Boolean),
    ]


def test_get_columns_laion(signals_laion):
    signals_flattened = flatten_signals(signals_laion)
    columns = get_columns(signals_flattened)
    columns.sort(key=lambda x: x[0])
    assert [(n, type(c)) for n, c in columns] == [
        ("caption", sa.String),
        ("exif", sa.String),
        ("hash", sa.Integer),
        ("height", sa.Integer),
        ("key", sa.String),
        ("md5", sa.String),
        ("original_height", sa.Integer),
        ("original_width", sa.Integer),
        ("punsafe", sa.Float),
        ("pwatermark", sa.Float),
        ("similarity", sa.Float),
        ("status", sa.String),
        ("url", sa.String),
        ("width", sa.Integer),
    ]


def test_get_columns_empty():
    assert get_columns({}) == []


def test_get_union_columns(signals):
    signals_flattened = flatten_signals(signals)
    signals_list = [signals_flattened, {**signals_flattened, "score": 344.4}]
    columns = get_union_columns(signals_list)
    columns.sort(key=lambda x: x[0])
    assert [(n, type(c)) for n, c in columns] == [
        ("embeddings.vector", sa.JSON),
        ("hash", sa.String),
        ("image.height", sa.Integer),
        ("image.length", sa.Integer),
        ("image.tags", sa.JSON),
        ("score", sa.Float),
        ("similarity", sa.Float),
        ("valid", sa.Boolean),
    ]


def test_get_union_columns_empty():
    assert get_union_columns([]) == []
