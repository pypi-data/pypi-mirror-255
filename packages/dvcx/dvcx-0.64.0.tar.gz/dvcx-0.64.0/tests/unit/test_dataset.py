from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import dialect as sqlite_dialect
from sqlalchemy.schema import CreateTable

from dql.data_storage.schema import DatasetRow
from dql.sql.types import JSON, Array, Binary, Float, Float32, Float64, Int


def test_dataset_table_compilation():
    table = DatasetRow.new_table(
        "ds-1",
        custom_columns=[
            Column("score", Float, nullable=False),
            Column("meta_info", JSON),
        ],
    )
    result = CreateTable(table, if_not_exists=True).compile(dialect=sqlite_dialect())

    assert result.string == (
        "\n"
        'CREATE TABLE IF NOT EXISTS "ds-1" (\n'
        "\tid INTEGER NOT NULL, \n"
        "\tvtype VARCHAR NOT NULL, \n"
        "\tdir_type INTEGER, \n"
        "\tparent_id INTEGER, \n"
        "\tparent VARCHAR, \n"
        "\tname VARCHAR NOT NULL, \n"
        "\tchecksum VARCHAR, \n"
        "\tetag VARCHAR, \n"
        "\tversion VARCHAR, \n"
        "\tis_latest BOOLEAN, \n"
        "\tlast_modified DATETIME, \n"
        "\tsize INTEGER NOT NULL, \n"
        "\towner_name VARCHAR, \n"
        "\towner_id VARCHAR, \n"
        "\tanno JSON, \n"
        "\trandom INTEGER NOT NULL, \n"
        "\tlocation JSON, \n"
        "\tsource VARCHAR NOT NULL, \n"
        "\tscore FLOAT NOT NULL, \n"
        "\tmeta_info JSON, \n"
        "\tPRIMARY KEY (id)\n"
        ")\n"
        "\n"
    )


def test_custom_column_types_serialization(dataset_record):
    dataset_record.custom_column_types = {"int_col": Int}
    assert dataset_record.custom_column_types_serialized == {"int_col": {"type": "Int"}}

    dataset_record.custom_column_types = {
        "binary_col": Binary,
        "float_32_col": Float32,
    }
    assert dataset_record.custom_column_types_serialized == {
        "binary_col": {"type": "Binary"},
        "float_32_col": {"type": "Float32"},
    }

    dataset_record.custom_column_types = {"nested_col": Array(Array(Float64))}
    assert dataset_record.custom_column_types_serialized == {
        "nested_col": {
            "type": "Array",
            "item_type": {"type": "Array", "item_type": {"type": "Float64"}},
        }
    }
