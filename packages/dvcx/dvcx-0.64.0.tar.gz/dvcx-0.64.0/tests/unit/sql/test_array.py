from dql.sql import literal, select
from dql.sql.functions import array, string


def test_length(data_storage):
    query = select(
        array.length(["abc", "def", "g", "hi"]),
        array.length([3.0, 5.0, 1.0, 6.0, 1.0]),
        array.length([[1, 2, 3], [4, 5, 6]]),
    )
    result = tuple(data_storage.ddb.execute(query))
    assert result == ((4, 5, 2),)


def test_length_on_split(data_storage):
    query = select(
        array.length(string.split(literal("abc/def/g/hi"), literal("/"))),
    )
    result = tuple(data_storage.ddb.execute(query))
    assert result == ((4,),)
