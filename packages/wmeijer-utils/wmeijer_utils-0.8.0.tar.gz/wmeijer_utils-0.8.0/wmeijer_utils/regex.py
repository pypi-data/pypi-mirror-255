from typing import Iterator

import regex as re


def get_matching(collection: Iterator[str], pattern: str) -> Iterator[str]:
    """Returns all entries that match the expression."""

    def __is_pattern_match(element: str) -> bool:
        return re.match(pattern, element)

    return filter(__is_pattern_match, collection)


def get_non_matching(collection: Iterator[str], pattern: str) -> Iterator[str]:
    """Returns all entries that do NOT match the expression."""

    def __is_not_pattern_match(element: str) -> bool:
        return not re.match(pattern, element)

    return filter(__is_not_pattern_match, collection)
