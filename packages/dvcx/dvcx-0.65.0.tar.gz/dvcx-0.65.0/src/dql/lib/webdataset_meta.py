import numpy as np

from dql.lib.udf import Aggregator
from dql.query import C, DatasetRow, LocalFilename
from dql.sql.functions import path
from dql.sql.types import Array, Float32, Int64, String

try:
    import pandas as pd
except ImportError:
    pd = None


def union_dicts(*dicts):
    """Union dictionaries.
    Equivalent to `d1 | d2 | d3` in Python3.9+ but works in older versions.
    """
    result = None
    for d in dicts:
        if not isinstance(d, dict):
            raise ValueError("All arguments must be dictionaries.")
        if not result:
            result = d.copy()
        else:
            result.update(d)
    return result


def parse_wds_meta(ds):
    return ds.aggregate(MergeParquetAndNpz(), partition_by=path.file_stem(C.name))


# We need to merge parquet and npz data first because they need to be
# used together for generating multiple records.
# It won't be a requirement when aggregator will generator based.
class MergeParquetAndNpz(Aggregator):
    PQ_SCHEMA = {
        "uid": String,
        "url": String,
        "text": String,
        "original_width": Int64,
        "original_height": Int64,
        "clip_b32_similarity_score": Float32,
        "clip_l14_similarity_score": Float32,
        "face_bboxes": Array(Array(Float32)),
        "sha256": String,
    }

    NPZ_SCHEMA = {
        "b32_img": Array(Float32),
        "b32_txt": Array(Float32),
        "l14_img": Array(Float32),
        "l14_txt": Array(Float32),
        "dedup": Array(Float32),
    }

    META_SCHEMA = {**PQ_SCHEMA, **NPZ_SCHEMA}

    def __init__(self):
        super().__init__(
            (
                "source",
                "parent",
                "name",
                "version",
                "etag",
                LocalFilename(),
            ),
            self.META_SCHEMA,
        )

    def process(self, args):
        group_params_fname = ["source", "parent", "name", "version", "etag", "fname"]
        df = pd.DataFrame(args, columns=group_params_fname)
        df["ext"] = df["name"].str.split(".").str[-1]

        fname_npz = df[df.ext == "npz"].fname.iloc[0]
        npz = np.load(fname_npz)
        npz_data = {key: npz[key] for key in self.NPZ_SCHEMA.keys()}

        fname_pq = df[df.ext == "parquet"].fname.iloc[0]
        pq = pd.read_parquet(fname_pq)

        pq_row = df[df.ext == "parquet"].values[0]
        source, parent, name, version, etag, _, _ = pq_row

        for idx, (_, row) in enumerate(pq.iterrows()):
            row_basic = DatasetRow.create(
                str(idx),
                source=source,
                parent=f"{parent}/{name}",
                version=version,
                etag=etag,
                vtype="parquet",
            )

            pq_payload = tuple([row[key] for key in self.PQ_SCHEMA.keys()])
            npz_payload = tuple([npz_data[key][idx] for key in self.NPZ_SCHEMA.keys()])

            yield row_basic + pq_payload + npz_payload
