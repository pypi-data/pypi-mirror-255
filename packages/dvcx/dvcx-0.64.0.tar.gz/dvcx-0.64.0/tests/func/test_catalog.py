import os
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch
from urllib.parse import urlparse

import pytest
import yaml
from fsspec.implementations.local import LocalFileSystem

from dql.catalog import indexer_formats, parse_edql_file
from dql.dataset import Status as DatasetStatus
from dql.error import (
    DatasetNotFoundError,
    QueryScriptCompileError,
    QueryScriptDatasetNotFound,
    QueryScriptRunError,
)

from ..utils import (
    DEFAULT_TREE,
    TARRED_TREE,
    WEBFORMAT_TREE,
    skip_if_not_sqlite,
    tree_from_path,
)


@pytest.fixture
def pre_created_ds_name():
    return "pre_created_dataset"


@pytest.fixture
def pre_created_ds(cloud_test_catalog, pre_created_ds_name):
    return cloud_test_catalog.catalog.create_shadow_dataset(
        pre_created_ds_name, [], populate=False
    )


@pytest.fixture
def mock_subprocess_run(cloud_test_catalog, listed_bucket):
    from subprocess import CompletedProcess

    with patch("subprocess.run") as mock_run:
        # create shadow dataset which would be created in subprocess
        cloud_test_catalog.catalog.create_shadow_dataset(
            "dogs_shadow_dataset",
            [f"{cloud_test_catalog.src_uri}/dogs/*"],
            recursive=True,
        )
        res = CompletedProcess([], 0)
        res.stdout = b"__ds__dogs_shadow_dataset__ds__\nuser log 1\nuser log 2"
        mock_run.return_value = res

        yield mock_run


@pytest.fixture
def mock_subprocess_run_error_exit_code(cloud_test_catalog):
    from subprocess import CompletedProcess

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess([], 1)
        yield mock_run


@pytest.fixture
def mock_subprocess_run_error_exit_code_10(cloud_test_catalog):
    from subprocess import CompletedProcess

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess([], 10)
        yield mock_run


@pytest.fixture
def mock_subprocess_run_dataset_not_created(cloud_test_catalog):
    from subprocess import CompletedProcess

    with patch("subprocess.run") as mock_run:
        res = CompletedProcess([], 0)
        res.stdout = b"random str"
        mock_run.return_value = res
        yield mock_run


def test_find(cloud_test_catalog):
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    assert set(catalog.find([src_uri])) == {
        f"{src_uri}/description",
        f"{src_uri}/cats/",
        f"{src_uri}/cats/cat1",
        f"{src_uri}/cats/cat2",
        f"{src_uri}/dogs/",
        f"{src_uri}/dogs/dog1",
        f"{src_uri}/dogs/dog2",
        f"{src_uri}/dogs/dog3",
        f"{src_uri}/dogs/others/",
        f"{src_uri}/dogs/others/dog4",
    }

    with pytest.raises(FileNotFoundError):
        set(catalog.find([f"{src_uri}/does_not_exist"]))


def test_find_names_paths_size_type(cloud_test_catalog):
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    assert set(catalog.find([src_uri], names=["*cat*"])) == {
        f"{src_uri}/cats/",
        f"{src_uri}/cats/cat1",
        f"{src_uri}/cats/cat2",
    }

    assert set(catalog.find([src_uri], names=["*cat*"], typ="dir")) == {
        f"{src_uri}/cats/",
    }

    assert len(list(catalog.find([src_uri], names=["*CAT*"]))) == 0

    assert set(catalog.find([src_uri], inames=["*CAT*"])) == {
        f"{src_uri}/cats/",
        f"{src_uri}/cats/cat1",
        f"{src_uri}/cats/cat2",
    }

    assert set(catalog.find([src_uri], paths=["*cats/cat*"])) == {
        f"{src_uri}/cats/cat1",
        f"{src_uri}/cats/cat2",
    }

    assert len(list(catalog.find([src_uri], paths=["*caTS/CaT**"]))) == 0

    assert set(catalog.find([src_uri], ipaths=["*caTS/CaT*"])) == {
        f"{src_uri}/cats/cat1",
        f"{src_uri}/cats/cat2",
    }

    assert set(catalog.find([src_uri], size="5", typ="f")) == {
        f"{src_uri}/description",
    }

    assert set(catalog.find([src_uri], size="-3", typ="f")) == {
        f"{src_uri}/dogs/dog2",
    }


def test_find_names_columns(cloud_test_catalog, cloud_type):
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    owner = "webfile" if cloud_type == "s3" else ""

    assert set(
        catalog.find(
            [src_uri],
            names=["*cat*"],
            columns=["du", "name", "owner", "path", "size", "type"],
        )
    ) == {
        "\t".join(columns)
        for columns in [
            ["8", "cats", "", f"{src_uri}/cats/", "0", "d"],
            ["4", "cat1", owner, f"{src_uri}/cats/cat1", "4", "f"],
            ["4", "cat2", owner, f"{src_uri}/cats/cat2", "4", "f"],
        ]
    }


@pytest.mark.parametrize(
    "recursive,star,dir_exists",
    (
        (True, True, False),
        (True, False, False),
        (True, False, True),
        (False, True, False),
        (False, False, False),
    ),
)
def test_cp_root(cloud_test_catalog, recursive, star, dir_exists):
    src_uri = cloud_test_catalog.src_uri
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog

    dest = working_dir / "data"

    if star:
        src_path = f"{src_uri}/*"
    else:
        src_path = src_uri

    if star:
        with pytest.raises(FileNotFoundError):
            catalog.cp([src_path], str(dest), recursive=recursive)

    if dir_exists or star:
        dest.mkdir()

    catalog.cp([src_path], str(dest), recursive=recursive)

    if not star and not recursive:
        # The root directory is skipped, so nothing is copied
        assert tree_from_path(dest) == {}
        return

    assert (dest / "description").read_text() == "Cats and Dogs"

    # Testing DQL File Contents
    assert dest.with_suffix(".edql").is_file()
    edql_contents = yaml.safe_load(dest.with_suffix(".edql").read_text())
    assert len(edql_contents) == 1
    data = edql_contents[0]
    assert data["data-source"]["uri"] == src_path.rstrip("/")
    expected_file_count = 7 if recursive else 1
    assert len(data["files"]) == expected_file_count
    files_by_name = {f["name"]: f for f in data["files"]}

    # Directories should never be saved
    assert "cats" not in files_by_name
    assert "dogs" not in files_by_name
    assert "others" not in files_by_name
    assert "dogs/others" not in files_by_name

    # Description is always copied (if anything is copied)
    prefix = "" if star or (recursive and not dir_exists) else "/"
    assert files_by_name[f"{prefix}description"]["size"] == 13

    if recursive:
        assert tree_from_path(dest) == DEFAULT_TREE
        assert files_by_name[f"{prefix}cats/cat1"]["size"] == 4
        assert files_by_name[f"{prefix}cats/cat2"]["size"] == 4
        assert files_by_name[f"{prefix}dogs/dog1"]["size"] == 4
        assert files_by_name[f"{prefix}dogs/dog2"]["size"] == 3
        assert files_by_name[f"{prefix}dogs/dog3"]["size"] == 4
        assert files_by_name[f"{prefix}dogs/others/dog4"]["size"] == 4
        return

    assert (dest / "cats").exists() is False
    assert (dest / "dogs").exists() is False
    for prefix in ["/", ""]:
        assert f"{prefix}cats/cat1" not in files_by_name
        assert f"{prefix}cats/cat2" not in files_by_name
        assert f"{prefix}dogs/dog1" not in files_by_name
        assert f"{prefix}dogs/dog2" not in files_by_name
        assert f"{prefix}dogs/dog3" not in files_by_name
        assert f"{prefix}dogs/others/dog4" not in files_by_name


@pytest.mark.parametrize(
    "cloud_type",
    ["s3", "gcs", "azure"],
    indirect=True,
)
def test_cp_local_dataset(cloud_test_catalog, dogs_registered_dataset):
    skip_if_not_sqlite()
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog

    dest = working_dir / "data"
    dest.mkdir()

    dataset_uri = dogs_registered_dataset.uri(version=1)

    catalog.cp([dataset_uri], str(dest))

    parsed = urlparse(str(cloud_test_catalog.src))
    netloc = Path(parsed.netloc.strip("/"))
    path = Path(parsed.path.strip("/"))

    assert tree_from_path(dest / netloc / path) == {
        "dogs": {
            "dog1": "woof",
            "dog2": "arf",
            "dog3": "bark",
            "others": {"dog4": "ruff"},
        }
    }


@pytest.mark.parametrize("tree", [TARRED_TREE], indirect=True)
@pytest.mark.parametrize("suffix", ["/", "/*"])
@pytest.mark.parametrize("recursive", [False, True])
@pytest.mark.parametrize("dir_exists", [False, True])
def test_cp_tar_root(cloud_test_catalog, suffix, recursive, dir_exists):
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.index([ctc.src_uri], index_processors=indexer_formats["tar-files"])
    dest = ctc.working_dir / "data"
    if dir_exists:
        dest.mkdir()
    src = f"{ctc.src_uri}/animals.tar{suffix}"
    dest_path = str(dest) + "/"

    if not dir_exists and suffix == "/*":
        with pytest.raises(FileNotFoundError):
            catalog.cp([src], dest_path, recursive=recursive, no_edql_file=True)
        return

    catalog.cp([src], dest_path, recursive=recursive, no_edql_file=True)

    expected = DEFAULT_TREE.copy()
    if not recursive:
        # Directories are not copied
        if suffix == "/":
            expected = {}
        else:
            for key in list(expected):
                if isinstance(expected[key], dict):
                    del expected[key]

    assert tree_from_path(dest) == expected


@pytest.mark.parametrize("tree", [TARRED_TREE], indirect=True)
def test_cp_full_tar(cloud_test_catalog):
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.index([ctc.src_uri], index_processors=indexer_formats["tar-files"])
    dest = ctc.working_dir / "data"
    dest.mkdir()
    src = f"{ctc.src_uri}/"
    catalog.cp([src], str(dest), recursive=True, no_edql_file=True)

    assert tree_from_path(dest, binary=True) == TARRED_TREE


@pytest.mark.parametrize(
    "recursive,star,slash,dir_exists",
    (
        (True, True, False, False),
        (True, False, False, False),
        (True, False, False, True),
        (True, False, True, False),
        (False, True, False, False),
        (False, False, False, False),
        (False, False, True, False),
    ),
)
def test_cp_subdir(cloud_test_catalog, recursive, star, slash, dir_exists):
    src_uri = f"{cloud_test_catalog.src_uri}/dogs"
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog

    dest = working_dir / "data"

    if star:
        src_path = f"{src_uri}/*"
    elif slash:
        src_path = f"{src_uri}/"
    else:
        src_path = src_uri

    if star:
        with pytest.raises(FileNotFoundError):
            catalog.cp([src_path], str(dest), recursive=recursive)

    if dir_exists or star:
        dest.mkdir()

    catalog.cp([src_path], str(dest), recursive=recursive)

    if not star and not recursive:
        # Directories are skipped, so nothing is copied
        assert tree_from_path(dest) == {}
        return

    # Testing DQL File Contents
    assert dest.with_suffix(".edql").is_file()
    edql_contents = yaml.safe_load(dest.with_suffix(".edql").read_text())
    assert len(edql_contents) == 1
    data = edql_contents[0]
    assert data["data-source"]["uri"] == src_path.rstrip("/")
    expected_file_count = 4 if recursive else 3
    assert len(data["files"]) == expected_file_count
    files_by_name = {f["name"]: f for f in data["files"]}

    # Directories should never be saved
    assert "others" not in files_by_name
    assert "dogs/others" not in files_by_name

    if not dir_exists:
        assert (dest / "dog1").read_text() == "woof"
        assert (dest / "dog2").read_text() == "arf"
        assert (dest / "dog3").read_text() == "bark"
        assert (dest / "dogs").exists() is False
        assert files_by_name["dog1"]["size"] == 4
        assert files_by_name["dog2"]["size"] == 3
        assert files_by_name["dog3"]["size"] == 4
        if recursive:
            assert (dest / "others" / "dog4").read_text() == "ruff"
            assert files_by_name["others/dog4"]["size"] == 4
        else:
            assert (dest / "others").exists() is False
            assert "others/dog4" not in files_by_name
        return

    assert tree_from_path(dest / "dogs") == DEFAULT_TREE["dogs"]
    assert (dest / "dog1").exists() is False
    assert (dest / "dog2").exists() is False
    assert (dest / "dog3").exists() is False
    assert (dest / "others").exists() is False
    assert files_by_name["dogs/dog1"]["size"] == 4
    assert files_by_name["dogs/dog2"]["size"] == 3
    assert files_by_name["dogs/dog3"]["size"] == 4
    assert files_by_name["dogs/others/dog4"]["size"] == 4


@pytest.mark.parametrize("tree", [TARRED_TREE], indirect=True)
@pytest.mark.parametrize("path", ["*/dogs", "animals.tar/dogs"])
@pytest.mark.parametrize("suffix", ["", "/", "/*"])
@pytest.mark.parametrize("recursive", [False, True])
@pytest.mark.parametrize("dir_exists", [False, True])
def test_cp_tar_subdir(cloud_test_catalog, path, suffix, recursive, dir_exists):
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.index([ctc.src_uri], index_processors=indexer_formats["tar-files"])
    dest = ctc.working_dir / "data"
    if dir_exists:
        dest.mkdir()
    src = f"{ctc.src_uri}/{path}{suffix}"

    if not dir_exists and suffix == "/*":
        with pytest.raises(FileNotFoundError):
            catalog.cp([src], str(dest), recursive=recursive)
        return

    catalog.cp([src], str(dest), recursive=recursive)

    expected = DEFAULT_TREE["dogs"].copy()
    if suffix in ("",) and dir_exists:
        expected = {"dogs": expected}
    if not recursive:
        # Directories are not copied
        if not dir_exists or suffix == "/":
            expected = {}
        else:
            for key in list(expected):
                if isinstance(expected[key], dict):
                    del expected[key]

    assert tree_from_path(dest) == expected


@pytest.mark.parametrize(
    "recursive,star,slash",
    (
        (True, True, False),
        (True, False, False),
        (True, False, True),
        (False, True, False),
        (False, False, False),
        (False, False, True),
    ),
)
def test_cp_multi_subdir(cloud_test_catalog, recursive, star, slash):  # noqa: PLR0915
    sources = [
        f"{cloud_test_catalog.src_uri}/cats",
        f"{cloud_test_catalog.src_uri}/dogs",
    ]
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog

    dest = working_dir / "data"

    if star:
        src_paths = [f"{src}/*" for src in sources]
    elif slash:
        src_paths = [f"{src}/" for src in sources]
    else:
        src_paths = sources

    with pytest.raises(FileNotFoundError):
        catalog.cp(src_paths, str(dest), recursive=recursive)

    dest.mkdir()

    catalog.cp(src_paths, str(dest), recursive=recursive)

    if not star and not recursive:
        # Directories are skipped, so nothing is copied
        assert tree_from_path(dest) == {}
        return

    # Testing DQL File Contents
    assert dest.with_suffix(".edql").is_file()
    edql_contents = yaml.safe_load(dest.with_suffix(".edql").read_text())
    assert len(edql_contents) == 2
    data_cats = edql_contents[0]
    data_dogs = edql_contents[1]
    assert data_cats["data-source"]["uri"] == src_paths[0].rstrip("/")
    assert data_dogs["data-source"]["uri"] == src_paths[1].rstrip("/")
    assert len(data_cats["files"]) == 2
    assert len(data_dogs["files"]) == 4 if recursive else 3
    cat_files_by_name = {f["name"]: f for f in data_cats["files"]}
    dog_files_by_name = {f["name"]: f for f in data_dogs["files"]}

    # Directories should never be saved
    assert "others" not in dog_files_by_name
    assert "dogs/others" not in dog_files_by_name

    if star or slash:
        assert (dest / "cat1").read_text() == "meow"
        assert (dest / "cat2").read_text() == "mrow"
        assert (dest / "dog1").read_text() == "woof"
        assert (dest / "dog2").read_text() == "arf"
        assert (dest / "dog3").read_text() == "bark"
        assert (dest / "cats").exists() is False
        assert (dest / "dogs").exists() is False
        assert cat_files_by_name["cat1"]["size"] == 4
        assert cat_files_by_name["cat2"]["size"] == 4
        assert dog_files_by_name["dog1"]["size"] == 4
        assert dog_files_by_name["dog2"]["size"] == 3
        assert dog_files_by_name["dog3"]["size"] == 4
        if recursive:
            assert (dest / "others" / "dog4").read_text() == "ruff"
            assert dog_files_by_name["others/dog4"]["size"] == 4
        else:
            assert (dest / "others").exists() is False
            assert "others/dog4" not in dog_files_by_name
        return

    assert (dest / "cats" / "cat1").read_text() == "meow"
    assert (dest / "cats" / "cat2").read_text() == "mrow"
    assert (dest / "dogs" / "dog1").read_text() == "woof"
    assert (dest / "dogs" / "dog2").read_text() == "arf"
    assert (dest / "dogs" / "dog3").read_text() == "bark"
    assert (dest / "dogs" / "others" / "dog4").read_text() == "ruff"
    assert (dest / "cat1").exists() is False
    assert (dest / "cat2").exists() is False
    assert (dest / "dog1").exists() is False
    assert (dest / "dog2").exists() is False
    assert (dest / "dog3").exists() is False
    assert (dest / "others").exists() is False
    assert cat_files_by_name["cats/cat1"]["size"] == 4
    assert cat_files_by_name["cats/cat2"]["size"] == 4
    assert dog_files_by_name["dogs/dog1"]["size"] == 4
    assert dog_files_by_name["dogs/dog2"]["size"] == 3
    assert dog_files_by_name["dogs/dog3"]["size"] == 4
    assert dog_files_by_name["dogs/others/dog4"]["size"] == 4


def test_cp_double_subdir(cloud_test_catalog):
    src_path = f"{cloud_test_catalog.src_uri}/dogs/others"
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog
    dest = working_dir / "data"

    catalog.cp([src_path], str(dest), recursive=True)

    # Testing DQL File Contents
    assert dest.with_suffix(".edql").is_file()
    edql_contents = yaml.safe_load(dest.with_suffix(".edql").read_text())
    assert len(edql_contents) == 1
    data = edql_contents[0]
    assert data["data-source"]["uri"] == src_path.rstrip("/")
    assert len(data["files"]) == 1
    files_by_name = {f["name"]: f for f in data["files"]}

    # Directories should never be saved
    assert "others" not in files_by_name
    assert "dogs/others" not in files_by_name

    assert (dest / "dogs").exists() is False
    assert (dest / "others").exists() is False
    assert (dest / "dog4").read_text() == "ruff"
    assert files_by_name["dog4"]["size"] == 4


@pytest.mark.parametrize("no_glob", (True, False))
def test_cp_single_file(cloud_test_catalog, no_glob):
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog
    dest = working_dir / "data"
    src_path = f"{cloud_test_catalog.src_uri}/dogs/dog1"
    dest.mkdir()

    catalog.cp([src_path], str(dest / "local_dog"), no_edql_file=True, no_glob=no_glob)

    assert tree_from_path(dest) == {"local_dog": "woof"}


@pytest.mark.parametrize("tree", [{"foo": "original"}], indirect=True)
def test_storage_mutation(cloud_test_catalog):
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog
    src_path = f"{cloud_test_catalog.src_uri}/foo"

    dest = working_dir / "data1"
    dest.mkdir()
    catalog.cp([src_path], str(dest / "local"), no_edql_file=True)
    assert tree_from_path(dest) == {"local": "original"}

    # Storage modified without reindexing, we get the old version from cache.
    (cloud_test_catalog.src / "foo").write_text("modified")
    dest = working_dir / "data2"
    dest.mkdir()
    catalog.cp([src_path], str(dest / "local"), no_edql_file=True)
    assert tree_from_path(dest) == {"local": "original"}

    # Storage modified without reindexing.
    # Since the old version cannot be found in storage or cache, it's an error.
    catalog.cache.clear()
    dest = working_dir / "data3"
    dest.mkdir()
    with pytest.raises(FileNotFoundError):
        catalog.cp([src_path], str(dest / "local"), no_edql_file=True)
    assert tree_from_path(dest) == {}

    # Storage modified with reindexing, we get the new version.
    catalog.index([cloud_test_catalog.src_uri], update=True)
    dest = working_dir / "data4"
    dest.mkdir()
    catalog.cp([src_path], str(dest / "local"), no_edql_file=True)
    assert tree_from_path(dest) == {"local": "modified"}


def test_cp_edql_file_options(cloud_test_catalog):
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog
    dest = working_dir / "data"
    src_path = f"{cloud_test_catalog.src_uri}/dogs/*"
    edql_file = working_dir / "custom_name.edql"

    catalog.cp(
        [src_path], str(dest), recursive=False, edql_only=True, edql_file=str(edql_file)
    )

    assert (dest / "dog1").exists() is False
    assert (dest / "dog2").exists() is False
    assert (dest / "dog3").exists() is False
    assert (dest / "dogs").exists() is False
    assert (dest / "others").exists() is False
    assert dest.with_suffix(".edql").exists() is False

    # Testing DQL File Contents
    assert edql_file.is_file()
    edql_contents = yaml.safe_load(edql_file.read_text())
    assert len(edql_contents) == 1
    data = edql_contents[0]
    assert data["data-source"]["uri"] == src_path
    expected_file_count = 3
    assert len(data["files"]) == expected_file_count
    files_by_name = {f["name"]: f for f in data["files"]}

    assert parse_edql_file(str(edql_file)) == edql_contents

    # Directories should never be saved
    assert "others" not in files_by_name
    assert "dogs/others" not in files_by_name

    assert files_by_name["dog1"]["size"] == 4
    assert files_by_name["dog2"]["size"] == 3
    assert files_by_name["dog3"]["size"] == 4
    assert "others/dog4" not in files_by_name

    with pytest.raises(FileNotFoundError):
        # Should fail, as * will not be expanded
        catalog.cp(
            [src_path],
            str(dest),
            recursive=False,
            edql_only=True,
            edql_file=str(edql_file),
            no_glob=True,
        )

    # Should succeed, as the DQL file exists check will be skipped
    edql_only_data = catalog.cp(
        [src_path],
        str(dest),
        recursive=False,
        edql_only=True,
        edql_file=str(edql_file),
        force=True,
    )

    # Check the returned DQL data contents
    assert len(edql_only_data) == len(edql_contents)
    edql_only_source = edql_only_data[0]
    assert edql_only_source["data-source"]["uri"] == src_path.rstrip("/")
    assert edql_only_source["files"] == data["files"]


def test_cp_edql_file_sources(cloud_test_catalog):  # noqa: PLR0915
    sources = [
        f"{cloud_test_catalog.src_uri}/cats/",
        f"{cloud_test_catalog.src_uri}/dogs/*",
    ]
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog

    dest = working_dir / "data"

    edql_files = [
        working_dir / "custom_cats.edql",
        working_dir / "custom_dogs.edql",
    ]

    catalog.cp(
        sources[:1],
        str(dest),
        recursive=True,
        edql_only=True,
        edql_file=str(edql_files[0]),
    )

    catalog.cp(
        sources[1:],
        str(dest),
        recursive=True,
        edql_only=True,
        edql_file=str(edql_files[1]),
    )

    # Files should not be copied yet
    assert (dest / "cat1").exists() is False
    assert (dest / "cat2").exists() is False
    assert (dest / "cats").exists() is False
    assert (dest / "dog1").exists() is False
    assert (dest / "dog2").exists() is False
    assert (dest / "dog3").exists() is False
    assert (dest / "dogs").exists() is False
    assert (dest / "others").exists() is False

    # Testing DQL File Contents
    edql_data = []
    for dqf in edql_files:
        assert dqf.is_file()
        edql_contents = yaml.safe_load(dqf.read_text())
        assert len(edql_contents) == 1
        edql_data.extend(edql_contents)

    assert len(edql_data) == 2
    data_cats1 = edql_data[0]
    data_dogs1 = edql_data[1]
    assert data_cats1["data-source"]["uri"] == sources[0].rstrip("/")
    assert data_dogs1["data-source"]["uri"] == sources[1].rstrip("/")
    assert len(data_cats1["files"]) == 2
    assert len(data_dogs1["files"]) == 4
    cat_files_by_name1 = {f["name"]: f for f in data_cats1["files"]}
    dog_files_by_name1 = {f["name"]: f for f in data_dogs1["files"]}

    # Directories should never be saved
    assert "others" not in dog_files_by_name1
    assert "dogs/others" not in dog_files_by_name1

    assert cat_files_by_name1["cat1"]["size"] == 4
    assert cat_files_by_name1["cat2"]["size"] == 4
    assert dog_files_by_name1["dog1"]["size"] == 4
    assert dog_files_by_name1["dog2"]["size"] == 3
    assert dog_files_by_name1["dog3"]["size"] == 4
    assert dog_files_by_name1["others/dog4"]["size"] == 4

    assert not dest.exists()

    with pytest.raises(FileNotFoundError):
        catalog.cp([str(dqf) for dqf in edql_files], str(dest), recursive=True)

    dest.mkdir()

    # Copy using these DQL files as sources
    catalog.cp([str(dqf) for dqf in edql_files], str(dest), recursive=True)

    # Files should now be copied
    assert (dest / "cat1").read_text() == "meow"
    assert (dest / "cat2").read_text() == "mrow"
    assert (dest / "dog1").read_text() == "woof"
    assert (dest / "dog2").read_text() == "arf"
    assert (dest / "dog3").read_text() == "bark"
    assert (dest / "others" / "dog4").read_text() == "ruff"

    # Testing DQL File Contents
    assert dest.with_suffix(".edql").is_file()
    edql_contents = yaml.safe_load(dest.with_suffix(".edql").read_text())
    assert len(edql_contents) == 2
    data_cats2 = edql_contents[0]
    data_dogs2 = edql_contents[1]
    assert data_cats2["data-source"]["uri"] == sources[0].rstrip("/")
    assert data_dogs2["data-source"]["uri"] == sources[1].rstrip("/")
    assert len(data_cats2["files"]) == 2
    assert len(data_dogs2["files"]) == 4
    cat_files_by_name2 = {f["name"]: f for f in data_cats2["files"]}
    dog_files_by_name2 = {f["name"]: f for f in data_dogs2["files"]}

    # Directories should never be saved
    assert "others" not in dog_files_by_name2
    assert "dogs/others" not in dog_files_by_name2

    assert cat_files_by_name2["cat1"]["size"] == 4
    assert cat_files_by_name2["cat2"]["size"] == 4
    assert dog_files_by_name2["dog1"]["size"] == 4
    assert dog_files_by_name2["dog2"]["size"] == 3
    assert dog_files_by_name2["dog3"]["size"] == 4
    assert dog_files_by_name2["others/dog4"]["size"] == 4


@pytest.mark.parametrize("cloud_type, version_aware", [("file", False)], indirect=True)
def test_cp_symlinks(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    catalog.client_config["use_symlinks"] = True
    src_uri = cloud_test_catalog.src_uri
    work_dir = cloud_test_catalog.working_dir
    dest = work_dir / "data"
    dest.mkdir()
    catalog.cp([f"{src_uri}/dogs/"], str(dest), recursive=True)

    assert (dest / "dog1").is_symlink()
    assert os.path.realpath(dest / "dog1") == str(
        cloud_test_catalog.src / "dogs" / "dog1"
    )
    assert (dest / "dog1").read_text() == "woof"
    assert (dest / "others" / "dog4").is_symlink()
    assert os.path.realpath(dest / "others" / "dog4") == str(
        cloud_test_catalog.src / "dogs" / "others" / "dog4"
    )
    assert (dest / "others" / "dog4").read_text() == "ruff"


def test_du(cloud_test_catalog):
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    expected_results = [
        (f"{src_uri}/cats/", 8),
        (f"{src_uri}/dogs/others/", 4),
        (f"{src_uri}/dogs/", 15),
        (f"{src_uri}/", 36),
    ]

    results = catalog.du([src_uri])
    assert set(results) == set(expected_results[3:])

    results = catalog.du([src_uri], depth=1)
    assert set(results) == set(expected_results[:1] + expected_results[2:])

    results = catalog.du([src_uri], depth=5)
    assert set(results) == set(expected_results)


def test_ls_glob(cloud_test_catalog):
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    assert sorted(
        (source.node.name, [r[0] for r in results])
        for source, results in catalog.ls([f"{src_uri}/dogs/dog*"], fields=["name"])
    ) == [("dog1", ["dog1"]), ("dog2", ["dog2"]), ("dog3", ["dog3"])]


def test_ls_prefix_not_found(cloud_test_catalog):
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog
    with pytest.raises(FileNotFoundError):
        list(catalog.ls([f"{src_uri}/bogus/"], fields=["name"]))


def clear_storages(catalog):
    ds = catalog.data_storage
    ds.mdb.execute(ds.storages.delete())


@pytest.mark.parametrize("cloud_type", ["file"], indirect=True)
@pytest.mark.parametrize("use_path", [False, True])
def test_add_storage(cloud_test_catalog, use_path):
    catalog = cloud_test_catalog.catalog
    src_uri = cloud_test_catalog.src_uri
    clear_storages(catalog)
    if use_path:
        src = LocalFileSystem._strip_protocol(src_uri)
        src = os.path.relpath(src)
    else:
        src = src_uri
    with pytest.raises(RuntimeError):
        catalog.index([src_uri])
    catalog.add_storage(src)
    catalog.index([src_uri])


@pytest.mark.parametrize("tree", [TARRED_TREE], indirect=True)
def test_tar_loader(cloud_test_catalog):
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.index([ctc.src_uri], index_processors=indexer_formats["tar-files"])


@pytest.mark.parametrize("tree", [WEBFORMAT_TREE], indirect=True)
def test_webformat_loader(cloud_test_catalog):
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.index([ctc.src_uri], index_processors=indexer_formats["json-pair"])


def test_add_storage_error(cloud_test_catalog, cloud_type):
    catalog = cloud_test_catalog.catalog
    src_uri = cloud_test_catalog.src_uri
    if cloud_type == "file":
        src_uri += "/invalid"
    with pytest.raises(RuntimeError):
        catalog.add_storage(src_uri)


@pytest.mark.parametrize("tree", [TARRED_TREE], indirect=True)
def test_ls_subobjects(cloud_test_catalog):
    ctc = cloud_test_catalog
    catalog = ctc.catalog
    catalog.index([ctc.src_uri], index_processors=indexer_formats["tar-files"])

    def do_ls(target):
        ((_, results),) = list(catalog.ls([target], fields=["name"]))
        results = list(results)
        result_set = {x[0] for x in results}
        assert len(result_set) == len(results)
        return result_set

    assert do_ls(ctc.src_uri) == {"animals.tar"}
    assert do_ls(f"{ctc.src_uri}/animals.tar") == {"animals.tar"}
    assert do_ls(f"{ctc.src_uri}/animals.tar/dogs") == {
        "dog1",
        "dog2",
        "dog3",
        "others",
    }
    assert do_ls(f"{ctc.src_uri}/animals.tar/") == {"description", "cats", "dogs"}
    assert do_ls(f"{ctc.src_uri}/*.tar/") == {"description", "cats", "dogs"}
    assert do_ls(f"{ctc.src_uri}/*.tar/desc*") == {"description"}


def test_index_error(cloud_test_catalog):
    protocol = cloud_test_catalog.src_uri.split("://", 1)[0]
    # XXX: different clients raise inconsistent exceptions
    with pytest.raises(Exception):  # noqa: B017
        cloud_test_catalog.catalog.index([f"{protocol}://does_not_exist"])


def test_query(cloud_test_catalog, mock_subprocess_run):
    catalog = cloud_test_catalog.catalog
    src_uri = cloud_test_catalog.src_uri

    query_script = f"""\
    from dql.query import C, DatasetQuery
    DatasetQuery({src_uri!r})
    """
    query_script = dedent(query_script)

    dataset = catalog.query(query_script)
    assert dataset
    assert {r.name for r in catalog.ls_dataset_rows(dataset.name)} == {
        "dog1",
        "dog2",
        "dog3",
        "dog4",
    }
    assert dataset.sources == ""
    assert dataset.query_script == query_script


def test_query_with_pre_created_dataset(
    cloud_test_catalog, mock_subprocess_run, pre_created_ds
):
    catalog = cloud_test_catalog.catalog
    src_uri = cloud_test_catalog.src_uri

    query_script = f"""
from dql.query import DatasetQuery, C
DatasetQuery('{src_uri}/dogs')
    """

    dataset = catalog.query(query_script, dataset=pre_created_ds)

    assert dataset.name == pre_created_ds.name
    assert {r.name for r in catalog.ls_dataset_rows(dataset.name)} == {
        "dog1",
        "dog2",
        "dog3",
        "dog4",
    }
    assert dataset.script_output == "user log 1\nuser log 2\n"

    # check that temp dataset created in a script is removed after
    with pytest.raises(DatasetNotFoundError):
        catalog.get_dataset("dogs_shadow_dataset")


def test_query_fail_to_compile(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog

    query_script = "syntax error"

    with pytest.raises(QueryScriptCompileError):
        catalog.query(query_script)


def test_query_fail_to_compile_pre_created_dataset(cloud_test_catalog, pre_created_ds):
    catalog = cloud_test_catalog.catalog
    query_script = """
import json
syntax error
"""

    with pytest.raises(QueryScriptCompileError):
        catalog.query(query_script, dataset=pre_created_ds)

    pre_created_ds = catalog.get_dataset(pre_created_ds.name)
    assert pre_created_ds.status == DatasetStatus.FAILED
    assert pre_created_ds.error_message.startswith("Query script failed to compile")
    assert pre_created_ds.error_stack
    assert pre_created_ds.sources == ""
    assert pre_created_ds.query_script == query_script


def test_query_subprocess_wrong_return_code(
    cloud_test_catalog, mock_subprocess_run_error_exit_code
):
    catalog = cloud_test_catalog.catalog
    src_uri = cloud_test_catalog.src_uri

    query_script = f"""
from dql.query import DatasetQuery, C
DatasetQuery('{src_uri}')
    """

    with pytest.raises(QueryScriptRunError):
        catalog.query(query_script)


def test_query_subprocess_wrong_return_code_pre_created_dataset(
    cloud_test_catalog, mock_subprocess_run_error_exit_code, pre_created_ds
):
    catalog = cloud_test_catalog.catalog
    src_uri = cloud_test_catalog.src_uri

    query_script = f"""
from dql.query import DatasetQuery, C
DatasetQuery('{src_uri}')
    """

    with pytest.raises(QueryScriptRunError):
        catalog.query(query_script, dataset=pre_created_ds)

    pre_created_ds = catalog.get_dataset(pre_created_ds.name)
    assert pre_created_ds.status == DatasetStatus.FAILED
    assert pre_created_ds.error_message.startswith(
        "Query script exited with error code 1"
    )
    assert pre_created_ds.error_stack
    assert pre_created_ds.sources == ""
    assert pre_created_ds.query_script == query_script


def test_query_last_statement_not_expression(
    cloud_test_catalog, mock_subprocess_run_error_exit_code_10, pre_created_ds
):
    catalog = cloud_test_catalog.catalog
    src_uri = cloud_test_catalog.src_uri

    query_script = f"""
from dql.query import DatasetQuery, C
ds = DatasetQuery('{src_uri}')
    """

    with pytest.raises(QueryScriptCompileError):
        catalog.query(query_script, dataset=pre_created_ds)

    pre_created_ds = catalog.get_dataset(pre_created_ds.name)
    assert pre_created_ds.status == DatasetStatus.FAILED
    assert pre_created_ds.error_message == (
        "Query script failed to compile, "
        "reason: Last line in a script was not an expression"
    )
    assert pre_created_ds.error_stack


def test_query_last_statement_not_ds_query_instance(
    cloud_test_catalog, mock_subprocess_run_error_exit_code_10, pre_created_ds
):
    catalog = cloud_test_catalog.catalog
    src_uri = cloud_test_catalog.src_uri

    query_script = f"""
from dql.query import DatasetQuery, C
ds = DatasetQuery('{src_uri}')
5
    """

    with pytest.raises(QueryScriptRunError):
        catalog.query(query_script, dataset=pre_created_ds)

    pre_created_ds = catalog.get_dataset(pre_created_ds.name)
    assert pre_created_ds.status == DatasetStatus.FAILED
    assert pre_created_ds.error_message == (
        "Last line in a script was not an instance of DatasetQuery"
    )
    assert pre_created_ds.error_stack
    assert pre_created_ds.sources == ""
    assert pre_created_ds.query_script == query_script


def test_query_dataset_not_returned(
    cloud_test_catalog, mock_subprocess_run_dataset_not_created
):
    catalog = cloud_test_catalog.catalog
    src_uri = cloud_test_catalog.src_uri

    query_script = f"""
from dql.query import DatasetQuery, C
DatasetQuery('{src_uri}')
    """

    with pytest.raises(QueryScriptDatasetNotFound):
        catalog.query(query_script)


def test_query_dataset_not_returned_pre_created_dataset(
    cloud_test_catalog, mock_subprocess_run_dataset_not_created, pre_created_ds
):
    catalog = cloud_test_catalog.catalog
    src_uri = cloud_test_catalog.src_uri

    query_script = f"""
from dql.query import DatasetQuery, C
DatasetQuery('{src_uri}')
    """

    with pytest.raises(QueryScriptDatasetNotFound):
        catalog.query(query_script, dataset=pre_created_ds)

    pre_created_ds = catalog.get_dataset(pre_created_ds.name)
    assert pre_created_ds.status == DatasetStatus.FAILED
    assert pre_created_ds.error_message == ("Internal error on creating dataset")
    assert pre_created_ds.error_stack
    assert pre_created_ds.sources == ""
    assert pre_created_ds.query_script == query_script
