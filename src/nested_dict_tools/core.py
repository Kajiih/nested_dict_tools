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
    - Get and Set deeply nested values.

flatten adapted from https://gist.github.com/crscardellino/82507c13ba2b832b860ba0960759b925

This code is licensed under the terms of the MIT license.
"""

from collections.abc import Iterable, Iterator, Mapping, MutableMapping, Sequence
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
    nested_dict_tools.core.KeySeparatorCollisionError: Separator `.` is a substring of key `a.`. Change separator.
    """

    def flatten_dict_gen(
        d: NestedMapping[K, V], parent_key: str | None, sep: str
    ) -> Iterator[tuple[str, V]]:
        for k, v in d.items():
            if sep in k:
                raise KeySeparatorCollisionError(k, sep)
            concat_key = parent_key + sep + k if parent_key is not None else k
            if isinstance(v, Mapping):
                yield from flatten_dict_gen(cast(NestedMapping[K, V], v), concat_key, sep)
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
            sub_dict = cast(NestedMutableMapping[K, V], sub_dict[key])
        except KeyError:
            sub_dict[key] = sub_dict = {}

    sub_dict[keys[-1]] = value
