from dql.vendored import ast


def test_simple_unparse():
    code = "d[1]"
    assert ast.unparse(ast.parse(code)) == code
