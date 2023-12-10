from enum import IntEnum
from typing import (
    Iterable,
    Tuple,
    TypeVar,
    Union,
)

import logging

T = TypeVar("T")


class Direction(IntEnum):
    East = 0
    North = 1
    West = 2
    South = 3


class Point:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"

    def __str__(self):
        return f"{self.x}, {self.y}"

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise Exception(f"cannot get subscript [{key}] for Point object")

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise Exception(f"cannot set subscript [{key}] for Point object")

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Point(self.x * other, self.y * other)

    def __truediv__(self, other):
        return Point(self.x / other, self.y / other)

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __abs__(self):
        return Point(abs(self.x), abs(self.y))

    def __hash__(self):
        return hash((self.x, self.y))


def first_and_last(itr: Union[list[int], Iterable[T]]) -> Tuple[T, T]:
    """Gets the first and last element from an iterable sequence. Note that for
    single element sequences the first and last element are the same."""
    if isinstance(itr, list):
        itr = iter(itr)

    first = last = next(itr)
    for last in itr:
        pass

    assert first is not None
    assert last is not None

    return (first, last)


def unzip(itr: Iterable[Tuple[T, T]]) -> (list[T], list[T]):
    a = []
    b = []

    for x, y in itr:
        a.append(x)
        b.append(y)

    return (a, b)


def load_input(day: Union[int, str], year: Union[int, str]) -> Iterable[Iterable[str]]:
    # Load the actual input if no input was given.
    with open(f"inputs/{year}/day{day}.txt", "r", encoding="utf-8") as file:
        input: Iterable[Iterable[str]] = [line.rstrip() for line in file]
        return input


# TODO: Move to advent.logging.init_logging()
def init_logging(default_level=logging.INFO):
    add_logging_level("TRACE", logging.DEBUG - 5)
    logging.basicConfig(level=default_level)


# TODO: Move to advent.logging._add_logging_level()
def add_logging_level(level_name, level_num):
    # Simplified version of https://stackoverflow.com/a/35804945
    method_name = level_name.lower()

    # Generate a function that implements logging at the requested logging level
    # by checking if it is enabled first.
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    def log_to_root(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    # Register the new log level with the Python logging system.
    logging.addLevelName(level_num, level_name)

    setattr(logging, level_name, level_num)  # Add `logging.$level_name = $level_num`
    setattr(logging.getLoggerClass(), method_name, logForLevel)
    setattr(logging, method_name, log_to_root)
