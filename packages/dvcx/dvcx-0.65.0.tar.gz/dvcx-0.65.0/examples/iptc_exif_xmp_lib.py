from dql.lib.iptc_exif_xmp import GetMetadata
from dql.query import C, DatasetQuery

source = "s3://ldb-public/remote/data-lakes/open-images-v6/"

if __name__ == "__main__":
    results = (
        DatasetQuery(
            source,
            client_config={"aws_anon": True},
        )
        .filter(C.name.glob("*.jpg"))
        .limit(10000)
        .add_signals(GetMetadata, processes=True)
        .select("source", "xmp", "exif", "iptc", "error")
        .results()
    )
    print(*results, sep="\n")
