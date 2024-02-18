try:
    import pandas as pd
except ImportError:
    pd = None


def row_to_pandas(args, params):
    data = dict(zip([i.name for i in params], args))
    return pd.Series(data, name=data.get("name", None))


def row_list_to_pandas(args, params):
    df = pd.DataFrame(args, columns=[i.name for i in params])
    return df


def bin_to_array(data):
    integers = [
        int.from_bytes(data[i : i + 4], byteorder="big") for i in range(0, len(data), 4)
    ]
    return integers


def array_to_bin(integers):
    return b"".join(int.to_bytes(i, length=4, byteorder="big") for i in integers)


def union_dicts(*dicts):
    """Union dictionaries.
    Equivalent to `d1 | d2 | d3` in Python3.9+ but works in older versions.
    """
    result = None
    for d in dicts:
        if not isinstance(d, dict):
            raise ValueError("All arguments must be dictionaries.")
        if not result:
            result = d.copy()
        else:
            result.update(d)
    return result
