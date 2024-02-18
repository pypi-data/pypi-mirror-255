import pytest

from dql.sql import literal, select
from dql.sql.functions import string


def test_length(data_storage):
    query = select(string.length(literal("abcdefg")))
    result = tuple(data_storage.ddb.execute(query))
    assert result == ((7,),)


@pytest.mark.parametrize(
    "args,expected",
    [
        ([literal("abc//def/g/hi"), literal("/")], ["abc", "", "def", "g", "hi"]),
        ([literal("abc//def/g/hi"), literal("/"), 2], ["abc", "", "def/g/hi"]),
    ],
)
def test_split(data_storage, args, expected):
    query = select(string.split(*args))
    result = tuple(data_storage.dataset_rows_select(query))
    assert result == ((expected,),)
