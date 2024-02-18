from adlfs import AzureBlobFileSystem

from .fsspec import DELIMITER, Client


class AzureClient(Client):
    FS_CLASS = AzureBlobFileSystem
    PREFIX = "az://"
    protocol = "az"

    def _dict_from_info(self, v, parent):
        version_id = v.get("version_id")
        checksum = v.get("content_settings", {}).get("content_md5", "")
        name = v.get("name", "").split(DELIMITER)[-1]
        if version_id:
            version_suffix = f"?versionid={version_id}"
            if name.endswith(version_suffix):
                name = name[: -len(version_suffix)]
        return {
            "dir_id": None,
            "parent": parent,
            "name": name,
            "checksum": checksum or "",
            "etag": v.get("etag", "").strip('"'),
            "version": version_id or "",
            "is_latest": version_id is None or bool(v.get("is_current_version")),
            "last_modified": v["last_modified"],
            "size": v.get("size", ""),
            "owner_name": "",
            "owner_id": "",
            "anno": None,
        }
