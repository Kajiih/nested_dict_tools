"""Top-level package for Nested Dict Tools."""

from .core import (
    KeySeparatorCollisionError,
    NestedDict,
    NestedDictNode,
    NestedMapping,
    NestedMappingNode,
    NestedMutableMapping,
    NestedMutableMappingNode,
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
    "flatten_dict",
    "get_deep",
    "map_leaves",
    "set_deep",
    "unflatten_dict",
]
