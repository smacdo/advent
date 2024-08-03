from abc import ABC, abstractmethod
from typing import Generator

DEFAULT_VARIANT_NAME = "default"

# TODO: @slow
# TODO: @part_missing

# TODO: @part_one_missing
# TODO: @part_one_incomplete
# TODO: @part_one_example(input=".....", expected="....")

# TODO: PartStatus [Missing, Incomplete, Broken, Finished]


class AbstractSolver(ABC):
    @abstractmethod
    def part_one(self, input: str) -> str | None:
        pass

    @abstractmethod
    def part_two(self, input: str) -> str | None:
        pass


class Solution:
    """Stores the solver class type for this solution and additional information
    about the solution."""

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

    def create_solver(
        self, day: int, variant: str | None = None, **kwargs
    ) -> AbstractSolver:
        variant_name = variant if variant is not None else DEFAULT_VARIANT_NAME
        solvers = self.solutions_for(day)

        if solvers is None or len(solvers) == 0:
            raise NoSolversForDay(year=self.year, day=day)
        else:
            # Find a solver with the same variant name.
            for s in solvers:
                if s.variant == variant_name:
                    return s.solver(**kwargs)

            # If no variant name was provided and there was no default variant
            # then use any available solver before throwing an exception.
            if variant is None and len(solvers) > 0:
                return solvers[0].solver(**kwargs)

            raise SolverVariantNotFound(year=self.year, day=day, variant=variant_name)


ADVENT_YEARS_REGISTRY: dict[int, AdventYearRegistry] = dict()


def get_global_advent_year_registry(year: int) -> AdventYearRegistry:
    if year not in ADVENT_YEARS_REGISTRY:
        ADVENT_YEARS_REGISTRY[year] = AdventYearRegistry(year)

    return ADVENT_YEARS_REGISTRY[year]


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