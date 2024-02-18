"""
A simple data loader example.

This downloads and displays the first 5 images of the dataset.
"""
from PIL import Image

from dql.catalog import get_catalog
from dql.error import DatasetNotFoundError
from dql.query import C, DatasetQuery, Object

catalog = get_catalog(client_config={"aws_anon": True})
try:
    catalog.get_dataset("cats")
except DatasetNotFoundError:
    DatasetQuery(
        path="s3://ldb-public/remote/data-lakes/dogs-and-cats/",
        catalog=catalog,
    ).filter(C.name.glob("*cat*.jpg")).save("cats")


def load_img(buf):
    img = Image.open(buf)
    img.load()
    return img


images = (
    DatasetQuery(name="cats", catalog=catalog)
    .limit(5)
    .extract(Object(load_img), cache=False)
)
for (img,) in images:
    img.show()
