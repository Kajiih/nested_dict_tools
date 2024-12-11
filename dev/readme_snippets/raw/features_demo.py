from nested_dict_tools import (
    filter_leaves,
    flatten_dict,
    get_deep,
    is_in_leaves,
    iter_leaf_containers,
    iter_leaves,
    map_leaves,
    set_deep,
    unflatten_dict,
)

nested = {"a": {"b": {"c": 42}}}

# Get a deeply nested value
value = get_deep(nested, ["a", "b"])
print(value)

# Set a deeply nested value
set_deep(nested, ["a", "z"], "new_value")
print(nested)

# Flatten the nested dictionary
flat = flatten_dict(nested, sep=".")
print(flat)

# Unflatten the flattened dictionary
unflattened = unflatten_dict(flat, sep=".")
print(unflattened == nested)


# Iterate over leaves
leaves = list(iter_leaves(nested))
print(leaves)

# Iterate over leaf conainers and keys
leaf_refs = list(iter_leaf_containers(nested))
print(leaf_refs)

# and mutate leaves in place
d, key = leaf_refs[0]
d[key] = 3
print(nested)


# Check if a values is the leaves
print(is_in_leaves("foo", nested))

# Filter leaves
nested = filter_leaves(
    nested,
    lambda k, v: isinstance(v, int),
)
print(nested)

# Map on leaves
mapped = map_leaves(lambda x: x + 1, nested)
print(mapped)

# Map on leaves with several dictionaries
mapped = map_leaves(lambda x, y: x + y + 1, nested, nested)
print(mapped)


# # Recursive types:
type NestedDict[K, V] = dict[K, NestedDictNode[K, V]]
type NestedDictNode[K, V] = V | NestedDict[K, V]
# Similar types for Mapping and MutableMapping
