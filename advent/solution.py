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
    """Base class for a solver capable of solving puzzle inputs."""

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
    part two for a solver. Examples tend to be small, contrived examples
    similiar in scope to a unit or integration test.
    """

    input: str
    output: str
    part: Part

    def __init__(self, input: str | list[str], output: str, part: Part):
        if isinstance(input, str):
            self.input = input
        else:
            self.input = os.linesep.join(input)

        self.output = output
        self.part = part

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


class SolverMetadata:
    """
    Stores an abstract solver type and other metadata associated with the solver.
    """

    klass: type[AbstractSolver]
    day: int
    year: int
    puzzle_name: str
    variant_name: str | None
    is_slow: bool

    def __init__(
        self,
        klass: type[AbstractSolver],
        day: int,
        year: int,
        puzzle_name: str | None = None,
        variant_name: str | None = None,
        is_slow: bool = False,
    ):
        self.klass = klass
        self.day = day
        self.year = year
        self.puzzle_name = (
            puzzle_name if puzzle_name is not None else f"{year} day {day}"
        )
        self.variant_name = (
            variant_name if variant_name is not None else DEFAULT_VARIANT_NAME
        )
        self.is_slow: bool = is_slow

    def create_solver_instance(self, **kwargs) -> AbstractSolver:
        return self.klass(**kwargs)


class NoSolversFound(Exception):
    def __init__(self, year: int, day: int):
        super().__init__(f"Cannot find any solvers for year {year} day {day}")


class SolverVariantNotFound(Exception):
    def __init__(self, year: int, day: int, variant: str):
        super().__init__(
            f"Cannot find a solver variant named {variant} for year {year} day {day}"
        )


class SolverRegistry:
    """
    Stores a list of solvers for a given year and day.
    """

    solvers: dict[tuple[int, int], list[SolverMetadata]]

    def __init__(self):
        self.solvers = dict()
        self.days = []

    def add(self, solver: SolverMetadata):
        """Adds a solver for an advent of code puzzle"""
        entry_key = (solver.year, solver.day)

        if (solver.year, solver.day) not in self.solvers:
            self.solvers[entry_key] = []

        self.solvers[entry_key].append(solver)

    def has_solver_for(self, year: int, day: int) -> bool:
        """Check if there is at least one solver for the given year and day"""
        return (year, day) in self.solvers

    def all_solvers_for(self, year: int, day: int) -> list[SolverMetadata]:
        """Get all of the solver variants for the given year and day"""
        if (year, day) in self.solvers:
            return self.solvers[(year, day)]
        else:
            return []

    def find_solver_for(
        self, year: int, day: int, variant: str | None = None
    ) -> SolverMetadata:
        variant_name = variant if variant is not None else DEFAULT_VARIANT_NAME
        all_solvers = self.all_solvers_for(year, day)

        if all_solvers is None or len(all_solvers) == 0:
            raise NoSolversFound(year=year, day=day)
        else:
            # Find a solver with the same variant name.
            for s in all_solvers:
                if s.variant_name == variant_name:
                    return s

            # If no variant name was provided and there was no default variant
            # then use any available solver before throwing an exception.
            if variant is None and len(all_solvers) > 0:
                return all_solvers[0]

            raise SolverVariantNotFound(year=year, day=day, variant=variant_name)

    def all_days(self, year: int) -> list[int]:
        """Returns a generator that yields all the days in the given year with at least one solver"""
        days = [k[1] for k in self.solvers if k[0] == year]
        days.sort()
        return days


_GLOBAL_SOLVER_REGISTRY: SolverRegistry = SolverRegistry()


def get_global_solver_registry() -> SolverRegistry:
    return _GLOBAL_SOLVER_REGISTRY


_SOLVER_EXAMPLES: dict[type[AbstractSolver], list[Example]] = dict()


def add_example_for_solver_at_head(cls: type[AbstractSolver], example: Example):
    """Appends `example` to the start of the list of examples for solver type `cls`."""
    if cls not in _SOLVER_EXAMPLES:
        _SOLVER_EXAMPLES[cls] = []

    _SOLVER_EXAMPLES[cls].insert(0, example)


def get_examples_for_solver(
    cls: type[AbstractSolver],
) -> Generator[Example, None, None]:
    """Get an ordered list of examples for the given solver type `cls`."""
    if cls in _SOLVER_EXAMPLES:
        for example in _SOLVER_EXAMPLES[cls]:
            yield example


def get_part_examples_for_solver(
    cls: type[AbstractSolver],
    part: Part,
) -> Generator[Example, None, None]:
    for example in get_examples_for_solver(cls):
        if example.part == part:
            yield example


# TODO: Move to module 'annotations'
# TODO: Rename to 'solver'
def advent_solution(
    day: int,
    year: int,
    name: str | None = None,
    variant: str | None = None,
):
    """Automatically registers a solver class instance with a globally available registry."""

    def wrapper(solver_class: type[AbstractSolver]):
        get_global_solver_registry().add(
            SolverMetadata(
                klass=solver_class,
                year=year,
                day=day,
                puzzle_name=name,
                variant_name=variant,
            )
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
