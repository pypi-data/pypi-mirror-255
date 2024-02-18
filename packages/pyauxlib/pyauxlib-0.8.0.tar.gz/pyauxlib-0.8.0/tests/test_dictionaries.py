"""Tests for `pyauxlib.utils.dictionaries`."""
from typing import Any

from pyauxlib.utils.dictionaries import is_empty_or_none, remove_keys


def test_remove_keys() -> None:
    """Test the `remove_keys` function.

    This function tests the following scenarios:
        - Removing existing keys from a dictionary.
        - Attempting to remove a key that does not exist in the dictionary.
    """
    dictionary = {"a": 1, "b": 2, "c": 3}
    remove = ["b", "c"]
    expected = {"a": 1}
    assert remove_keys(dictionary, remove) == expected

    dictionary = {"a": 1, "b": 2, "c": 3}
    remove = ["d"]
    expected = {"a": 1, "b": 2, "c": 3}
    assert remove_keys(dictionary, remove) == expected


def test_is_empty_or_none() -> None:
    """Test the `is_empty_or_none` function.

    This function tests the following scenarios:
        - Checking an empty dictionary.
        - Checking a dictionary where all values are None.
        - Checking a dictionary where all values are None or empty dictionaries.
        - Checking a dictionary where one value is not None.
    """
    dictionary: dict[str, Any] = {}
    assert is_empty_or_none(dictionary) is True

    dictionary = {"a": None, "b": {"c": None}}
    assert is_empty_or_none(dictionary) is True

    dictionary = {"a": None, "b": {}}
    assert is_empty_or_none(dictionary) is True

    dictionary = {"a": None, "b": {"c": 0}}
    assert is_empty_or_none(dictionary) is False
