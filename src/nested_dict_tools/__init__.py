"""Top-level package for Nested Dict Tools."""

from nested_dict_tools._core import (
    KeySeparatorCollisionError,
    NestedDict,
    NestedDictNode,
    NestedMapping,
    NestedMappingNode,
    NestedMutableMapping,
    NestedMutableMappingNode,
    filter_leaves,
    flatten_dict,
    get_deep,
    map_leaves,
    set_deep,
    unflatten_dict,
)

__all__ = [
    "KeySeparatorCollisionError",
    "NestedDict",
    "NestedDictNode",
    "NestedMapping",
    "NestedMappingNode",
    "NestedMutableMapping",
    "NestedMutableMappingNode",
    "filter_leaves",
    "flatten_dict",
    "get_deep",
    "map_leaves",
    "set_deep",
    "unflatten_dict",
]
