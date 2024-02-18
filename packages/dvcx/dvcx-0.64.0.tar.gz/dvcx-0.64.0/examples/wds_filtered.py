import pandas as pd

import dql.error
from dql.lib.dataset import Dataset
from dql.lib.webdataset import WebDataset
from dql.query.schema import C
from dql.sql import literal
from dql.sql.functions import array, greatest, least, string

name = "wds"
wds = Dataset(name=name)
try:
    df = wds.limit(3).to_pandas()
except dql.error.DatasetNotFoundError:
    (
        Dataset("s3://dvcx-datacomp-small/shards", client_config={"aws_anon": True})
        .filter(C.name.glob("00000000.tar"))
        .generate(WebDataset())
        .save(name)
    )
    df = wds.limit(3).to_pandas()

print(df.columns.tolist())
columns = [
    "parent",
    "name",
    "vtype",
    "dir_type",
    "size",
    "caption",
    "url",
    "width",
    "height",
    "original_width",
    "original_height",
]
with pd.option_context("display.max_columns", None):
    print(df[columns])

filtered = (
    wds.filter(string.length(C.caption) > 5)
    .filter(array.length(string.split(C.caption, literal(" "))) > 2)
    .filter(least(C.original_width, C.original_height) > 200)
    .filter(
        greatest(C.original_width, C.original_height)
        / least(C.original_width, C.original_height)
        < 3.0
    )
)
filtered_df = filtered.limit(3).to_pandas()[columns]
with pd.option_context("display.max_columns", None):
    print(filtered_df)

print(f"wds count:      {wds.count():>6}")
print(f"filtered count: {filtered.count():>6}")
