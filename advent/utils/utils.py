from typing import (
    Any,
    ClassVar,
    Dict,
    Iterable,
    Optional,
    Self,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import logging
import typing
import unittest

AdventDay = TypeVar("AdventDay", bound="AdventDaySolver")
T = TypeVar("T")


# TODO: Move the factory functions for tracking subclasses out of AdventDaySolver
#       because its mixing in factory stuff and makes the API confusing.
#   - _add_day_class  => GetGlobalSolverRegistry().add_solver(s, day, year)
#   - years =>  .solvers()
#   - days  =>  .solvers()
class AdventDaySolver:
    """The parent class for all Advent day solutions which will take care of
    self registration and other goodies."""

    day_classes: ClassVar[Dict[int, Dict[int, Any]]] = dict()

    def __init__(self, input: Iterable[Iterable[str]]):
        self.input = input

    # ==========================================================================#
    # Subclass registration                                                    #
    # ==========================================================================#
    def __init_subclass__(
        cls,
        day: Union[int, str],
        year: Union[int, str],
        name: str,
        solution: Optional[Tuple[Any, Any]],
    ) -> None:
        AdventDaySolver._add_day_class(cls, day, year, name, solution)

    @classmethod
    def _add_day_class(
        cls,
        day_class: Type[AdventDay],
        day: Union[int, str],
        year: Union[int, str],
        name: str,
        solution: Optional[Tuple[Any, Any]],
    ) -> None:
        if year not in AdventDaySolver.day_classes:
            AdventDaySolver.day_classes[int(year)] = dict()

        if day in AdventDaySolver.day_classes[int(year)]:
            raise Exception(f"Advent day {day} year {year} class already registered")

        # Skip test / template / etc subclasses.
        if int(day) < 1 or int(year) < 1:
            return

        # Remember the solver's advent properties.
        setattr(day_class, "advent_day", day)
        setattr(day_class, "advent_year", year)
        setattr(day_class, "advent_name", name)
        setattr(day_class, "advent_solution", solution)

        # Register the solver into our list of solvers.
        AdventDaySolver.day_classes[int(year)][int(day)] = day_class

    # ==========================================================================#
    # AdventDaySolver public class methods                                     #
    # ==========================================================================#
    @classmethod
    def years(cls) -> list[int]:
        return list(AdventDaySolver.day_classes.keys())

    @classmethod
    def days(cls, year: Union[int, str]) -> list[int]:
        return list(AdventDaySolver.day_classes[int(year)].keys())

    @classmethod
    def get_solver(cls, day: Union[int, str], year: Union[int, str]) -> Self:
        return typing.cast(Self, AdventDaySolver.day_classes[int(year)][int(day)])

    @classmethod
    def day(cls) -> int:
        return int(getattr(cls, "advent_day"))

    @classmethod
    def year(cls) -> int:
        return int(getattr(cls, "advent_year"))

    @classmethod
    def name(cls) -> str:
        return getattr(cls, "advent_name")

    @classmethod
    def solution(cls) -> Tuple[Any, Any]:
        return getattr(cls, "advent_solution")

    # ==========================================================================#
    # AdventDaySolver virtual method                                           #
    # ==========================================================================#
    def solve(self) -> Tuple[Any, Any]:
        raise NotImplementedError()


class AdventDayTestCase(unittest.TestCase):
    def setUp(self, solver):
        super().setUp()
        self.solver = solver

    def _create_real_solver(self):
        return self.solver(load_input(day=self.solver.day(), year=self.solver.year()))

    def _create_sample_solver(self, input: str):
        return self.solver(input.split("\n"))


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


def print_part_solution(expected: Any, actual: Any, part_num: int) -> None:
    if expected is None:
        if actual is None:
            print(f"✏️ Part {part_num} is not implemented")
        else:
            print(f"🤔 Potential solution for part {part_num}: {actual}")

    else:
        if expected == actual:
            print(f"✅ Correct solution for part {part_num}: {actual}")
        else:
            print(
                f"❌ Wrong solution for part {part_num}: expected `{expected}` but was `{actual}`"
            )


def run_tests_for_solver(
    test_program: unittest.TestProgram, solver_class: type[AdventDaySolver]
) -> None:
    # Did tests pass? Only try actual puzzle inputs if all unit tests pass.
    if test_program.result.wasSuccessful():
        logging.info(
            "unit tests passed - will try running solver on actual puzzle input"
        )

        # Verify the solver defined a valid day, year and that the puzzle input
        # file exists.
        if solver_class.day() < 1:
            logging.error(f"{solver_class.__name__} `day` attribute not set")
            return
        if solver_class.year() < 1:
            logging.error(f"{solver_class.__name__} `year` attribute not set")
            return

        try:
            input_lines = load_input(day=solver_class.day(), year=solver_class.year())
        except FileNotFoundError as e:
            logging.error(f"Puzzle input file missing: {e}")
            return

        # Test passed! Try running the solver to see what happens.
        expected = solver_class.solution()
        actual = solver_class(input_lines).solve()

        print_part_solution(expected[0], actual[0], 1)
        print_part_solution(expected[1], actual[1], 2)
    else:
        logging.warning("unit tests did not pass, will skip actual puzzle input")


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
