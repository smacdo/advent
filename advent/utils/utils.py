from collections.abc import Iterator
from enum import IntEnum
from typing import (
    Callable,
    Generic,
    Iterable,
    Tuple,
    TypeVar,
    Union,
)

import logging

T = TypeVar("T")


class Point:
    """Represents a 2d cartesian x, y point value."""

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        else:
            return self.x == other.x and self.y == other.y

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other: int) -> "Point":
        return Point(self.x * other, self.y * other)

    def __truediv__(self, other: int) -> "Point":
        return Point(self.x // other, self.y // other)

    def __neg__(self) -> "Point":
        return Point(-self.x, -self.y)

    def __abs__(self) -> "Point":
        return Point(abs(self.x), abs(self.y))

    def __hash__(self) -> int:
        return hash((self.x, self.y))


class Direction(IntEnum):
    """Represents a north/south/east/west direction heading."""

    East = 0
    North = 1
    West = 2
    South = 3

    def to_point(self) -> Point:
        """Convert the direction to a unit point with the same heading."""
        if self == Direction.East:
            return Point(1, 0)
        elif self == Direction.North:
            return Point(0, -1)
        elif self == Direction.West:
            return Point(-1, 0)
        elif self == Direction.South:
            return Point(0, 1)

    def reverse(self) -> "Direction":
        """Get the direction in the opposite direction."""
        if self == Direction.East:
            return Direction.West
        elif self == Direction.North:
            return Direction.South
        elif self == Direction.West:
            return Direction.East
        elif self == Direction.South:
            return Direction.North

    def __str__(self) -> str:
        """Convert the direction to a human readable string"""
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
        """Generate all four cardination directions."""
        yield Direction.East
        yield Direction.North
        yield Direction.West
        yield Direction.South


class Grid(Generic[T]):
    """Holds a collection of values in a 2d grid."""

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
        """Test if a point is a valid cell position."""
        return pt.x >= 0 and pt.y >= 0 and pt.x < self.x_count and pt.y < self.y_count

    def validate_in_bounds(self, pt: Point) -> None:
        """Throw an exception if the point is not a valid cell position."""
        if not self.check_in_bounds(pt):
            raise Exception(
                f"Point out of bounds; x: 0<={pt.x}<{self.x_count}, y: 0<={pt.y}<{self.y_count}"
            )

    def yield_row(self, y_row: int) -> Iterable[Tuple[Point, T]]:
        if y_row < 0 or y_row >= self.y_count:
            raise Exception(f"yield_row {y_row} is out of bounds")

        x = 0

        for i in range(y_row * self.x_count, (y_row + 1) * self.x_count):
            yield (Point(x, y_row), self.cells[i])
            x += 1

    def row(self, y_row: int) -> list[T]:
        if y_row < 0 or y_row >= self.y_count:
            raise Exception(f"yield_row {y_row} is out of bounds")

        return [
            self.cells[i]
            for i in range(y_row * self.x_count, (y_row + 1) * self.x_count)
        ]

    def row_count(self):
        return self.y_count

    def col_count(self):
        return self.x_count

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

    def __iter__(self) -> Iterator[T]:
        return iter(self.cells)

    def __str__(self) -> str:
        return "\n".join(
            "".join(str(self.cells[y * self.x_count + x]) for x in range(self.x_count))
            for y in range(self.y_count)
        )

    def rows(self) -> "GridMultiRowIterator[T]":
        """Returns an interator that yields each row in the grid."""
        return GridMultiRowIterator(self, 0, self.row_count())


class GridRowIterator(Generic[T]):
    __slots__ = ("grid", "row", "x", "end_x")
    grid: Grid[T]
    row: int
    x: int
    end_x: int

    def __init__(self, grid: Grid[T], row: int, x: int, end_x: int):
        # TODO: Bounds check.
        self.grid = grid
        self.row = row
        self.x = x
        self.end_x = end_x

    def __next__(self) -> T:
        if self.x < self.grid.col_count():
            self.x += 1
            return self.grid[Point(self.x - 1, self.row)]
        else:
            raise StopIteration

    def __iter__(self):
        return self


class GridMultiRowIterator(Generic[T]):
    __slots__ = ("grid", "row", "end_row")
    grid: Grid[T]
    row: int
    end_row: int

    def __init__(self, grid: Grid[T], start_row: int, end_row: int):
        if start_row < 0 or start_row >= end_row:
            raise Exception(f"start_row={start_row} out of range")

        if end_row > grid.row_count():
            raise Exception(f"end_row={end_row} larger than row count")

        self.grid = grid
        self.row = start_row
        self.end_row = end_row

    def __next__(self) -> GridRowIterator[T]:
        if self.row < self.grid.row_count():
            self.row += 1
            return GridRowIterator(self.grid, self.row - 1, 0, self.grid.col_count())
        else:
            raise StopIteration

    def __iter__(self):
        return self


def new_grid_from_input_lines(lines: Iterable[Iterable[str]]) -> "Grid[str]":
    chars = [[c for c in line] for line in lines]
    return Grid(len(chars[0]), len(chars), chars)


def count_if(itr: Union[list[T], Iterable[T]], pred: Callable[[T], bool]) -> int:
    """Count the number of times `pred` returns true for each item in the collection."""
    if isinstance(itr, list):
        itr = iter(itr)

    count = 0

    for x in itr:
        if pred(x):
            count += 1

    return count


def first_and_last(itr: Union[Iterable[T], Iterator[T]]) -> Tuple[T, T]:
    """Gets the first and last element from an iterable sequence. Note that for
    single element sequences the first and last element are the same."""
    if isinstance(itr, Iterable):
        itr = iter(itr)

    first = last = next(itr)
    for last in itr:
        pass

    assert first is not None
    assert last is not None

    return (first, last)


def unzip(itr: Iterable[Tuple[T, T]]) -> Tuple[list[T], list[T]]:
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
