from typing import Any
import collections.abc


def update_dict(d: collections.abc.Mapping, u: Any):
    """
    Update nested dictionary
    """
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def extend_dict(d: collections.abc.Mapping, u):
    """
    Extend nested dictionary
    """
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = extend_dict(d.get(k, {}), v)
        elif k not in d:
            d[k] = v
    return d
