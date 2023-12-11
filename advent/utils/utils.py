from collections.abc import Iterator
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

    def to_point(self) -> "Direction":
        if self == Direction.East:
            return Point(1, 0)
        elif self == Direction.North:
            return Point(0, 1)
        elif self == Direction.West:
            return Point(-1, 0)
        elif self == Direction.South:
            return Point(0, -1)

    def __str__(self) -> str:
        if self == Direction.East:
            return "East"
        elif self == Direction.North:
            return "North"
        elif self == Direction.West:
            return "West"
        elif self == Direction.South:
            return "South"

    @classmethod
    def cardinal_dirs(cls) -> Iterator["Direction"]:
        yield Direction.East
        yield Direction.North
        yield Direction.West
        yield Direction.South


class Point:
    __slots__ = ("x", "y")
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Point(x={self.x}, y={self.y})"

    def __str__(self) -> str:
        return f"{self.x}, {self.y}"

    def __getitem__(self, key: int) -> int:
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise Exception(f"cannot get subscript [{key}] for Point object")

    def __setitem__(self, key: int, value: int) -> None:
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise Exception(f"cannot set subscript [{key}] for Point object")

    def __eq__(self, other: "Point") -> bool:
        return self.x == other.x and self.y == other.y

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other: int) -> "Point":
        return Point(self.x * other, self.y * other)

    def __truediv__(self, other: int) -> "Point":
        return Point(self.x / other, self.y / other)

    def __neg__(self) -> "Point":
        return Point(-self.x, -self.y)

    def __abs__(self) -> "Point":
        return Point(abs(self.x), abs(self.y))

    def __hash__(self) -> int:
        return hash((self.x, self.y))


class Grid:
    __slots__ = ("cells", "x_count", "y_count")
    cells: list[T]
    x_count: int
    y_count: int

    def __init__(
        self, x_count: int, y_count: int, initial: Union[T, list[list[T]]]
    ) -> None:
        if x_count < 1:
            raise Exception("Grid column count `x_count` must be larger than zero")
        if y_count < 1:
            raise Exception("Grid row count `y_count` must be larger than zero")

        self.x_count = x_count
        self.y_count = y_count

        if isinstance(initial, list):
            if len(initial) != self.y_count:
                raise Exception("Grid initial rows list len must equal `y_count`")

            # Verify all rows are lists of cells and of uniform size.
            for row in initial:
                if not isinstance(row, list):
                    raise Exception(
                        "Grid initial rows must all be lists of column value"
                    )
                if len(row) != self.x_count:
                    raise Exception("Grid initial rows be consistent length")

            # Copy rows.
            self.cells = [c for row in initial for c in row]
        else:
            self.cells = [initial for _ in range(x_count * y_count)]

    def check_in_bounds(self, pt: Point) -> bool:
        return pt.x >= 0 and pt.y >= 0 and pt.x < self.x_count and pt.y < self.y_count

    def validate_in_bounds(self, pt: Point) -> None:
        if not self.check_in_bounds(pt):
            raise Exception(
                f"Point out of bounds; x: 0<={pt.x}<{self.x_count}, y: 0<={pt.y}<{self.y_count}"
            )

    def __getitem__(self, pt: Point) -> T:
        self.validate_in_bounds(pt)
        return self.cells[pt.y * self.x_count + pt.x]

    def __setitem__(self, pt: Point, v: T) -> None:
        self.validate_in_bounds(pt)
        self.cells[pt.y * self.x_count + pt.x] = v

    def __delitem__(Self, pt: Point) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        return len(self.cells)

    def __iter__(self) -> Iterable[T]:
        return iter(self.cells)

    def __str__(self) -> str:
        return "\n".join(
            "".join(str(self.cells[y * self.x_count + x]) for x in range(self.x_count))
            for y in range(self.y_count)
        )


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
