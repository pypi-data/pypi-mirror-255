import json
import tarfile

from dql.lib.udf import Generator
from dql.lib.utils import bin_to_array, union_dicts
from dql.query import DatasetRow
from dql.query.schema import Stream
from dql.sql.types import JSON, Array, Float, Int, Int32, Int64, String

FILES_SCHEMA = {
    "txt": String,
    "text": String,
    "cap": String,
    "transcript": String,
    "cls": Int32,
    "cls2": Int32,
    "index": Int64,
    "inx": Int64,
    # renamed from `id` in original payload not to conflicts with core column id
    "_id": Int64,
    "json": String,  # It suppose to be JSON but there is an issue
    "jsn": String,  # Same
    "pyd": Array(Int32),  # These are suppose to be binary (when enabled)
    "pickle": Array(Int32),
    "pth": Array(Int32),
    "ten": Array(Int32),
    "tb": Array(Int32),
    "mp": Array(Int32),
    "msg": Array(Int32),
    "npy": Array(Int32),
    "npz": Array(Int32),
    "cbor": Array(Int32),
}

ALL_EXTENSIONS = tuple(FILES_SCHEMA.keys())

LAION_SCHEMA = {
    "uid": String,
    "face_bboxes": Array(Array(Float)),
    "caption": String,
    "url": String,
    "key": String,
    "status": String,
    "error_message": String,
    "width": Int,
    "height": Int,
    "original_width": Int,
    "original_height": Int,
    "exif": String,
    "sha256": String,
}


TAR_SCHEMA = {"tar_offset": Int64}


class WebDataset(Generator):
    def __init__(
        self,
        core_extension="jpg",
        extensions=ALL_EXTENSIONS,
        encoding="utf-8",
        json_to_flatten=LAION_SCHEMA,
    ):
        self.json_to_flatten = json_to_flatten
        self.file_schema = {k: FILES_SCHEMA[k] for k in FILES_SCHEMA if k in extensions}

        self.core_extension = core_extension
        self.extensions = extensions
        self.encoding = encoding

        super().__init__(
            (
                "source",
                "parent",
                "name",
                "etag",
                Stream(),
            ),
            union_dicts(
                TAR_SCHEMA,
                self.json_to_flatten,
                self.file_schema,
            ),
        )

    def process(self, source, parent, name, etag, stream):
        with stream:
            with tarfile.open(fileobj=stream) as tar:
                curr_basename = None
                curr_item = None
                curr_payload = {}

                it_basename = None
                for item in tar.getmembers():
                    if not item.isfile():
                        continue

                    it_basename, it_ext = self.split_extension(item.name)

                    if curr_basename != it_basename:
                        if curr_basename is not None:
                            yield self.create_record(
                                source,
                                parent,
                                name,
                                etag,
                                it_basename,
                                curr_item,
                                curr_payload,
                            )
                        curr_basename = it_basename
                        curr_item = None
                        curr_payload = {}

                    if it_ext == self.core_extension:
                        curr_item = item
                    elif it_ext in self.extensions:
                        curr_payload[it_ext] = tar.extractfile(item).read()

                if curr_basename:
                    yield self.create_record(
                        source, parent, name, etag, it_basename, curr_item, curr_payload
                    )

    @staticmethod
    def split_extension(fname):
        dot_index = fname.find(".")
        if dot_index == -1:
            return fname, ""

        basename = fname[:dot_index]
        ext = fname[dot_index + 1 :]
        last_ext = ext.split(".")[-1]
        return basename, last_ext

    def create_record(self, source, parent, name, etag, basename, item, payload):
        if item is None:
            file = f"{source}/{parent}/{name}"
            target_file = f"{basename}.{self.core_extension}"
            raise RuntimeError(f"File {target_file} was not found in {file}")
        return (
            DatasetRow.create(
                item.name,
                source=source,
                parent=f"{parent}/{name}",
                size=item.size,
                etag=etag,
                vtype="tar",
                location={"size": item.size, "offset": item.offset_data, "etag": etag},
            )
            + (item.offset_data,)
            + self.flatten_json(payload)
            + self.create_files_payload(payload)
        )

    def flatten_json(self, payload):
        j = json.loads(payload["json"].decode(self.encoding))
        return tuple([j.get(name, None) for name in self.json_to_flatten.keys()])

    def create_files_payload(self, payload):
        res = []
        for name, type_ in self.file_schema.items():
            # we cannot allow `id` to be in custom columns as it conflicts with
            # core column with the same name
            if name == "_id":
                name = "id"
            data = payload.get(name, None)
            if not data:
                value = None
            elif type_ in (Int64, Int32):
                value = int(data.decode(self.encoding))
            elif type_ == String:
                value = data.decode(self.encoding)
            elif type_ == JSON:
                value = json.loads(data.decode(self.encoding))
            elif str(type_) == str(Array(Int32)):
                value = bin_to_array(data)
            else:
                RuntimeError(f"Unknown file type '{type_}' in WebDataset")

            res.append(value)
        return tuple(res)
