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

# Filter leaves
nested = filter_leaves(lambda k, v: isinstance(v, int), nested)
print(nested)

# Map on leaves
mapped = map_leaves(lambda x: x + 1, nested)
print(mapped)

# Map on leaves with several dictionaries
mapped = map_leaves(lambda x, y: x + y + 1, nested, nested)
print(mapped)


# Recursive types:
type NestedDict[K, V] = dict[K, NestedDictNode[K, V]]
type NestedDictNode[K, V] = V | NestedDict[K, V]
# Similar types for Mapping and MutableMapping

print("This is a new lines!")  # hihi
