"""
This script provides an example of the dir expansion query available
for datasets and storage indices. It prints the results, some summary
stats and verifies that the result is the same both for a dataset and
for a storage index with the same entries.
"""
import sys

import sqlalchemy as sa

from dql.catalog import get_catalog, indexer_formats
from dql.error import DatasetNotFoundError
from dql.query import DatasetQuery

show_ids = False
if len(sys.argv) > 1:
    if sys.argv[1] == "--show-ids":
        show_ids = True
    else:
        raise RuntimeError(f"Invalid arg: {sys.argv[1]}")

source = "s3://ldb-public/remote/datasets/"
catalog = get_catalog(client_config={"aws_anon": True})
data_storage = catalog.data_storage

try:
    dataset = data_storage.get_dataset("ds1")
    partial_id = data_storage.get_valid_partial_id("s3://ldb-public", "remote/datasets")
    n = data_storage.nodes_table("s3://ldb-public", partial_id)
except DatasetNotFoundError:
    catalog.index([source], index_processors=indexer_formats["webdataset"])
    partial_id = data_storage.get_valid_partial_id("s3://ldb-public", "remote/datasets")
    n = data_storage.nodes_table("s3://ldb-public", partial_id)

    ds = DatasetQuery(source)
    ds.save("ds1")

d = data_storage.dataset_rows("ds1")


def get_values_to_compare(query):
    q = query.dir_expansion().subquery()
    return list(
        data_storage.ddb.execute(
            sa.select(
                q.c.source,
                q.c.parent,
                q.c.name,
                q.c.version,
                q.c.vtype,
                q.c.is_dir,
                q.c.location,
            )
        )
    )


dq = d.dir_expansion()
result = data_storage.ddb.execute(dq)
for id_, vtype, is_dir, source, parent, name, version, _loc in result:
    id_str = f"{id_!r:12} " if show_ids else ""
    print(f"{id_str}{vtype!r:6} {version!r} {is_dir} {source!r} {parent!r} {name!r}")

print()
print("num dir expansion rows: ", len(list(data_storage.ddb.execute(dq))))
print(
    "num dir expansion files:",
    len(list(data_storage.ddb.execute(dq.having(~dq.selected_columns.is_dir)))),
)
print("num table rows:         ", len(list(data_storage.ddb.execute(d.select()))))
print("same values:            ", get_values_to_compare(n) == get_values_to_compare(d))
