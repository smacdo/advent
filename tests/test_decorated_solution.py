from donner.annotations import solver, example
from donner.solution import AbstractSolver, Example, MaybeAnswerType, Part
from donner.solution import get_global_solver_registry

import unittest


@solver(day=12, year=2012, name="Puzzles R Awesome", variant="superawesome")
@example(input="abc", part_one="A1B2C2")
@example(input="x", part_one="22")
@example(input="89", part_two="yes")
class DecoratedTestSolution(AbstractSolver):
    def part_one(self, input: str) -> MaybeAnswerType:
        return "1A_part_one"

    def part_two(self, input: str) -> MaybeAnswerType:
        return "1A_part_two"


class SolutionDecoratorTests(unittest.TestCase):
    def test_is_registered_with_expected_atttributes(self):
        registry = get_global_solver_registry()
        solvers = registry.all_solvers_for(2012, 12)

        self.assertEqual(len(solvers), 1)

        self.assertEqual(solvers[0].klass, DecoratedTestSolution)
        self.assertEqual(solvers[0].day(), 12)
        self.assertEqual(solvers[0].year(), 2012)
        self.assertEqual(solvers[0].puzzle_name(), "Puzzles R Awesome")
        self.assertEqual(solvers[0].variant_name(), "superawesome")

    def test_is_registered_with_expected_examples_in_expected_order(self):
        self.assertSequenceEqual(
            list(
                get_global_solver_registry().get_examples(
                    DecoratedTestSolution, Part.One
                )
            ),
            [
                Example(input="abc", output="A1B2C2", part=Part.One),
                Example(input="x", output="22", part=Part.One),
            ],
        )
        self.assertSequenceEqual(
            list(
                get_global_solver_registry().get_examples(
                    DecoratedTestSolution, Part.Two
                )
            ),
            [
                Example(input="89", output="yes", part=Part.Two),
            ],
        )
