from advent.spatial import Grid
from collections.abc import Iterator
from typing import (
    Callable,
    Generator,
    Iterable,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)
import logging


T = TypeVar("T")


def new_grid_from_input_lines(lines: Iterable[Iterable[str]]) -> Grid[str]:
    chars = [[c for c in line] for line in lines]
    return Grid(len(chars[0]), len(chars), chars)


def count_if(itr: Union[list[T], Iterable[T]], pred: Callable[[T], bool]) -> int:
    """Count the number of times `pred` returns true for each item in the collection."""
    if isinstance(itr, list):
        itr = iter(itr)
    elif not isinstance(itr, Iterator):
        raise TypeError("argument `itr` must be of type `Iterable` or `Iterable`")

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
    elif not isinstance(itr, Iterator):
        raise TypeError("argument `itr` must be of type `Iterable` or `Iterable`")

    first = last = next(itr)
    for last in itr:
        pass

    assert first is not None
    assert last is not None

    return (first, last)


def unzip(itr: Iterable[Tuple[T, T]]) -> Tuple[list[T], list[T]]:
    if not isinstance(itr, Iterable):
        raise TypeError("argument `itr` must be of type `Iterable`")

    a = []
    b = []

    for x, y in itr:
        a.append(x)
        b.append(y)

    return (a, b)


def all_pairs(items: list[T]) -> Iterator[Tuple[T, T]]:
    """Generate all pair combinations from `items` without counting each pair more
    than once (eg `(2 1)` would be a copy of `(1 2)`)."""
    if not isinstance(items, list):
        raise TypeError("argument `items` must be type `list`")

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            yield (items[i], items[j])


def combinations(k: int, items: list[T]) -> Generator[list[T], None, None]:
    """Generates all possible combinations of `k` size from `items` without
    repeats."""
    if not isinstance(k, int):
        raise TypeError("argument `k` must be type `int`")
    if not isinstance(items, list):
        raise TypeError("argument `items` must be type `list`")
    if k < 1:
        raise ValueError("`k` must be larger than zero")
    if k > len(items):
        raise ValueError("`k` must be smaller than the length of the items list")

    def step(
        depth: int, k: int, start_i: int, items: list[T], scratch: list[Optional[T]]
    ) -> Generator[list[T], None, None]:
        for i in range(start_i, len(items)):
            scratch[depth] = items[i]

            if depth + 1 == k:
                x = scratch.copy()

                if x is None:
                    raise Exception(
                        "None is not supported in `combinations` util function"
                    )
                else:
                    yield cast(list[T], x)
            else:
                yield from step(depth + 1, k, i + 1, items, scratch)

    scratch: list[Optional[T]] = [None for _ in range(0, k)]
    yield from step(0, k, 0, items, scratch)


# TODO: Delete below, not needed anymore.
def load_input(day: int, year: int) -> Iterable[Iterable[str]]:
    """Loads input for a solver from a given day and year, and returns it as a
    list of strings."""
    if not isinstance(day, int):
        raise TypeError("argument `day` must be type `int`")
    if not isinstance(year, int):
        raise TypeError("argument `year` must be type `int`")

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
