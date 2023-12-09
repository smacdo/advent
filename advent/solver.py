import logging
from typing import (
    Self,
    TypeVar,
    ClassVar,
    Dict,
    Any,
    Iterable,
    Union,
    Optional,
    Type,
    Tuple,
    cast,
)
import unittest

from advent import utils

AdventDay = TypeVar("AdventDay", bound="AdventDaySolver")


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
        return cast(Self, AdventDaySolver.day_classes[int(year)][int(day)])

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
        return self.solver(
            utils.load_input(day=self.solver.day(), year=self.solver.year())
        )

    def _create_sample_solver(self, input: str):
        return self.solver(input.split("\n"))


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


def solver_main(
    test_program: unittest.TestProgram, solver_class: type[AdventDaySolver]
) -> None:
    utils.init_logging(logging.DEBUG)

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
            input_lines = utils.load_input(
                day=solver_class.day(), year=solver_class.year()
            )
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
