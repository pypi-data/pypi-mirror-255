import os

# support DVCX_ aliases for DQL_ env vars
for key in list(os.environ.keys()):
    if key.startswith("DQL_"):
        import warnings

        new_key = f"DVCX_{key[4:]}"
        warnings.warn(
            f"DQL env vars are deprecated. Forwarding {key} to {new_key}",
            DeprecationWarning,
            stacklevel=2,
        )
        os.environ.setdefault(new_key, os.environ[key])

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "UNKNOWN"
