from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Generator
import os

DEFAULT_VARIANT_NAME = "default"

type MaybeAnswerType = int | str | None
type AnswerType = int | str

# TODO: @slow
# TODO: PartStatus [Missing, Incomplete, Broken, Finished]


class Part(Enum):
    One = 1
    Two = 2

    def __str__(self) -> str:
        if self == Part.One:
            return "Part one"
        elif self == Part.Two:
            return "Part two"
        else:
            raise Exception("Unhandled enum case in Part __str__")


class AbstractSolver(ABC):
    """Base class for a solver capable of solving puzzle inputs."""

    @abstractmethod
    def part_one(self, input: str) -> MaybeAnswerType:
        pass

    @abstractmethod
    def part_two(self, input: str) -> MaybeAnswerType:
        pass

    def get_part_func(self, part: Part) -> Callable[[str], MaybeAnswerType]:
        """Returns the solver's `part_one` function if `part == Part.One` otherwise the `part_two` function is returned"""
        if part == Part.One:
            return self.part_one
        else:
            return self.part_two


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
    _part_one_examples: list[Example]
    _part_two_examples: list[Example]
    _day: int
    _year: int
    _puzzle_name: str
    _variant_name: str | None
    _is_slow: bool

    def __init__(
        self,
        klass: type[AbstractSolver],
        day: int,
        year: int,
        puzzle_name: str | None = None,
        variant_name: str | None = None,
        is_slow: bool = False,
        examples: list[Example] | None = None,
    ):
        self.klass = klass
        self._day = day
        self._year = year
        self._puzzle_name = (
            puzzle_name if puzzle_name is not None else f"{year} day {day}"
        )
        self._variant_name = (
            variant_name if variant_name is not None else DEFAULT_VARIANT_NAME
        )
        self._is_slow: bool = is_slow
        self._part_one_examples = list()
        self._part_two_examples = list()

        if examples is not None:
            for example in examples:
                if example.part == Part.One:
                    self._part_one_examples.append(example)
                else:
                    self._part_two_examples.append(example)

    def create_solver_instance(self, **kwargs) -> AbstractSolver:
        return self.klass(**kwargs)

    def day(self):
        return self._day

    def year(self):
        return self._year

    def puzzle_name(self):
        return self._puzzle_name

    def variant_name(self):
        return self._variant_name

    def is_slow(self):
        return self._is_slow

    def add_example(self, example: Example):
        """Appends `example` to the start of this solver's examples list."""
        if example.part == Part.One:
            self._part_one_examples.insert(0, example)
        else:
            self._part_two_examples.insert(0, example)

    def examples(self, part: Part) -> Generator[Example, None, None]:
        if part == Part.One:
            yield from self._part_one_examples
        else:
            yield from self._part_two_examples

    def __repr__(self) -> str:
        return f"SolutionMetadata(\n\tday={self._day},\n\tyear={self._year},\n\tname={self._puzzle_name},\n\tvname={self._variant_name},\n\tklass={self.klass},\n\tp1_ex={self._part_one_examples},\n\tp2_ex={self._part_two_examples}\n)"


class NoSolversFound(Exception):
    def __init__(self, year: int, day: int):
        super().__init__(f"Cannot find any solvers for year {year} day {day}")


class SolverVariantNotFound(Exception):
    def __init__(self, year: int, day: int, variant: str):
        super().__init__(
            f"Cannot find a solver variant named {variant} for year {year} day {day}"
        )


class DuplicateSolverType(Exception):
    def __init__(self, solver_type: type[AbstractSolver]):
        super().__init__(f"Cannot register {solver_type} more than once")


class SolverRegistry:
    """
    Stores a list of solvers for a given year and day.
    """

    solvers: dict[tuple[int, int], list[type[AbstractSolver]]]
    metadata: dict[type[AbstractSolver], SolverMetadata]
    examples_scratch: dict[type[AbstractSolver], tuple[list[Example], list[Example]]]

    def __init__(self):
        self.solvers = dict()
        self.metadata = dict()
        self.examples_scratch = dict()

    def add_metadata(self, solver: SolverMetadata):
        """Adds metadata for a new solver class."""
        # Associate the metadata to the solver class.
        if solver.klass in self.metadata:
            raise DuplicateSolverType(solver.klass)
        else:
            self.metadata[solver.klass] = solver

        # Move any examples that have been registered for this type from scratch
        # into this metadata value.
        if solver.klass in self.examples_scratch:
            for e in reversed(self.examples_scratch[solver.klass][0]):
                solver.add_example(e)
            for e in reversed(self.examples_scratch[solver.klass][1]):
                solver.add_example(e)

            del self.examples_scratch[solver.klass]

        # Add a solver entry for this day + year.
        entry_key = (solver.year(), solver.day())

        if (solver.year(), solver.day()) not in self.solvers:
            self.solvers[entry_key] = []

        self.solvers[entry_key].append(solver.klass)

    def add_example(self, solver_class: type[AbstractSolver], example: Example):
        """Appends `example` to the start of the list of examples for solver `solver_class`."""

        # Add the example directly to the solver's metadata if it exists.
        if solver_class in self.metadata:
            self.metadata[solver_class].add_example(example)
        else:
            # Otherwise add the exapmles to scratch so it can be added once the
            # metadata info is added.
            if solver_class not in self.examples_scratch:
                self.examples_scratch[solver_class] = (list(), list())

            if example.part == Part.One:
                self.examples_scratch[solver_class][0].insert(0, example)
            else:
                self.examples_scratch[solver_class][1].insert(0, example)

    def get_examples(
        self, solver_class: type[AbstractSolver], part: Part
    ) -> Generator[Example, None, None]:
        # Use the examples from the solver's metadata if available.
        if solver_class in self.metadata:
            yield from self.metadata[solver_class].examples(part)
        else:
            # Otherwise use the temporary scratch exmaples.
            if part == Part.One:
                yield from self.examples_scratch[solver_class][0]
            else:
                yield from self.examples_scratch[solver_class][1]

    def has_solver_for(self, year: int, day: int) -> bool:
        """Check if there is at least one solver for the given year and day"""
        return (year, day) in self.solvers

    def all_solvers_for(self, year: int, day: int) -> list[SolverMetadata]:
        """Get all of the solver variants for the given year and day"""
        if (year, day) in self.solvers:
            return [self.metadata[x] for x in self.solvers[(year, day)]]
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
                if s.variant_name() == variant_name:
                    return s

            # If no variant name was provided and there was no default variant
            # then use any available solver before throwing an exception.
            if variant is None and len(all_solvers) > 0:
                return all_solvers[0]

            raise SolverVariantNotFound(year=year, day=day, variant=variant_name)

    def all_days(self, year: int) -> list[int]:
        """
        Returns a sorted list of days in the requested year that have a solution.
        """
        days = [k[1] for k in self.solvers if k[0] == year]
        days.sort()
        return days

    def all_years(self) -> list[int]:
        """
        Returns a sorted list of years that have at least one day with a solution.
        """
        years: list[int] = []

        for year, _ in self.solvers.keys():
            if year not in years:
                years.append(year)

        years.sort()
        return years


_GLOBAL_SOLVER_REGISTRY: SolverRegistry = SolverRegistry()


def get_global_solver_registry() -> SolverRegistry:
    return _GLOBAL_SOLVER_REGISTRY
