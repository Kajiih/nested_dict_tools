[![Build][github-ci-image]][github-ci-link]
[![Coverage Status][codecov-image]][codecov-link]
[![PyPI Version][pypi-image]][pypi-link]
[![PyPI - Python Version][python-image]][pypi-link]
![License][license-image-mit]

# 🪆 Nested Dict Tools

**Nested Dict Tools** is a Python package that provides utilities for working with nested dictionaries. It includes:

- Recursive types for describing nested mappings and dictionaries.
- Fully typed functions to:
  - Flatten and unflatten nested dictionaries.
  - Get and set deeply nested values.

```python
from nested_dict_tools import flatten_dict, unflatten_dict, get_deep, set_deep

nested = {'a': {'b': {'c': 42}}}

# Get a deeply nested value
value = get_deep(nested, ['a', 'b'])
print(value)  # Output: {'c': 42}

# Set a deeply nested value
set_deep(nested, ['a', 'z'], 'new_value')
print(nested)  # Output: {'a': {'b': {'c': 42}, 'z': 'new_value'}}

# Flatten the nested dictionary
flat = flatten_dict(nested, sep='.')
print(flat)  # Output: {'a.b.c': 42, 'a.z': 'new_value'}

# Unflatten the flattened dictionary
unflattened = unflatten_dict(flat, sep='.')
print(unflattened == nested)  # Output: True

# Recursive types:
type NestedDict[K, V] = dict[K, NestedDictNode[K, V]]
type NestedDictNode[K, V] = V | NestedDict[K, V]
# Similar types for Mapping and MutableMapping
```

## ⬇️ Installation

You can install **Nested Dict Tools** via pip:

```bash
pip install nested-dict-tools
```

## 🧾 License

[MIT](LICENSE)

<!-- Links -->
[github-ci-image]: https://github.com/kajiih/nested_dict_tools/actions/workflows/build.yml/badge.svg?branch=main
[github-ci-link]: https://github.com/kajiih/nested_dict_tools/actions?query=workflow%3Abuild+branch%3Amain

[codecov-image]: https://img.shields.io/codecov/c/github/kajiih/nested_dict_tools/main.svg?logo=codecov&logoColor=aaaaaa&labelColor=333333
[codecov-link]: https://codecov.io/github/kajiih/nested_dict_tools

[pypi-image]: https://img.shields.io/pypi/v/nested-dict-tools.svg?logo=pypi&logoColor=aaaaaa&labelColor=333333
[pypi-link]: https://pypi.python.org/pypi/nested-dict-tools

[python-image]: https://img.shields.io/pypi/pyversions/nested-dict-tools?logo=python&logoColor=aaaaaa&labelColor=333333
[license-image-mit]: https://img.shields.io/badge/license-MIT-blue.svg?labelColor=333333
