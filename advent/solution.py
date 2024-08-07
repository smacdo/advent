from abc import ABC, abstractmethod
from enum import Enum
from typing import Generator
import os

DEFAULT_VARIANT_NAME = "default"

# TODO: @slow
# TODO: @part_missing

# TODO: @part_one_missing
# TODO: @part_one_incomplete
# TODO: @part_one_example(input=".....", expected="....")

# TODO: PartStatus [Missing, Incomplete, Broken, Finished]


class AbstractSolver(ABC):
    """Base class for solutions."""

    @abstractmethod
    def part_one(self, input: str) -> str | None:
        pass

    @abstractmethod
    def part_two(self, input: str) -> str | None:
        pass


class Part(Enum):
    One = 0
    Two = 1


class Example:
    """
    Provides an input example and the expected output for either part one or
    part two for a solution. Examples tend to be small, contrived examples
    similiar in scope to a unit or integration test.
    """

    def __init__(self, input: str | list[str], output: str, part: Part):
        if isinstance(input, str):
            self.input: str = input
        else:
            self.input: str = os.linesep.join(input)

        self.output: str = output
        self.part: Part = part

    def __eq__(self, value: object) -> bool:
        if type(value) is Example:
            return (
                self.input == value.input
                and self.output == value.output
                and self.part == value.part
            )
        else:
            return False

    def __repr__(self) -> str:
        return f"Example(input={self.input}, output={self.output}, part={self.part})"


class Solution:
    """
    Stores an abstract solver type and other metadata associated with a solution
    to a puzzle.
    """

    def __init__(
        self,
        solver: type[AbstractSolver],
        day: int,
        year: int,
        name: str | None = None,
        variant: str | None = None,
        slow: bool = False,
    ):
        self.solver: type[AbstractSolver] = solver
        self.day: int = day
        self.year: int = year
        self.name: str = name if name is not None else f"{year} day {day}"
        self.variant: str = variant if variant is not None else DEFAULT_VARIANT_NAME
        self.slow: bool = slow


class NoSolversForDay(Exception):
    def __init__(self, year: int, day: int):
        super().__init__(f"Cannot find any solvers for year {year} day {day}")


class SolverVariantNotFound(Exception):
    def __init__(self, year: int, day: int, variant: str):
        super().__init__(
            f"Cannot find a solver variant named {variant} for year {year} day {day}"
        )


class AdventYearRegistry:
    """Holds a list of solutions for one or more advent days in a year"""

    def __init__(self, year: int):
        self.year: int = year
        self.solutions: dict[int, list[Solution]] = dict()
        self.days: list[int] = []

    def add(
        self,
        solver: type[AbstractSolver],
        day: int,
        name: str | None = None,
        variant: str | None = None,
        slow: bool = False,
    ):
        """Adds a solver for an advent of code puzzle"""
        if day not in self.solutions:
            self.solutions[day] = []
            self.days.append(day)
            self.days.sort()

        self.solutions[day].append(
            Solution(
                solver=solver,
                day=day,
                year=self.year,
                name=name,
                variant=variant,
                slow=slow,
            )
        )

    def has_solution_for_day(self, day: int) -> bool:
        """Check if there is at least one solution"""
        return day in self.solutions

    def solutions_for(self, day: int) -> list[Solution]:
        """Get all of the solution variants for an advent day"""
        if day in self.solutions:
            return self.solutions[day]
        else:
            return []

    def all_days(self) -> Generator[int, None, None]:
        """Returns a generator that yields all the advent days with at least one solution"""
        for day in self.days:
            yield day

    def get_solver_class(
        self, day: int, variant: str | None = None
    ) -> type[AbstractSolver]:
        variant_name = variant if variant is not None else DEFAULT_VARIANT_NAME
        solutions = self.solutions_for(day)

        if solutions is None or len(solutions) == 0:
            raise NoSolversForDay(year=self.year, day=day)
        else:
            # Find a solver with the same variant name.
            for s in solutions:
                if s.variant == variant_name:
                    return s.solver

            # If no variant name was provided and there was no default variant
            # then use any available solver before throwing an exception.
            if variant is None and len(solutions) > 0:
                return solutions[0].solver

            raise SolverVariantNotFound(year=self.year, day=day, variant=variant_name)

    def create_solver(
        self, day: int, variant: str | None = None, **kwargs
    ) -> AbstractSolver:
        return self.get_solver_class(day, variant)(**kwargs)


_ADVENT_YEARS_REGISTRY: dict[int, AdventYearRegistry] = dict()


def get_global_advent_year_registry(year: int) -> AdventYearRegistry:
    """Returns a registry containing all of the solutions registered for the given advent year."""
    if year not in _ADVENT_YEARS_REGISTRY:
        _ADVENT_YEARS_REGISTRY[year] = AdventYearRegistry(year)

    return _ADVENT_YEARS_REGISTRY[year]


_SOLUTION_EXAMPLES: dict[type[AbstractSolver], list[Example]] = dict()


def add_example_for_solver_at_head(cls: type[AbstractSolver], example: Example):
    """Appends `example` to the start of the list of examples for solver type `cls`."""
    if cls not in _SOLUTION_EXAMPLES:
        _SOLUTION_EXAMPLES[cls] = []

    _SOLUTION_EXAMPLES[cls].insert(0, example)


def get_examples_for_solver(
    cls: type[AbstractSolver],
) -> Generator[Example, None, None]:
    """Get an ordered list of examples for the given solver type `cls`."""
    if cls in _SOLUTION_EXAMPLES:
        for example in _SOLUTION_EXAMPLES[cls]:
            yield example


def get_part_examples_for_solver(
    cls: type[AbstractSolver],
    part: Part,
) -> Generator[Example, None, None]:
    for example in get_examples_for_solver(cls):
        if example.part == part:
            yield example


def advent_solution(
    day: int,
    year: int,
    name: str | None = None,
    variant: str | None = None,
):
    """Automatically registers a solver class instance with a globally available registry."""

    def wrapper(solver_class: type[AbstractSolver]):
        get_global_advent_year_registry(year).add(
            solver_class, day=day, name=name, variant=variant, slow=False
        )

        return solver_class

    return wrapper


def part_one_example(input: str | list[str], output: str):
    """Set an example for part one of this solver"""

    def wrapper(solver_class: type[AbstractSolver]):
        add_example_for_solver_at_head(
            solver_class, Example(input=input, output=output, part=Part.One)
        )

        return solver_class

    return wrapper


def part_two_example(input: str | list[str], output: str):
    """Set an example for part two of this solver"""

    def wrapper(solver_class: type[AbstractSolver]):
        add_example_for_solver_at_head(
            solver_class, Example(input=input, output=output, part=Part.Two)
        )

        return solver_class

    return wrapper
