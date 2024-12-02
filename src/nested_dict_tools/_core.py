"""
Nested dictionary utilities core.

This module provides a set of utilities for working with python nested
dictionaries. It includes recursive types describing nested mappings and
dictionaries, fully typed functions to flatten and unflatten dictionaries,
retrieve and set deeply nested values.

This module provides a set of utilities for working with Python nested
dictionaries. It includes:

- Recursive types for describing nested mappings and dictionaries.
- Fully typed functions to:
    - Flatten and unflatten nested dictionaries.
    - Get and set deeply nested values.
    - Filter and map functions on leaves

flatten adapted from https://gist.github.com/crscardellino/82507c13ba2b832b860ba0960759b925

This code is licensed under the terms of the MIT license.
"""

from collections.abc import Callable, Iterable, Iterator, Mapping, MutableMapping, Sequence
from typing import Any, Literal, cast, overload

type NestedMapping[K, V] = Mapping[K, NestedMappingNode[K, V]]
type NestedMappingNode[K, V] = V | NestedMapping[K, V]

type NestedMutableMapping[K, V] = MutableMapping[K, NestedMutableMappingNode[K, V]]
type NestedMutableMappingNode[K, V] = V | NestedMutableMapping[K, V]

type NestedDict[K, V] = dict[K, NestedDictNode[K, V]]
type NestedDictNode[K, V] = V | NestedDict[K, V]


class KeySeparatorCollisionError(Exception):
    """Separator collides with a key of a nested dict."""

    def __init__(self, key: str, sep: str) -> None:
        super().__init__(f"Separator `{sep}` is a substring of key `{key}`. Change separator.")


def flatten_dict[K: str, V](d: NestedMapping[K, V], sep: str = ".") -> dict[str, V]:
    """
    Recursively flatten a dictionary.

    Args:
        d: Nested dictionary or mapping to flatten.
        sep: Separator used to represent nested structures as flattened keys.

    Returns:
        The flattened dictionary.

    Raises:
        KeySeparatorCollisionError: If the separator is a  substring of a key of
            the nested dictionary.

    >>> flatten_dict({"a": {"b": 1, "c": 2}, "d": {"e": {"f": 3}}})
    {'a.b': 1, 'a.c': 2, 'd.e.f': 3}

    >>> flatten_dict({"a.": 1})
    Traceback (most recent call last):
    ...
    nested_dict_tools._core.KeySeparatorCollisionError: Separator `.` is a substring of key `a.`. Change separator.
    """

    def flatten_dict_gen(
        d: NestedMapping[K, V], parent_key: str | None, sep: str
    ) -> Iterator[tuple[str, V]]:
        for k, v in d.items():
            if sep in k:
                raise KeySeparatorCollisionError(k, sep)
            concat_key = parent_key + sep + k if parent_key is not None else k
            if isinstance(v, Mapping):
                yield from flatten_dict_gen(cast("NestedMapping[K, V]", v), concat_key, sep)
            else:
                yield concat_key, v

    return dict(flatten_dict_gen(d, None, sep))


def unflatten_dict[K: str, V](d: Mapping[K, V], sep: str = ".") -> NestedDict[str, V]:
    """
    Unflatten a dictionary flattened with separator.

    Args:
        d: The flattened dictionary to unflatten.
        sep: The separator used to flatten the dictionary.

    Returns:
        The unflattened dictionary.

    >>> unflatten_dict({"a.b": 1, "a.c": 2, "d.e.f": 3})
    {'a': {'b': 1, 'c': 2}, 'd': {'e': {'f': 3}}}

    >>> unflatten_dict({"x_y_z": 10, "x_y_w": 20, "a": 5}, sep="_")
    {'x': {'y': {'z': 10, 'w': 20}}, 'a': 5}
    """
    nested = {}
    for concat_key, v in d.items():
        keys = concat_key.split(sep)

        sub_dict = nested
        for key in keys[:-1]:
            sub_dict[key] = sub_dict = sub_dict.get(key, {})

        sub_dict[keys[-1]] = v

    return nested


@overload
def get_deep[K, V](
    d: NestedMapping[K, V],
    keys: Iterable[K],
    default: Any = None,
    no_default: Literal[True] = True,
) -> V | NestedMapping[K, V]: ...


@overload
def get_deep[K, V, D](
    d: NestedMapping[K, V],
    keys: Iterable[K],
    default: D = None,
    no_default: bool = False,
) -> V | D | NestedMapping[K, V]: ...


def get_deep[K, V, D](
    d: NestedMapping[K, V],
    keys: Iterable[K],
    default: D = None,
    no_default: bool = False,
) -> V | D | NestedMapping[K, V]:
    """
    Retrieve a value from a nested dictionary using a sequence of keys.

    Args:
        d: Nested dictionary.
        keys: Sequence of keys.
        default: Default to return if a key is missing and no_default is False.
        no_default: Wether to return default in case of missing keys.

    Returns:
        The item corresponding to the sequence of keys.

    >>> data = {"a": {"b": {"c": 42}}}
    >>> get_deep(data, ["a", "b", "c"])
    42

    >>> get_deep(data, ["a", "b", "x"], default="missing")
    'missing'

    >>> get_deep(data, ["a", "x"], default="missing")
    'missing'

    >>> get_deep(data, ["a", "x"], no_default=True)
    Traceback (most recent call last):
    ...
    KeyError: 'x'

    >>> get_deep(data, ["a", "b"])
    {'c': 42}
    """
    sub_dict = d
    try:
        for key in keys:
            sub_dict = sub_dict[key]  # pyright: ignore[reportIndexIssue]
    except (KeyError, TypeError):
        if no_default:
            raise
        return default

    return sub_dict


# ? Is it possible to replace Any by V in the type annotation without having problems because of
# ? invariance of mutable mappings?
def set_deep[K, V](d: NestedMutableMapping[K, Any], keys: Sequence[K], value: Any) -> None:
    """
    Set a value in a nested dictionary, creating any missing sub-dictionaries along the way.

    Args:
        d: The nested dictionary to modify.
        keys: A sequence of keys leading to the location where the value will be
        set.
        value: The value to set at the specified location.

    >>> data = {"a": {"b": {"c": 42}}}
    >>> set_deep(data, ["a", "b", "d"], 100)
    >>> data
    {'a': {'b': {'c': 42, 'd': 100}}}

    >>> data = {}
    >>> set_deep(data, ["x", "y", "z"], "new")
    >>> data
    {'x': {'y': {'z': 'new'}}}
    """
    sub_dict: NestedMutableMapping[K, V] = d
    for key in keys[:-1]:
        try:
            # Raise TypeError if an existing key doesn't map to a dict
            sub_dict = cast("NestedMutableMapping[K, V]", sub_dict[key])
        except KeyError:
            sub_dict[key] = sub_dict = {}

    sub_dict[keys[-1]] = value


@overload
def map_leaves[K, V, W](
    func: Callable[[V], W], nested_dict1: NestedMapping[K, V], /
) -> NestedMapping[K, W]: ...


@overload
def map_leaves[K, V1, V2, W](
    func: Callable[[V1, V2], W],
    nested_dict1: NestedMapping[K, V1],
    nested_dict2: NestedMapping[K, V2],
    /,
) -> NestedMapping[K, W]: ...


@overload
def map_leaves[K, V1, V2, V3, W](
    func: Callable[[V1, V2, V3], W],
    nested_dict1: NestedMapping[K, V1],
    nested_dict2: NestedMapping[K, V2],
    nested_dict3: NestedMapping[K, V3],
    /,
) -> NestedMapping[K, W]: ...


@overload
def map_leaves[K, V1, V2, V3, V4, W](
    func: Callable[[V1, V2, V3, V4], W],
    nested_dict1: NestedMapping[K, V1],
    nested_dict2: NestedMapping[K, V2],
    nested_dict3: NestedMapping[K, V3],
    nested_dict4: NestedMapping[K, V4],
    /,
) -> NestedMapping[K, W]: ...


@overload
def map_leaves[K, V1, V2, V3, V4, V5, W](
    func: Callable[[V1, V2, V3, V4, V5], W],
    nested_dict1: NestedMapping[K, V1],
    nested_dict2: NestedMapping[K, V2],
    nested_dict3: NestedMapping[K, V3],
    nested_dict4: NestedMapping[K, V4],
    nested_dict5: NestedMapping[K, V5],
    /,
) -> NestedMapping[K, W]: ...


@overload
def map_leaves[K, W](
    func: Callable[..., W],
    nested_dict1: NestedMapping[K, Any],
    nested_dict2: NestedMapping[K, Any],
    nested_dict3: NestedMapping[K, Any],
    nested_dict4: NestedMapping[K, Any],
    nested_dict5: NestedMapping[K, Any],
    /,
    *nested_dicts: NestedMapping[K, Any],
) -> NestedMapping[K, W]: ...


def map_leaves[K, V, W](
    func: Callable[..., W],
    *nested_dicts: NestedMapping[K, V],
) -> NestedMapping[K, W]:
    """
    Apply the function to every leaf (non-mapping values) of the nested dictionaries.

    If multiple nested dictionaries are passed, performs element-wise operations on their corresponding values at each key.

    Args:
        func: Function to apply on the leaves.
        *nested_dicts: Nested dictionaries on which to apply the function.

    Return:
        The result nested dictionary with mapped leaves.

    >>> map_leaves(lambda x: x * 2, {"a": 1, "b": 2, "c": 3})
    {'a': 2, 'b': 4, 'c': 6}

    >>> map_leaves(lambda x, y: x + y, {"a": 1, "b": 2}, {"a": 3, "b": 4})
    {'a': 4, 'b': 6}
    """
    dict_res: NestedMapping[K, W] = {}
    dict1 = nested_dicts[0]
    for key in dict1:
        args = (d[key] for d in nested_dicts)
        if isinstance(dict1[key], Mapping):
            dict_res[key] = map_leaves(func, *cast("Iterator[NestedMapping[K, V]]", args))
        else:
            dict_res[key] = func(*cast("Iterator[V]", args))

    return dict_res


def filter_leaves[K, V](
    func: Callable[[K, V], bool],
    nested_dict: NestedMapping[K, V],
    remove_empty: bool = True,
) -> NestedDict[K, V]:
    """
    Filter the leaves of a nested dictionary.

    Args:
        func: A function that takes a key and a value, and returns `True` if the
            key-value pair should be included in the result.
        nested_dict: The nested dictionary to filter.
        remove_empty: A flag that determines whether empty sub-dictionaries
            should be removed.

    Returns:
        The new nested dictionary with filtered leaves.

    >>> d = {"a": {"b": 1, "c": 2}, "d": {"e": 3}}
    >>> filter_leaves(lambda k, v: v > 1, d)
    {'a': {'c': 2}, 'd': {'e': 3}}

    >>> d = {"a": {"b": 1, "c": 2}, "d": {"e": 0}}
    >>> filter_leaves(lambda k, v: v > 1, d, remove_empty=False)
    {'a': {'c': 2}, 'd': {}}
    """
    dict_res: NestedDict[K, V] = {}
    for key in nested_dict:
        sub_dict = nested_dict[key]
        if isinstance(sub_dict, Mapping):
            filtered = filter_leaves(func, cast("NestedMapping[K, V]", sub_dict), remove_empty)
            if filtered or not remove_empty:
                dict_res[key] = filtered
        else:
            val = sub_dict
            if func(key, val):
                dict_res[key] = val

    return dict_res
