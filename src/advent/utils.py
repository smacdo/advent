from dataclasses import dataclass
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
import re


T = TypeVar("T")


def not_none(value: T | None) -> T:
    # TODO: Write tests.
    # TODO: Unique exception
    if value is None:
        raise Exception("value cannot be null")
    else:
        return value


def expect_re_match(pattern: re.Pattern | str, text: str) -> re.Match:
    """
    Matches `text` against the regex `pattern`, and returns the match results.
    This function will throw an exception if the pattern fails to match.

    See: https://docs.python.org/3/library/re.html#re.Pattern.match
    """
    if type(pattern) is re.Pattern:
        m = pattern.match(text)
    else:
        pattern = re.compile(pattern)
        m = pattern.match(text)

    if m is None:
        raise Exception(f"expected regex pattern `{pattern}` to match `text`")

    return m


def split(
    text: str, sep: str, ignore_empty: bool = True, strip_whitespace=True
) -> list[str]:
    """
    Splits `text` into multiple parts using `sep` as the separator.

    ignore_empty:      When true, only parts with len > 0 are returned.
    strip_whitespace:  When true, parts have leading and trailing whitespace removed.

    Example:

    """

    def is_empty(s: str):
        if strip_whitespace:
            return len(s.strip()) == 0
        else:
            return len(s) == 0

    if ignore_empty:
        return [x for x in text.split(sep) if not is_empty(x)]
    else:
        return text.split(sep)


def find_ints(text: str) -> Iterable[int]:
    """Returns all the integers found in the text string and ignores any non-number characters."""
    return map(int, re.findall(r"-?[0-9]+", text))


def new_grid_from_input_lines(lines: Iterable[Iterable[str]]) -> Grid[str]:
    chars = [[c for c in line] for line in lines]
    return Grid(len(chars[0]), len(chars), chars)


def count_if(itr: Union[list[T], Iterable[T]], pred: Callable[[T], bool]) -> int:
    """
    Count the number of times `pred` returns true for each item in the collection.

    itr:  A list or other iterable object to count.
    pred: A callable object that takes each item from `itr` as input, and returns
          `True` if the item should be counted or `False` otherwise.

    Example:
    ```
        count_if([1, 2, 3, 4], lambda x: x % 2 == 0) # returns 2
    ```
    """
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
    """
    Takes an iterable list of `(x, y)` and returns it as `(list(x...), list(y...))`
    """
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


@dataclass
class Range:
    start: int
    length: int

    def __init__(self, start: int, length: int) -> None:
        if length < 1:
            raise ValueError(f"Range length {length} must be larger than zero")

        self.start = start
        self.length = length

    def __str__(self):
        return f"[{self.start}, {self.start + self.length - 1}]"

    def __contains__(self, value: int) -> bool:
        return value >= self.start and value < (self.start + self.length)

    def __iter__(self) -> Generator[int, None, None]:
        for i in range(self.start, self.start + self.length):
            yield i

    def __len__(self) -> int:
        return self.length

    def __getitem__(self, index: int) -> int:
        if index >= 0 and index < self.length:
            return self.start + index
        elif index < 0 and index >= (-self.length):
            return self.start + self.length + index
        else:
            raise IndexError(f"Range index {index} out of bounds")

    def __setitem__(self, index: int, value: int):
        raise NotImplementedError()

    def __delitem__(self, index: int):
        raise NotImplementedError()

    def overlaps(self, other: "Range") -> bool:
        return (
            self.start < (other.start + other.length)
            and (self.start + self.length) > other.start
        )

    def split(
        self, other: "Range"
    ) -> "tuple[Range | None, Range, Range | None] | None":
        """
        Splits `self` into multiple parts assuming `other` intersects.
        The contents of the tuple are as follows:

        0: The part of this range before `other`
        1: The part of this range intersects with `other`.
        2: The part of this range after `other`.

        Tuple components `0` and `2` will be set to `None` if there is no valid
        range after cutting it up.

        This function will return `None` if `other` does not overlap.
        """
        my_start = self.start
        my_end = self.start + self.length
        other_start = other.start
        other_end = other.start + other.length

        # Return `None`` if the provided range does not overlap.
        if my_start >= other_end or my_end <= other_start:
            return None

        # Calculate the portion of this range that exists before `other`.
        before_start = my_start
        before_end = max(my_start, other_start)
        before = (
            Range(before_start, before_end - before_start)
            if before_end > before_start
            else None
        )

        # Calculate the portion of this range that is intersected by `other`.
        inner_start = max(my_start, other_start)
        inner_end = min(my_end, other_end)
        inner = Range(inner_start, inner_end - inner_start)

        # Calculate the portion of this range that exists after `other`.
        after_start = min(my_end, other_end)
        after_end = max(my_end, other_end)

        after = (
            Range(after_start, after_end - after_start)
            if after_start < my_end
            else None
        )

        return (before, inner, after)
