import pytest

from dql.sql import column, select, values
from dql.sql import literal as lit
from dql.sql.functions import greatest, least


@pytest.mark.parametrize(
    "args,expected",
    [
        ([lit("abc"), lit("bcd"), lit("Abc"), lit("cd")], "cd"),
        ([3, 1, 2.0, 3.1, 2.5, -1], 3.1),
        ([4], 4),
    ],
)
def test_greatest(data_storage, args, expected):
    query = select(greatest(*args))
    result = tuple(data_storage.ddb.execute(query))
    assert result == ((expected,),)


@pytest.mark.parametrize(
    "args,expected",
    [
        ([lit("abc"), lit("bcd"), lit("Abc"), lit("cd")], "Abc"),
        ([3, 1, 2.0, 3.1, 2.5, -1], -1),
        ([4], 4),
    ],
)
def test_least(data_storage, args, expected):
    query = select(least(*args))
    result = tuple(data_storage.ddb.execute(query))
    assert result == ((expected,),)


@pytest.mark.parametrize(
    "expr,expected",
    [
        (greatest(column("a")), [(3,), (8,), (9,)]),
        (least(column("a")), [(3,), (8,), (9,)]),
        (least(column("a"), column("b")), [(3,), (7,), (1,)]),
    ],
)
def test_conditionals_with_multiple_rows(data_storage, expr, expected):
    # In particular, we want to ensure that we are avoiding sqlite's
    # default behavior for `max` and `min` which is to behave as
    # aggregate functions when a single argument is passed.
    # See https://www.sqlite.org/lang_corefunc.html#max_scalar
    query = select(expr).select_from(values([(3, 5), (8, 7), (9, 1)], ["a", "b"]))
    result = list(data_storage.ddb.execute(query))
    assert result == expected
