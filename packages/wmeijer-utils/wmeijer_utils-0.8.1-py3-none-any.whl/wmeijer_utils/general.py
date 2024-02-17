from datetime import datetime
import random


class Counter:
    """Simple tool for picking the next number in line."""

    def __init__(self, start_value: int = 42, increment: int = 1) -> None:
        self.__current_value = start_value
        self.__increment = increment

    def get_next(self):
        self.__current_value += self.__increment
        return self.__current_value


def lies_between(x, start, end) -> bool:
    return x >= start and x <= end


def lies_outside_timewindow(
    timestamp: str, start: datetime, end: datetime, time_format: str
) -> bool:
    """Returns true if the provided timestamp lies outside the provided window."""
    timestamp = datetime.strptime(timestamp, time_format)
    return timestamp < start and timestamp > end


def shuffled_range(start=0, end=100, step=1):
    lst = list(range(start, end, step))
    random.shuffle(lst)
    return lst
