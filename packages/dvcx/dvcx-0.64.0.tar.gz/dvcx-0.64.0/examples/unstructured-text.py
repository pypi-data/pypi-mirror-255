#
# pip install unstructured[all-docs]
# libmagic
#
# partition_object supports via unstructured library:
#
# "csv", "doc", "docx", "epub", "image", "md", "msg", "odt", "org",
# "pdf", "ppt", "pptx", "rtf", "rst", "tsv", "xlsx"

from transformers import pipeline

from dql.lib.dataset import Dataset
from dql.lib.unstructured import PartitionObject
from dql.query import C
from dql.sql.types import String

device = "cpu"
model = "pszemraj/led-large-book-summary"
source = "s3://ldb-public/remote/data-lakes/NLP/infobooks/"


def cleanse(text):
    separator = "Listen to this story"
    head, sep, tail = text.partition(separator)
    return (head,)


def summarize(clean):
    helper = pipeline(model=model, device=device)
    summary = helper(clean, max_length=200)[0]["summary_text"]
    return (summary,)


ds = (
    Dataset(
        source,
        client_config={"aws_anon": True},
    )
    .filter(C.name.glob("*.pdf"))
    .limit(1)
    .map(PartitionObject(), parallel=False)
)

ds = ds.map(cleanse, output={"clean": String})
ds = ds.map(summarize, output={"summary": String})
results = ds.select("text", "summary").results()

for story in results:
    print("\n *********** the original: ********** ")
    print(story[0])

    print("\n *********** the summary: *********** ")
    print(story[1])
    print("\n")
