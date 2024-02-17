import math
from typing import Iterator, List, Callable, TypeVar, Tuple, Dict
from numbers import Number

import numpy

T = TypeVar("T")


def ordered_chain(
    iterables: List[Iterator[T]], key: Callable[[T, T], Number]
) -> Iterator[Tuple[int, T]]:
    """
    Iterates through multiple generators in a chained fashion,
    iterating through them in an ordered fashion. Assumes the
    individual generators are sorted already.

    :param list[Generator[T]] iterables: The lists that are being chained.
    :param Callable[[T], Number] key: Method that is used for ordering
    iterable elements.
    """

    current_elements = [next(iterables[idx]) for idx in range(len(iterables))]
    stop_iterations = 0

    def __key_wrapper(entry):
        return math.inf if entry is None else key(entry)

    while stop_iterations != len(iterables):
        current_idx = numpy.argmin([__key_wrapper(ele) for ele in current_elements])
        yield current_idx, current_elements[current_idx]
        try:
            current_elements[current_idx] = next(iterables[current_idx])
        except StopIteration:
            stop_iterations += 1
            current_elements[current_idx] = None


def tuple_chain(
    iterator: Iterator[T], yield_first: bool = False, yield_last: bool = False
) -> "Iterator[Tuple[T | None, T | None]]":
    """Returns tuples of entries. Given [a, b, c, d], it outputs [(a,b), (b,c), (c,d)]"""
    if not isinstance(iterator, Iterator):
        iterator = iter(iterator)

    previous = None
    current = next(iterator)

    if yield_first:
        yield previous, current

    for entry in iterator:
        previous = current
        current = entry
        yield previous, current

    if yield_last:
        yield current, None


def chain_with_intermediary_callback(
    generator: Iterator[T], callback: Callable[[T], None]
) -> Iterator[T]:
    """Calls the specified function before yielding the entry like normal."""
    for entry in generator:
        callback(entry)
        yield entry


def stepped_enumerate(
    collection: Iterator[T], start: Number = 0, step: Number = 1
) -> Iterator[Tuple[Number, T]]:
    current = start
    for entry in collection:
        yield (current, entry)
        current += step


def merge_iterate_through_lists(
    collections: List[List[T]], sorting_key: Callable[[T], Number]
) -> Tuple[Number, Iterator[Dict[Number, T]]]:
    """
    Applies the same method used in MergeSort to iterate through various lists.
    If multiple entries have the same key, they are ALL yielded.
    Assumes that an individual collection has no duplicate sorting keys.
    """
    element_pointers = [0] * len(collections)
    counter = 0
    counter_max = sum([len(coll) for coll in collections])
    while counter < counter_max:
        # Finds the current elements with the lowest sorting key
        lowest = math.inf
        collection = {}
        for collection_index, elements in enumerate(collections):
            pointer = element_pointers[collection_index]
            if pointer >= len(elements):
                continue
            current: T = elements[pointer]
            element_value = sorting_key(current)
            # Creates new collection if a lower value is found.
            if element_value < lowest:
                lowest = element_value
                collection = {collection_index: current}
            # Appends collection if value is the same.
            elif element_value == lowest:
                collection[collection_index] = current
        # Updates guard and pointers.
        counter += len(collection)
        for collection_index in collection.keys():
            element_pointers[collection_index] += 1
        yield lowest, collection
