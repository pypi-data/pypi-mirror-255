import uuid

from tabulate import tabulate

from dql.query import C, DatasetQuery, udf
from dql.sql.types import Int

# To install script dependencies: pip install tabulate


# Define the UDF:
@udf(
    ("name",),  # Columns consumed by the UDF.
    {
        "name_len": Int
    },  # Signals being returned by the UDF, with the signal name and type.
)
def name_len(name):
    if name.endswith(".json"):
        return (-1,)
    else:
        return (len(name),)


if __name__ == "__main__":
    ds_name = uuid.uuid4().hex
    print(f"Saving to dataset: {ds_name}")
    # Save as a new shadow dataset
    DatasetQuery(
        path="s3://ldb-public/remote/data-lakes/dogs-and-cats/",
        client_config={"aws_anon": True},
    ).filter(C.name.glob("*cat*")).add_signals(name_len).save(ds_name)

    # Output the contents of the new dataset.
    print(
        tabulate(
            DatasetQuery(name=ds_name)
            .order_by(C.parent, C.name)
            .limit(10)
            .select(C.source, C.parent, C.name, C.size, C.name_len)
            .results()
        )
    )
