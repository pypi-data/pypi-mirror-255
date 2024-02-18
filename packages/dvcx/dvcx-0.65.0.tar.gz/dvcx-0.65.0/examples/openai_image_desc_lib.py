# pip install Pillow

import os

from dql.lib.gpt4_vision import DescribeImage
from dql.query import C, DatasetQuery

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

source = "s3://ldb-public/remote/data-lakes/dogs-and-cats/"

if __name__ == "__main__":
    results = (
        DatasetQuery(
            source,
            client_config={"aws_anon": True},
        )
        .filter(C.name.glob("cat*.jpg"))
        .limit(10)
        .add_signals(
            DescribeImage(
                key=OPENAI_API_KEY, max_tokens=300, prompt="What is in this image?"
            ),
            parallel=-1,
        )
        .select("source", "parent", "name", "description", "error")
        .results()
    )
    print(*results, sep="\n")
