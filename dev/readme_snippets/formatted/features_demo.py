from nested_dict_tools import (
    filter_leaves,
    flatten_dict,
    get_deep,
    map_leaves,
    set_deep,
    unflatten_dict,
)

nested = {"a": {"b": {"c": 42}}}

# Get a deeply nested value
value = get_deep(nested, ["a", "b"])
print(value)  # Output: {'c': 42}

# Set a deeply nested value
set_deep(nested, ["a", "z"], "new_value")
print(nested)  # Output: {'a': {'b': {'c': 42}, 'z': 'new_value'}}

# Flatten the nested dictionary
flat = flatten_dict(nested, sep=".")
print(flat)  # Output: {'a.b.c': 42, 'a.z': 'new_value'}

# Unflatten the flattened dictionary
unflattened = unflatten_dict(flat, sep=".")
print(unflattened == nested)  # Output: True

# Filter leaves
nested = filter_leaves(lambda k, v: isinstance(v, int), nested)
print(nested)  # Output: {'a': {'b': {'c': 42}}}

# Map on leaves
mapped = map_leaves(lambda x: x + 1, nested)
print(mapped)  # Output: {'a': {'b': {'c': 43}}}

# Map on leaves with several dictionaries
mapped = map_leaves(lambda x, y: x + y + 1, nested, nested)
print(mapped)  # Output: {'a': {'b': {'c': 85}}}


# Recursive types:
type NestedDict[K, V] = dict[K, NestedDictNode[K, V]]
type NestedDictNode[K, V] = V | NestedDict[K, V]
# Similar types for Mapping and MutableMapping