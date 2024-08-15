from advent.solution import AbstractSolver, Example, Part, advent_solution
from advent.solution import part_one_example, part_two_example
from advent.solution import get_global_solver_registry
from advent.solution import get_examples_for_solver

import unittest


@advent_solution(day=12, year=2012, name="Puzzles R Awesome", variant="superawesome")
@part_one_example(input="abc", output="A1B2C2")
@part_one_example(input="x", output="22")
@part_two_example(input="89", output="yes")
class DecoratedTestSolution(AbstractSolver):
    def part_one(self, input: str) -> str | None:
        return "1A_part_one"

    def part_two(self, input: str) -> str | None:
        return "1A_part_two"


class SolutionDecoratorTests(unittest.TestCase):
    def test_is_registered_with_expected_atttributes(self):
        registry = get_global_solver_registry()
        solvers = registry.all_solvers_for(2012, 12)

        self.assertEqual(len(solvers), 1)

        self.assertEqual(solvers[0].klass, DecoratedTestSolution)
        self.assertEqual(solvers[0].day, 12)
        self.assertEqual(solvers[0].year, 2012)
        self.assertEqual(solvers[0].puzzle_name, "Puzzles R Awesome")
        self.assertEqual(solvers[0].variant_name, "superawesome")

    def test_is_registered_with_expected_examples_in_expected_order(self):
        examples = list(get_examples_for_solver(DecoratedTestSolution))
        self.assertSequenceEqual(
            examples,
            [
                Example(input="abc", output="A1B2C2", part=Part.One),
                Example(input="x", output="22", part=Part.One),
                Example(input="89", output="yes", part=Part.Two),
            ],
        )

    # TODO: test for part one and part two examples
