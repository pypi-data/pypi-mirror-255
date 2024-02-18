import importlib.util
import os
import os.path as osp
import random
import stat
import sys
import time
from datetime import datetime
from itertools import islice
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from dateutil import tz
from dateutil.parser import isoparse
from tomlkit import parse

if TYPE_CHECKING:
    from tomlkit import TOMLDocument

GLOB_CHARS = ["?", "*", "[", "]"]
NUL = b"\0"

T = TypeVar("T", bound="DQLDir")


class DQLDir:
    DEFAULT = ".dql"
    CACHE = "cache"
    TMP = "tmp"
    DB = "db"
    ENV_VAR = "DVCX_DIR"
    ENV_VAR_DQL_ROOT = "DVCX_ROOT_DIR"

    def __init__(
        self,
        root: Optional[str] = None,
        cache: Optional[str] = None,
        tmp: Optional[str] = None,
        db: Optional[str] = None,
    ) -> None:
        self.root = osp.abspath(root) if root is not None else self.default_root()
        self.cache = (
            osp.abspath(cache) if cache is not None else osp.join(self.root, self.CACHE)
        )
        self.tmp = (
            osp.abspath(tmp) if tmp is not None else osp.join(self.root, self.TMP)
        )
        self.db = osp.abspath(db) if db is not None else osp.join(self.root, self.DB)

    def init(self):
        os.makedirs(self.root, exist_ok=True)
        os.makedirs(self.cache, exist_ok=True)
        os.makedirs(self.tmp, exist_ok=True)
        os.makedirs(osp.split(self.db)[0], exist_ok=True)

    @classmethod
    def default_root(cls) -> str:
        try:
            root_dir = os.environ[cls.ENV_VAR_DQL_ROOT]
        except KeyError:
            root_dir = os.getcwd()

        return osp.join(root_dir, cls.DEFAULT)

    @classmethod
    def find(cls: Type[T], create: bool = True) -> T:
        try:
            root = os.environ[cls.ENV_VAR]
        except KeyError:
            root = cls.default_root()
        instance = cls(root)
        if not osp.isdir(root):
            if create:
                instance.init()
            else:
                NotADirectoryError(root)
        return instance


def read_config(dql_root: str) -> Optional["TOMLDocument"]:
    project_path = osp.join(dql_root, "config")
    if osp.isfile(project_path):
        with open(project_path, encoding="utf-8") as f:
            text = f.read()
        return parse(text)
    return None


def get_remote_config(
    config: Optional["TOMLDocument"], remote: str = ""
) -> Mapping[str, str]:
    if config is None:
        return {"type": "local"}
    if not remote:
        try:
            remote = config["core"]["default-remote"]  # type: ignore[index,assignment]
        except KeyError:
            return {"type": "local"}
    try:
        remote_conf: Mapping[str, str] = config["remote"][remote]  # type: ignore[assignment,index]
    except KeyError:
        raise Exception(  # noqa: B904
            f"missing config section for default remote: remote.{remote}"
        )
    except Exception as exc:
        raise Exception("invalid config") from exc

    if not isinstance(remote_conf, Mapping):
        raise Exception(f"config section remote.{remote} must be a mapping")

    remote_type = remote_conf.get("type")
    if remote_type not in ("local", "http"):
        raise Exception(
            f'config section remote.{remote} must have "type" with one of: '
            '"local", "http"'
        )

    if remote_type == "http":
        for key in ["url", "username", "token"]:
            try:
                remote_conf[key]
            except KeyError:
                raise Exception(  # noqa: B904
                    f"config section remote.{remote} of type {remote_type} "
                    f"must contain key {key}"
                )
    elif remote_type != "local":
        raise Exception(
            f"config section remote.{remote} has invalid remote type {remote_type}"
        )
    return remote_conf


def human_time_to_int(time: str) -> Optional[int]:
    if not time:
        return None

    suffix = time[-1]
    try:
        num = int(time if suffix.isdigit() else time[:-1])
    except ValueError:
        return None
    return num * {
        "h": 60 * 60,
        "d": 60 * 60 * 24,
        "w": 60 * 60 * 24 * 7,
        "m": 31 * 24 * 60 * 60,
        "y": 60 * 60 * 24 * 365,
    }.get(suffix.lower(), 1)


def time_to_str(dt):
    if isinstance(dt, str):
        dt = isoparse(dt)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def time_to_local(dt: Union[datetime, str]) -> datetime:
    # TODO check usage
    if isinstance(dt, str):
        dt = isoparse(dt)
    try:
        return dt.astimezone(tz.tzlocal())
    except (OverflowError, OSError, ValueError):
        return dt


def time_to_local_str(dt: Union[datetime, str]) -> str:
    return time_to_str(time_to_local(dt))


def is_expired(expires: Optional[Union[datetime, str]]):
    if expires:
        return time_to_local(expires) < time_to_local(datetime.now())

    return False


SIZE_SUFFIXES = ["", "K", "M", "G", "T", "P", "E", "Z", "Y", "R", "Q"]


def sizeof_fmt(num, suffix="", si=False):
    power = 1000.0 if si else 1024.0
    for unit in SIZE_SUFFIXES[:-1]:
        if abs(num) < power:
            if not unit:
                return f"{num:4.0f}{suffix}"
            return f"{num:3.1f}{unit}{suffix}"
        num /= power
    return f"{num:.1f}Q{suffix}"


def suffix_to_number(num_str: str) -> int:
    try:
        if len(num_str) > 1:
            suffix = num_str[-1].upper()
            if suffix in SIZE_SUFFIXES:
                suffix_idx = SIZE_SUFFIXES.index(suffix)
                return int(num_str[:-1]) * (1024**suffix_idx)
        return int(num_str)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid number/suffix for: {num_str}")  # noqa: B904


def force_create_dir(name):
    if not os.path.exists(name):
        os.mkdir(name)
    elif not os.path.isdir(name):
        os.remove(name)
        os.mkdir(name)


def dql_paths_join(source_path: str, file_paths: Iterable[str]) -> Iterable[str]:
    source_parts = source_path.rstrip("/").split("/")
    if set(source_parts[-1]).intersection(GLOB_CHARS):
        # Remove last element if it is a glob match (such as *)
        source_parts.pop()
    source_stripped = "/".join(source_parts)
    return (f"{source_stripped}/{path.lstrip('/')}" for path in file_paths)


# From: https://docs.python.org/3/library/shutil.html#rmtree-example
def remove_readonly(func, path, _):
    "Clear the readonly bit and reattempt the removal"
    os.chmod(path, stat.S_IWRITE)
    func(path)


def sql_escape_like(search: str, escape: str = "\\") -> str:
    return (
        search.replace(escape, escape * 2)
        .replace("%", f"{escape}%")
        .replace("_", f"{escape}_")
    )


def get_envs_by_prefix(prefix: str) -> Dict[str, str]:
    """
    Function that searches env variables by some name prefix and returns
    the ones found, but with prefix being excluded from it's names
    """
    variables: Dict[str, str] = {}
    for env_name, env_value in os.environ.items():
        if env_name.startswith(prefix):
            variables[env_name[len(prefix) :]] = env_value

    return variables


def import_object(object_spec):
    filename, identifier = object_spec.rsplit(":", 1)
    filename = filename.strip()
    identifier = identifier.strip()

    if not identifier.isidentifier() or not filename.endswith(".py"):
        raise ValueError(f"Invalid object spec: {object_spec}")

    modname = os.path.abspath(filename)
    if modname in sys.modules:
        module = sys.modules[modname]
    else:
        # Use importlib to find and load the module from the given filename
        spec = importlib.util.spec_from_file_location(modname, filename)
        module = importlib.util.module_from_spec(spec)
        sys.modules[modname] = module
        spec.loader.exec_module(module)

    return getattr(module, identifier)


def parse_params_string(params: str):
    """
    Parse a string containing UDF class constructor parameters in the form
    `a, b, key=val` into *args and **kwargs.
    """
    args = []
    kwargs = {}
    for part in params.split():
        if "=" in part:
            key, val = part.split("=")
            kwargs[key] = val
        else:
            args.append(part)
    if any((args, kwargs)):
        return args, kwargs
    return None, None


def batched(iterable, n):
    "Batch data into tuples of length n. The last batch may be shorter."
    # Based on: https://docs.python.org/3/library/itertools.html#itertools-recipes
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("Batch size must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def chunk(input_list: List[Any], chunk_size: int) -> Iterable[List[Any]]:
    """Breaks list into iterable of chunks of defined size"""
    for i in range(0, len(input_list), chunk_size):
        yield input_list[i : i + chunk_size]


def flatten(items):
    for item in items:
        if isinstance(item, list):
            yield from item
        else:
            yield item


def retry_with_backoff(retries=5, backoff_sec=1):
    def retry(f):
        def wrapper(*args, **kwargs):
            num_tried = 0
            while True:
                try:
                    return f(*args, **kwargs)
                except Exception:
                    if num_tried == retries:
                        raise
                    sleep = (
                        backoff_sec * 2**num_tried + random.uniform(0, 1)  # noqa: S311
                    )
                    time.sleep(sleep)
                    num_tried += 1

        return wrapper

    return retry


def determine_processes(parallel: Optional[Union[bool, int]]) -> Union[bool, int]:
    if parallel is None and os.environ.get("DVCX_SETTINGS_PARALLEL") is not None:
        parallel = int(os.environ["DVCX_SETTINGS_PARALLEL"])
    if parallel is None or parallel is False:
        return False
    if parallel is True:
        return True
    if parallel == 0:
        return False
    if parallel < 0:
        return True
    return parallel


def get_env_list(
    key: str, default: Optional[Sequence] = None, sep: str = ","
) -> Optional[Sequence[str]]:
    try:
        str_val = os.environ[key]
    except KeyError:
        return default
    return str_val.split(sep=sep)
