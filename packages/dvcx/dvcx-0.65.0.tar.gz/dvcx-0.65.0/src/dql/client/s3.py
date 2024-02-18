from typing import cast

from s3fs import S3FileSystem

from .fsspec import DELIMITER, TIME_ZERO, Client

UPDATE_CHUNKSIZE = 1000


class ClientS3(Client):
    FS_CLASS = S3FileSystem
    PREFIX = "s3://"
    protocol = "s3"

    @classmethod
    def create_fs(cls, **kwargs) -> S3FileSystem:
        if "aws_anon" in kwargs:
            kwargs.setdefault("anon", kwargs.pop("aws_anon"))
        if "aws_endpoint_url" in kwargs:
            kwargs.setdefault("client_kwargs", {}).setdefault(
                "endpoint_url", kwargs.pop("aws_endpoint_url")
            )
        if "aws_key" in kwargs:
            kwargs.setdefault("key", kwargs.pop("aws_key"))
        if "aws_secret" in kwargs:
            kwargs.setdefault("secret", kwargs.pop("aws_secret"))
        if "aws_token" in kwargs:
            kwargs.setdefault("token", kwargs.pop("aws_token"))

        # caching bucket regions to use the right one in signed urls, otherwise
        # it tries to randomly guess and creates wrong signature
        kwargs.setdefault("cache_regions", True)

        # We want to use newer v4 signature version since regions added after
        # 2014 are not going to support v2 which is the older one.
        # All regions support v4.
        kwargs.setdefault("config_kwargs", {}).setdefault("signature_version", "s3v4")

        return cast(S3FileSystem, super().create_fs(**kwargs))

    async def _fetch_dir(self, prefix, pbar, listing, data_storage):
        if prefix:
            prefix = prefix.lstrip(DELIMITER) + DELIMITER
        files = []
        subdirs = set()
        pbar_updated = 0
        async for info in self.fs._iterdir(self.name, prefix=prefix, versions=True):
            full_path = info["name"]
            _, subprefix, _ = self.fs.split_path(info["name"])
            if info["type"] == "directory":
                name = full_path.split(DELIMITER)[-1]
                await listing.insert_dir(
                    name,
                    TIME_ZERO,
                    prefix.rstrip("/"),
                    data_storage=data_storage,
                )
                subdirs.add(subprefix)
            else:
                files.append(self._dict_from_info(info, prefix.rstrip("/")))
                pbar_update_count = len(files) - pbar_updated
                if pbar_update_count >= UPDATE_CHUNKSIZE:
                    pbar.update(pbar_update_count)
                    pbar_updated += pbar_update_count
        if files:
            await data_storage.insert_nodes(files)
            await data_storage.update_last_inserted_at()
            pbar_update_count = len(files) - pbar_updated
            pbar.update(pbar_update_count)
            pbar_updated += pbar_update_count
        pbar.update(len(subdirs))
        found_count = len(subdirs) + pbar_updated
        return subdirs, found_count

    @staticmethod
    def clean_s3_version(ver):
        return ver if ver != "null" else ""

    def _dict_from_info(self, v, parent):
        return {
            "is_dir": False,
            "parent": parent,
            "name": v.get("Key", "").split(DELIMITER)[-1],
            # 'expires': expires,
            "checksum": "",
            "etag": v.get("ETag", "").strip('"'),
            "version": ClientS3.clean_s3_version(v.get("VersionId", "")),
            "is_latest": v.get("IsLatest", True),
            "last_modified": v.get("LastModified", ""),
            "size": v["size"],
            # 'storage_class': v.get('StorageClass'),
            "owner_name": v.get("Owner", {}).get("DisplayName", ""),
            "owner_id": v.get("Owner", {}).get("ID", ""),
            "anno": None,
        }
