import os
from importlib import import_module

from dql.catalog import Catalog
from dql.data_storage import SQLiteDataStorage
from dql.utils import get_envs_by_prefix

ADAPTER_ARG_PREFIX = "DVCX_ADAPTER_ARG_"
DISTRIBUTED_ARG_PREFIX = "DVCX_DISTRIBUTED_ARG_"


def get_db_adapter():
    db_adapter_import_path = os.environ.get("DVCX_DB_ADAPTER")
    adapter_arg_envs = get_envs_by_prefix(ADAPTER_ARG_PREFIX)
    # Convert env variable names to keyword argument names by lowercasing them
    adapter_args = {k.lower(): v for k, v in adapter_arg_envs.items()}

    if db_adapter_import_path:
        # DB Adapter paths are specified as (for example):
        # dql.data_storage.SQLiteDataStorage
        if "." not in db_adapter_import_path:
            raise RuntimeError(
                f"Invalid DVCX_DB_ADAPTER import path: {db_adapter_import_path}"
            )
        module_name, _, class_name = db_adapter_import_path.rpartition(".")
        db_adapter = import_module(module_name)
        db_adapter_class = getattr(db_adapter, class_name)
    else:
        db_adapter_class = SQLiteDataStorage
    return db_adapter_class(**adapter_args)


def get_distributed_class(**kwargs):
    distributed_import_path = os.environ.get("DVCX_DISTRIBUTED")
    distributed_arg_envs = get_envs_by_prefix(DISTRIBUTED_ARG_PREFIX)
    # Convert env variable names to keyword argument names by lowercasing them
    distributed_args = {k.lower(): v for k, v in distributed_arg_envs.items()}

    if not distributed_import_path:
        raise RuntimeError(
            "DVCX_DISTRIBUTED import path is required for distributed UDF processing."
        )
    # Distributed class paths are specified as (for example):
    # module.classname
    if "." not in distributed_import_path:
        raise RuntimeError(
            f"Invalid DVCX_DISTRIBUTED import path: {distributed_import_path}"
        )
    module_name, _, class_name = distributed_import_path.rpartition(".")
    distributed = import_module(module_name)
    distributed_class = getattr(distributed, class_name)
    return distributed_class(**{**distributed_args, **kwargs})


def get_catalog(client_config=None) -> Catalog:
    """
    Function that creates Catalog instance with appropriate data storage class
    Data storage class can be provided with env variable DVCX_DB_ADAPTER and if
    not provided, default one is used

    If data storage class expects some kwargs, they can be provided via
    env variables by adding them with prefix DVCX_DB_ADAPTER_ARG_ and
    name of variable after, e.g if it accepts team_id as kwargs we can provide
    DVCX_DB_ADAPTER_ARG_TEAM_ID=12345 env variable
    """
    return Catalog(get_db_adapter(), client_config=client_config)
