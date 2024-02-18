"""
fashion-clip UDF, using the
[fashion-clip](https://pypi.org/project/fashion-clip/#description) package.

Generated embeddings are stored json-encoded.

To install script dependencies: pip install tabulate fashion-clip
"""
import json

from fashion_clip.fashion_clip import FashionCLIP
from PIL import Image
from sqlalchemy import JSON
from tabulate import tabulate

from dql.query import C, DatasetQuery, Object, udf


def load_image(raw):
    img = Image.open(raw)
    img.load()
    return img


@udf(
    params=(Object(load_image),),
    output={"fclip": JSON},
    method="fashion_clip",
    batch=10,
)
class MyFashionClip:
    def __init__(self):
        self.fclip = FashionCLIP("fashion-clip")

    def fashion_clip(self, inputs):
        embeddings = self.fclip.encode_images(
            [input[0] for input in inputs], batch_size=1
        )
        emb_json = [(json.dumps(emb),) for emb in embeddings.tolist()]
        return emb_json


if __name__ == "__main__":
    # This example processes 5 objects in the new dataset and generates the
    # embeddings for them.
    DatasetQuery(path="s3://dql-zalando-hd-resized/zalando-hd-resized/").filter(
        C.name.glob("*.jpg")
    ).limit(5).add_signals(MyFashionClip).save("zalando_hd_emb")

    print(tabulate(DatasetQuery(name="zalando_hd_emb").results()[:5]))
