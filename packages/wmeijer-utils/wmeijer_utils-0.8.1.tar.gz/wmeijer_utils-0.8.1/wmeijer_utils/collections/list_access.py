from typing import Iterator, Any, Callable, List, Sequence


def resolve_callables_in_list(
    coll: "Iterator[Any | Callable]", *args, **kwargs
) -> Iterator[Any]:
    for entry in coll:
        if isinstance(entry, Callable):
            entry = entry(*args, **kwargs)
        yield entry


def safe_index(list: List, entry: object) -> int:
    try:
        return list.index(entry)
    except ValueError:
        return -1


def flatten(iterator: "Iterator[Iterator | Any]") -> Iterator[Any]:
    """
    Flattens Iterator with nested Iterators.
    """

    for element in iterator:
        if (
            isinstance(element, Iterator) or isinstance(element, Sequence)
        ) and not isinstance(element, str):
            for inner_element in flatten(element):
                yield inner_element
        else:
            yield element
