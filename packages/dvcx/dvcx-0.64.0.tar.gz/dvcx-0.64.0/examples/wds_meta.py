from dql.lib.dataset import Dataset
from dql.lib.webdataset_meta import parse_wds_meta
from dql.query.schema import C

ds = Dataset("s3://dvcx-datacomp-small", client_config={"aws_anon": True})
ds = ds.filter(C.name.glob("0020f*"))
ds = ds.apply(parse_wds_meta)

print(ds.limit(20).select(C.name, C.uid, C.l14_img).to_pandas())
