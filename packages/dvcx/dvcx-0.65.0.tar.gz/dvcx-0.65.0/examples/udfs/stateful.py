"""
To install dependencies:

  pip install imgbeddings

"""
import uuid

from imgbeddings import imgbeddings
from PIL import Image

from dql.query import C, DatasetQuery, Object, udf
from dql.sql.types import Array, Float32


def load_image(raw):
    img = Image.open(raw)
    img.load()
    return img


@udf(
    params=(Object(load_image),),
    output={"embedding": Array(Float32)},
    method="embedding",
)
class ImageEmbeddings:
    def __init__(self):
        self.emb = imgbeddings()

    def embedding(self, img):
        emb = self.emb.to_embeddings(img)
        return (emb[0].tolist(),)


if __name__ == "__main__":
    ds_name = uuid.uuid4().hex
    print(f"Saving to dataset: {ds_name}")
    # Save as a new shadow dataset
    DatasetQuery(
        path="s3://ldb-public/remote/data-lakes/dogs-and-cats/",
        client_config={"aws_anon": True},
    ).filter(C.name.glob("*cat*.jpg")).limit(5).add_signals(ImageEmbeddings).save(
        ds_name
    )

    for row in DatasetQuery(name=ds_name).results()[:2]:
        print("default columns: ", row[:-1])
        print("embedding[:10]:  ", row[-1][:10])
        print(f"type: {type(row[-1]).__name__}, len: {len(row[-1])}")
        print()
