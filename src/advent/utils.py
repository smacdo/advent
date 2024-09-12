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
