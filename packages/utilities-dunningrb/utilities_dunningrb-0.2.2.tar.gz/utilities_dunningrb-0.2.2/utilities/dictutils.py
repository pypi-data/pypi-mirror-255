"""Define utility methods for working with dictionaries.
"""
from __future__ import annotations

import heapq
from collections import defaultdict
from typing import Any

from utilities import listutils


def confirm_keys(d: dict, *, keys: list) -> None:
    """Return boolean True if each of the elements in list keys is a key in the given dictionary."""
    if all([k in list(d.keys()) for k in keys]):
        return
    else:
        err_msg = (
            f"Parameter <d> does not contain all required keys.\n"
            f"\tRequired keys: {listutils.get_string(keys)}"
            f"\tReceived keys: {listutils.get_string(list(d.keys()))}."
        )
        raise ValueError(err_msg)


def compare_dicts(d1: dict, d2: dict) -> dict:
    """
    Return a dictionary of dictionaries comparing the given d1 and d2 dictionaries on the
    basis of the k-v pairs of each but without regard to the ordering of the keys in either.

    The returned dictionary contains four outer keys (as strings) that map to the result
    dictionaries:

        * "unique-to-d1": maps to a dictionary of k-v pairs where the keys are unique to d1.

        * "unique-to-d2": maps to a dictionary of k-v pairs where the keys are unique to d2.

        * "conflicting": maps to a dictionary of k-v pairs where the keys are common to d1 and d2
        but for each key the value in d1 does not equal the value in d2. Each key is mapped to a
        tuple that holds these two unequal values, with the first element coming from d1 and the
        second element coming from d2.

        * "identical": maps to a dictionary of k-v pairs where the keys are common to d1 and d2
        and for each key the value in d1 equals the value in d2, and is the value mapped by that
        same key in the returned dictionary.

    Notes:
        1. If the returned dictionary is constructed correctly, at least two of its
        result dictionaries will be populated, and each key of the given d1 and d2 dictionaries
        will appear exactly once in exactly one of the result dictionaries.

        2. If the returned dictionary is constructed correctly, there cannot be any tuple in
        the "conflicting" data for which the first and second elements are equal.

    """
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    shared_keys = d1_keys.intersection(d2_keys)
    unique_to_d1 = {k: d1[k] for k in d1_keys - d2_keys}
    unique_to_d2 = {k: d2[k] for k in d2_keys - d1_keys}
    conflicting = {k: (d1[k], d2[k]) for k in shared_keys if d1[k] != d2[k]}
    identical = {k: d1[k] for k in shared_keys if d1[k] == d2[k]}
    return {
        "unique-to-d1": unique_to_d1,
        "unique-to-d2": unique_to_d2,
        "conflicting": conflicting,
        "identical": identical,
    }


def get_pure_dict(d: defaultdict | dict) -> dict:  # Recursive.
    """Receives a defaultdict or dict with possibly nested defaultdicts and returns a pure dict
    object having the same k-v pairs."""
    new = {}
    for k, v in d.items():
        if isinstance(v, dict) or isinstance(v, defaultdict):
            new[k] = get_pure_dict(v)
        else:
            new[k] = v
    return new


def get_defaultdict():
    return defaultdict(get_defaultdict)


def get_key_for_max_value(d: dict) -> Any:
    """Return the key whose value is the maximum."""
    return max(d, key=d.get)


def get_keys_for_largest_n_values(d: dict, *, n: int = 1) -> list:
    """Return a list of the <n> keys whose mapped values are largest in the given dictionary.

    NOTE: The order of the returned keys is not guaranteed.
    """
    if n > 1:
        z = heapq.nlargest(n, d.items(), key=lambda i: i[0])
        return [i[0] for i in z]
    else:
        return [get_key_for_max_value(d)]


def get_string(
    d: dict | defaultdict, n: int = 0, num_tabs: int = 0
) -> str:  # Recursive.
    """Return a nicely-formatted string showing each kv pair in the given dictionary. Recursive."""

    # Convert d to type dict, but since get_pure_dict is recursive do this only on the first call.

    if n == 0 and isinstance(d, defaultdict):
        d_ = get_pure_dict(d)
    else:
        d_ = {k: v for k, v in d.items()}

    s = ""
    tabs = (n + num_tabs + 1) * "\t"
    for k, v in d_.items():
        if isinstance(v, dict):
            s += f"\n{tabs}{k}: {get_string(v, n + 1)}"  # Recursive call.
        else:
            s += f"\n{tabs}{k}: {v}"
    return s


def invert(d: dict) -> None:
    """Invert the kv pairs of the given dictionary, in place. If there are duplicated values
    only the last kv pair will be inverted to a vk pair and the other kv pairs will vanish.
    """
    orig_keys = list(d.keys())
    d_ = {v: k for k, v in d.items()}

    for v in list(d_.keys()):
        d[v] = d_[v]

    for k in orig_keys:
        d.pop(k)


def invert_strict(d: dict) -> None:
    """Similar to invert, which see, but if any values are duplicated raise ValueError."""
    if listutils.has_duplicates(list(d.values())):
        err_msg = "At least two keys map to the same value."
        raise ValueError(err_msg)
    invert(d)


def reorder_by_key(d: dict, *, reverse: bool = False) -> None:
    """Reorder the kv pairs of d by key, in place."""
    d_ = dict(sorted(d.items(), reverse=reverse))  # local copy, sorted

    for k_, v_ in d_.items():
        d.pop(k_)
        d[k_] = v_


def reorder_by_value(d: dict, reverse: bool = False) -> None:
    """Reorder the kv pairs by value, in place."""
    z = sorted(d.items(), key=lambda x: x[1], reverse=reverse)
    d_ = {k: v for k, v in z}  # local copy

    for k_, v_ in d_.items():
        d.pop(k_)
        d[k_] = v_


def replace_key(d: dict, *, k_new: Any, k_old: Any) -> dict:
    """Return a dictionary identical to the given dictionary but with k_old replaced by k_new."""
    try:
        d[k_new] = d.pop(k_old)  # noqa
    except KeyError:
        pass
    return d


def set_all_values(d: dict, *, value: Any) -> dict:
    """Set all values of the given dictionary d to the given parameter val."""
    return {k: value for k in d}
