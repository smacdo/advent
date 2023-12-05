from typing import Any, ClassVar, Dict, Iterable, Optional, Self, Tuple, Type, TypeVar, Union

import logging
import typing
import unittest

AdventDay = TypeVar("AdventDay", bound="AdventDaySolver")

class AdventDaySolver:
    """The parent class for all Advent day solutions which will take care of 
    self registration and other goodies."""

    day_classes: ClassVar[Dict[int, Dict[int, Any]]] = dict()

    def __init__(self, input: Optional[Iterable[Iterable[str]]] = None):
        # Load the actual input if no input was given.
        if not input:
            day = getattr(type(self), "advent_day")
            year = getattr(type(self), "advent_year")
            
            self.input = load_input(day, year)
        else:
            self.input = input

    #==========================================================================#
    # Subclass registration                                                    #
    #==========================================================================#
    def __init_subclass__(cls, day: Union[int, str], year: Union[int, str], name: str, solution: Optional[Tuple[Any, Any]]) -> None:
        AdventDaySolver._add_day_class(cls, day, year, name, solution)

    @classmethod
    def _add_day_class(cls, day_class: Type[AdventDay], day: Union[int, str], year: Union[int, str], name: str, solution: Optional[Tuple[Any, Any]]) -> None:
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

    #==========================================================================#
    # AdventDaySolver public class methods                                     #
    #==========================================================================#
    @classmethod
    def years(cls) -> list[int]:
        return list(AdventDaySolver.day_classes.keys())
    
    @classmethod
    def days(cls, year: Union[int, str]) -> list[int]:
        return list(AdventDaySolver.day_classes[int(year)].keys())

    @classmethod
    def new_solver(cls, day: Union[int, str], year: Union[int, str]) -> Self:
        return typing.cast(Self, AdventDaySolver.day_classes[int(year)][int(day)](None))
    
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
    def solution(cls) -> Optional[Tuple[Any, Any]]:
        return getattr(cls, "advent_solution")

    #==========================================================================#
    # AdventDaySolver virtual method                                           #
    #==========================================================================#
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

def load_input(day: Union[int, str], year: Union[int, str]) -> Iterable[Iterable[str]]:
    # Load the actual input if no input was given.
    with open(f"inputs/{year}/day{day}.txt", "r", encoding="utf-8") as file:
        input: Iterable[Iterable[str]] = [line for line in file]
        return input

def init_logging(default_level=logging.INFO):
    add_logging_level("TRACE", logging.DEBUG - 5)
    logging.basicConfig(level=default_level)


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


class TestUtilsModule(unittest.TestCase):
    def test_load_input(self):
        input = load_input(0, 0)
        self.assertEqual(input, ["hello", "123"])

