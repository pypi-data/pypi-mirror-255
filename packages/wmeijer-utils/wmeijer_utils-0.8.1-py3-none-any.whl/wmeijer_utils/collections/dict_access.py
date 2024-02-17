"""
Implements utility functions for interacting with dictionaries.
"""

from typing import Dict, Any, List, TypeVar, Set
from numbers import Number


K = TypeVar("K")
V = TypeVar("V")


def has_all_keys(collection: Dict[K, V], keys: List[K]) -> bool:
    """Returns true if all of the keys are present in the dictionary."""
    return all((key in collection for key in keys))


def safe_add_list_element(collection: Dict[K, List[V]], key: K, value: V):
    """
    Adds the new element to the list of elements in corresponding
    to the key if a list exists already, otherwise it creates a new list.
    :param dictionary: The dictionary to which the element is added.
    :param key: The key of the new element.
    :param value: The new element.
    """
    if key not in collection:
        collection[key] = list()
    collection[key].append(value)


def safe_add_set_element(collection: Dict[K, Set[V]], key: K, value: V):
    """Adds the new element to the set of elements in corresponding
    to the key if a set exists already, otherwise it creates a new set.
    :param collection: The dictionary to which the element is added.
    :param key: The key of the new element.
    :param value: The new element.
    """
    if key not in collection:
        collection[key] = set()
    collection[key].add(value)


def get_nested(collection: Dict[K, V], key: List[K]) -> "V | None":
    """
    Returns value corresponding to the key by recursively
    searching in the given dictionary. It returns `None`
    when the key is invalid.

    :params obj: The used dictionary.
    :params key: The query key.
    :return: The value, if such a value exists.
    """

    current = collection
    for key_element in key:
        if not key_element in current:
            return None
        current = current[key_element]
    return current


def get_nested_many(obj: dict, key: List[str]) -> "List[Any] | Any | None":
    """Same idea as ``get_nested``, however, when a variable is a list it iterates through all of them."""
    current = obj
    for key_index, key_element in enumerate(key):
        if isinstance(current, list):
            return [get_nested_many(element, key[key_index:]) for element in current]
        if not key_element in current:
            return None
        current = current[key_element]
    return current


# BUG: Query with Dict[Dict[List[List]]], which should yield a list of lists, doesn't work.
def better_get_nested_many(
    collection: Dict[Any, Any], nested_key: List[Any], raise_on_missing_key: bool = True
) -> List[Any]:
    """
    Same thing as ``get_nested_many`` but always returns a list.
    """

    current = collection
    for key_index, key_element in enumerate(nested_key):
        if isinstance(current, List):
            all_inner = [
                better_get_nested_many(element, nested_key[key_index:], raise_on_missing_key)
                for element in current
            ]
            combined = []
            for inner in all_inner:
                combined.extend(inner)
            return combined
        elif not key_element in current:
            if raise_on_missing_key:
                raise KeyError(f"Missing key {key_element} in object {current}.")
            return []
        else:
            current = current[key_element]
    if isinstance(current, List):
        return current
    else:
        return [current]


def safe_get(collection: Dict[K, V], key: K, default: "V | None" = None) -> V:
    """Returns the value of the queried key, or the default if the key is not present."""
    if key in collection:
        return collection[key]
    return default


def subtract_dict(
    collection_a: Dict[K, Number], collection_b: Dict[K, Number]
) -> Dict[K, Number]:
    """
    Subtracts the values of one dict from another: `set_a - set_b`.
    :param collection_a: The dictionary subtracted from.
    :param collection_b: The dictionary that's subtracted.
    """
    key_intersect = set(collection_a.keys()).intersection(collection_b.keys())
    if len(key_intersect) != len(collection_a) or len(key_intersect) != len(
        collection_b
    ):
        raise ValueError("Elements don't have the same keys.")
    return {key: collection_a[key] - collection_b[key] for key in key_intersect}


def invert_dict(collection: Dict[K, V]) -> Dict[V, K]:
    """
    Inverts the dictionary such that the keys become
    its values and vice versa. Assumes all values are unique.
    """
    return {value: key for key, value in collection.items()}
