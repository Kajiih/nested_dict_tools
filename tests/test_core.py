"""Tests for core module."""

import math
import time

import pytest

from nested_dict_tools import (
    KeySeparatorCollisionError,
    flatten_dict,
    get_deep,
    set_deep,
    unflatten_dict,
)


class TestFlattenDict:
    # Flatten a simple nested dictionary with default separator
    def test_flatten_simple_nested_dict(self):
        input_dict = {"a": {"b": 1, "c": 2}, "d": {"e": {"f": 3}}}
        expected_output = {"a.b": 1, "a.c": 2, "d.e.f": 3}
        assert flatten_dict(input_dict) == expected_output

    # Raise KeySeparatorCollisionError when separator is part of a key
    def test_key_separator_collision_error(self):
        input_dict = {"a.": 1}
        with pytest.raises(KeySeparatorCollisionError) as excinfo:
            flatten_dict(input_dict)
        assert "Separator `.` is a substring of key `a.`" in str(excinfo.value)

    # Flatten a nested dictionary with multiple levels of nesting
    def test_flatten_complex_nested_dict(self):
        input_dict = {
            "a": {"b": {"c": 1}, "d": 2},
            "e": {"f": {"g": {"h": 3}}, "i": 4},
            "j": 5,
        }
        expected_output = {"a.b.c": 1, "a.d": 2, "e.f.g.h": 3, "e.i": 4, "j": 5}
        assert flatten_dict(input_dict) == expected_output

    # Flatten a dictionary with custom separator
    def test_flatten_dict_with_custom_separator(self):
        input_dict = {"a": {"b": 1, "c": 2}, "d": {"e": {"f": 3}}}
        expected_output = {"a-b": 1, "a-c": 2, "d-e-f": 3}
        assert flatten_dict(input_dict, sep="-") == expected_output

        # Test for KeySeparatorCollisionError
        input_dict_with_collision = {"a-": 1}
        with pytest.raises(KeySeparatorCollisionError):
            flatten_dict(input_dict_with_collision, sep="-")

    # Handle empty dictionary input gracefully
    def test_flatten_empty_dict(self):
        input_dict = {}
        expected_output = {}
        assert flatten_dict(input_dict) == expected_output

    # Handle dictionaries with non-dictionary values at any level
    def test_flatten_dict_with_non_dict_values(self):
        input_dict = {"a": {"b": 1, "c": 2}, "d": 3, "e": {"f": {"g": 4}, "h": 5}}
        expected_output = {"a.b": 1, "a.c": 2, "d": 3, "e.f.g": 4, "e.h": 5}
        assert flatten_dict(input_dict) == expected_output

    # Handle dictionaries with mixed types of values
    def test_flatten_dict_with_mixed_value_types(self):
        input_dict = {"a": {"b": 1, "c": [2, 3]}, "d": {"e": {"f": "text"}}}
        expected_output = {"a.b": 1, "a.c": [2, 3], "d.e.f": "text"}
        assert flatten_dict(input_dict) == expected_output

    # Verify immutability of input dictionary after flattening
    def test_input_dict_immutable_after_flattening(self):
        input_dict = {"a": {"b": 1, "c": 2}, "d": {"e": {"f": 3}}}
        original_dict = input_dict.copy()
        flatten_dict(input_dict)
        assert input_dict == original_dict

    # Test performance with large nested dictionaries
    def test_flatten_large_nested_dict_performance(self):
        NB_RECURSION = 500
        # Create a large nested dictionary
        large_nested_dict = {}
        current_level = large_nested_dict
        for i in range(NB_RECURSION):
            current_level[f"key{i}"] = {}
            current_level = current_level[f"key{i}"]
        current_level["final_key"] = "value"

        # Measure the time taken to flatten the large nested dictionary
        start_time = time.time()
        flattened_dict = flatten_dict(large_nested_dict)
        end_time = time.time()

        # Check if the flattened dictionary has the expected single key
        assert list(flattened_dict.keys()) == [
            ".".join([f"key{i}" for i in range(NB_RECURSION)]) + ".final_key"
        ]
        assert (
            flattened_dict[".".join([f"key{i}" for i in range(NB_RECURSION)]) + ".final_key"]
            == "value"
        )

        # Assert that the operation completes within a reasonable time frame
        assert end_time - start_time < 1  # The operation should complete in less than 1 second

    # Test with dictionaries having None as values
    def test_flatten_dict_with_none_values(self):
        input_dict = {"a": {"b": None, "c": 2}, "d": {"e": {"f": None}}}
        expected_output = {"a.b": None, "a.c": 2, "d.e.f": None}
        assert flatten_dict(input_dict) == expected_output


class TestUnflattenDict:
    # Converts a flat dictionary with dot separators into a nested dictionary
    def test_unflatten_with_dot_separator(self):
        flat_dict = {"a.b": 1, "a.c": 2, "d.e.f": 3}
        expected = {"a": {"b": 1, "c": 2}, "d": {"e": {"f": 3}}}
        result = unflatten_dict(flat_dict)
        assert result == expected

    # Handles keys with no separator correctly
    def test_unflatten_with_no_separator(self):
        flat_dict = {"a": 5, "b.c": 10}
        expected = {"a": 5, "b": {"c": 10}}
        result = unflatten_dict(flat_dict)
        assert result == expected

    # Correctly nests keys with single-level depth
    def test_single_level_nesting(self):
        flat_dict = {"a.b": 1, "c.d": 2}
        expected = {"a": {"b": 1}, "c": {"d": 2}}
        result = unflatten_dict(flat_dict)
        assert result == expected

    # Returns an empty dictionary when given an empty input
    def test_unflatten_empty_input(self):
        flat_dict = {}
        expected = {}
        result = unflatten_dict(flat_dict)
        assert result == expected

    # Handles dictionaries with different separators like underscores
    def test_unflatten_with_underscore_separator(self):
        flat_dict = {"x_y_z": 10, "x_y_w": 20, "a": 5}
        expected = {"x": {"y": {"z": 10, "w": 20}}, "a": 5}
        result = unflatten_dict(flat_dict, sep="_")
        assert result == expected

    def test_flatten_with_special_character_separator(self):
        input_dict = {"a": {"b": {"c": 1}}}
        expected_output = {"a->b->c": 1}
        result = flatten_dict(input_dict, sep="->")
        assert result == expected_output

        # Test unflattening with the same separator
        unflattened = unflatten_dict(result, sep="->")
        assert unflattened == input_dict

    # Manages cases where the separator is not present in any key
    def test_unflatten_without_separator(self):
        flat_dict = {"a": 1, "b": 2, "c": 3}
        expected = {"a": 1, "b": 2, "c": 3}
        result = unflatten_dict(flat_dict)
        assert result == expected

    # Deals with dictionaries where keys have trailing separators
    def test_unflatten_with_trailing_separator(self):
        flat_dict = {"a.b.": 1, "a.c.": 2, "d.e.f.": 3}
        expected = {"a": {"b": {"": 1}, "c": {"": 2}}, "d": {"e": {"f": {"": 3}}}}
        result = unflatten_dict(flat_dict)
        assert result == expected

    # Handles large dictionaries efficiently
    def test_unflatten_large_dict(self):
        # Create a large flattened dictionary
        flat_dict = {f"key{i}.subkey{i}": i for i in range(1000)}
        # Expected result after unflattening
        expected = {f"key{i}": {f"subkey{i}": i} for i in range(1000)}
        result = unflatten_dict(flat_dict)
        assert result == expected

    # Processes dictionaries with mixed data types as values
    def test_unflatten_with_mixed_data_types(self):
        flat_dict = {
            "a.b": 1,
            "a.c": "string",
            "d.e.f": [1, 2, 3],
            "g.h": {"nested": "dict"},
        }
        expected = {
            "a": {"b": 1, "c": "string"},
            "d": {"e": {"f": [1, 2, 3]}},
            "g": {"h": {"nested": "dict"}},
        }
        result = unflatten_dict(flat_dict)
        assert result == expected

    # Handles dictionaries with keys that have multiple consecutive separators
    def test_unflatten_with_multiple_consecutive_separators(self):
        flat_dict = {"a..b": 1, "a..c": 2, "d...e.f": 3}
        expected = {"a": {"": {"b": 1, "c": 2}}, "d": {"": {"": {"e": {"f": 3}}}}}
        result = unflatten_dict(flat_dict, sep=".")
        assert result == expected

    def test_flatten_and_unflatten_consistency(self):
        input_dict = {"a": {"b": 1, "c": {"d": 2}}}
        flattened = flatten_dict(input_dict)
        result = unflatten_dict(flattened)
        assert result == input_dict


class TestGetDeep:
    # Retrieve value from nested dictionary using valid keys
    def test_retrieve_value_with_valid_keys(self):
        data = {"a": {"b": {"c": 42}}}
        result = get_deep(data, ["a", "b", "c"])
        assert result == 42

    # Raise KeyError when key is missing and no_default is True
    def test_key_error_with_no_default_true(self):
        data = {"a": {"b": {"c": 42}}}
        with pytest.raises(KeyError):
            get_deep(data, ["a", "x"], no_default=True)

    # Return default value when key is missing and no_default is False
    def test_return_default_when_key_missing(self):
        data = {"a": {"b": {"c": 42}}}
        result = get_deep(data, ["a", "b", "x"], default="missing")
        assert result == "missing"

    # Return nested dictionary when keys lead to a sub-dictionary
    def test_return_nested_dict_for_sub_dictionary_keys(self):
        data = {"a": {"b": {"c": 42}}}
        result = get_deep(data, ["a", "b"])
        expected = {"c": 42}
        assert result == expected

    # Handle empty keys sequence gracefully
    def test_get_deep_with_empty_keys(self):
        data = {"a": {"b": {"c": 42}}}
        result = get_deep(data, [])
        assert result == data

    # Handle non-dictionary types within nested structure
    def test_get_deep_with_non_dict_values(self):
        # Test with a nested structure containing non-dictionary values
        data = {"a": {"b": 42, "c": [1, 2, 3]}, "d": "string_value"}

        # Accessing a non-dictionary value directly
        assert get_deep(data, ["a", "b"]) == 42

        # Accessing a list within the nested structure
        assert get_deep(data, ["a", "c"]) == [1, 2, 3]

        # Accessing a string value directly
        assert get_deep(data, ["d"]) == "string_value"

        # Attempting to access a non-existent key with default value
        assert get_deep(data, ["a", "x"], default="missing") == "missing"

        # Attempting to access a non-existent key without default should raise KeyError
        with pytest.raises(KeyError):
            get_deep(data, ["a", "x"], no_default=True)

    # Verify behavior with mixed data types in nested dictionary
    def test_get_deep_with_mixed_data_types(self):
        # Test data with mixed types
        data = {
            "a": {"b": 42, "c": [1, 2, 3]},
            "d": {"e": {"f": "text", "g": None}},
            "h": math.pi,
            "i": True,
        }

        # Test retrieving an integer
        assert get_deep(data, ["a", "b"]) == 42

        # Test retrieving a list
        assert get_deep(data, ["a", "c"]) == [1, 2, 3]

        # Test retrieving a string
        assert get_deep(data, ["d", "e", "f"]) == "text"

        # Test retrieving a None value
        assert get_deep(data, ["d", "e", "g"]) is None

        # Test retrieving a float
        assert get_deep(data, ["h"]) == math.pi

        # Test retrieving a boolean
        assert get_deep(data, ["i"]) is True

        # Test with default value for missing key
        assert get_deep(data, ["a", "x"], default="missing") == "missing"

        # Test KeyError when no_default is True and key is missing
        with pytest.raises(KeyError):
            get_deep(data, ["a", "x"], no_default=True)

    # Ensure compatibility with different iterable types for keys
    def test_get_deep_with_various_iterable_keys(self):
        data = {"a": {"b": {"c": 42}, "d": 100}, "e": 200}

        # Test with list of keys
        assert get_deep(data, ["a", "b", "c"]) == 42

        # Test with tuple of keys
        assert get_deep(data, ("a", "d")) == 100

        # Test with generator of keys
        key_gen = (key for key in ["e"])
        assert get_deep(data, key_gen) == 200

        # Test with default value when key is missing
        assert get_deep(data, ["a", "x"], default="missing") == "missing"

        # Test with no_default=True raising KeyError
        with pytest.raises(KeyError):
            get_deep(data, ["a", "x"], no_default=True)


class TestSetDeep:
    # Sets a value in a nested dictionary at the specified keys
    def test_set_value_at_specified_keys(self):
        data = {"a": {"b": {"c": 42}}}
        set_deep(data, ["a", "b", "d"], 100)
        assert data == {"a": {"b": {"c": 42, "d": 100}}}

    # Creates missing sub-dictionaries when setting a value
    def test_create_missing_sub_dictionaries(self):
        # Test case 1: Set a new value in an existing nested dictionary
        data = {"a": {"b": {"c": 42}}}
        set_deep(data, ["a", "b", "d"], 100)
        assert data == {"a": {"b": {"c": 42, "d": 100}}}

        # Test case 2: Set a new value in an empty dictionary
        data = {}
        set_deep(data, ["x", "y", "z"], "new")
        assert data == {"x": {"y": {"z": "new"}}}

    # Works with empty dictionaries to create new nested structures
    def test_set_deep_with_empty_dict(self):
        data = {}
        set_deep(data, ["x", "y", "z"], "new")
        assert data == {"x": {"y": {"z": "new"}}}

    # Handles sequences of keys correctly to navigate nested dictionaries
    def test_set_value_in_nested_dict(self):
        # Test case 2: Overwrite an existing value in a nested dictionary
        data = {"a": {"b": {"c": 42}}}
        set_deep(data, ["a", "b", "c"], 100)
        assert data == {"a": {"b": {"c": 100}}}

        # Test case 3: Set a value with a single key
        data = {}
        set_deep(data, ["single_key"], "value")
        assert data == {"single_key": "value"}

    # Manages existing keys that do not map to dictionaries
    def test_set_deep_with_non_dict_key(self):
        data = {"a": {"b": 42}}
        with pytest.raises(TypeError):
            set_deep(data, ["a", "b", "c"], 100)

    # Supports various data types for values being set
    def test_set_deep_with_various_data_types(self):
        # Test setting a list value
        data = {"a": {}}
        set_deep(data, ["a", "list"], [1, 2, 3])
        assert data == {"a": {"list": [1, 2, 3]}}

        # Test setting a dictionary value
        data = {}
        set_deep(data, ["nested", "dict"], {"key": "value"})
        assert data == {"nested": {"dict": {"key": "value"}}}

        # Test setting a None value
        data = {"a": {"b": {}}}
        set_deep(data, ["a", "b", "none"], None)
        assert data == {"a": {"b": {"none": None}}}

    # Handles large dictionaries efficiently
    def test_set_deep_with_large_dictionary(self):
        # Create a large nested dictionary
        large_dict = {}
        keys = [f"key_{i}" for i in range(1000)]
        value = "final_value"

        # Set a deep value in the large dictionary
        set_deep(large_dict, keys, value)

        # Verify that the value is set correctly
        sub_dict = large_dict
        for key in keys[:-1]:
            sub_dict = sub_dict[key]
        assert sub_dict[keys[-1]] == value
