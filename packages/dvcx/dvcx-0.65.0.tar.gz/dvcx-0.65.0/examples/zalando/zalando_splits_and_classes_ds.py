from dql.query import C, DatasetQuery
from dql.sql.functions import path

source_path = "s3://dql-zalando-hd-resized/zalando-hd-resized/"
ds = (
    DatasetQuery(source_path)
    .filter(C.name.glob("*.jpg"))
    .mutate(**{"class": path.name(C.parent), "label": path.name(path.parent(C.parent))})
)
