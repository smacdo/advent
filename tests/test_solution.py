from advent.solution import AbstractSolver, AdventYearRegistry, Solution
from advent.solution import NoSolversForDay, SolverVariantNotFound

import unittest


class Solution_1A(AbstractSolver):
    def part_one(self, input: str) -> str | None:
        return "1A_part_one"

    def part_two(self, input: str) -> str | None:
        return "1A_part_two"


class Solution_1B(AbstractSolver):
    def part_one(self, input: str) -> str | None:
        return "1B_part_one"

    def part_two(self, input: str) -> str | None:
        return "1B_part_two"


class Solution_1C(AbstractSolver):
    def part_one(self, input: str) -> str | None:
        return "1C_part_one"

    def part_two(self, input: str) -> str | None:
        return "1C_part_two"


class Solution_2A(AbstractSolver):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def part_one(self, input: str) -> str | None:
        return f"2A{self.x}_part_one"

    def part_two(self, input: str) -> str | None:
        return f"2A{self.y}_part_two"


class SolutionMetadataTests(unittest.TestCase):
    def test_default_name(self):
        m = Solution(solver=Solution_1A, day=15, year=2010)
        self.assertEqual(m.name, "2010 day 15")

    def test_variant_name(self):
        m_named_variant = Solution(
            solver=Solution_1A, day=20, year=1999, variant="foobar"
        )
        m_missing_variant = Solution(solver=Solution_1A, day=20, year=1999)

        self.assertEqual(m_named_variant.variant, "foobar")
        self.assertEqual(m_missing_variant.variant, "default")


class AdventYearRegistryTests(unittest.TestCase):
    def test_add_single_solution(self):
        registry = AdventYearRegistry(year=2000)
        registry.add(solver=Solution_1A, day=1, name="Solution_1A")

        self.assertSequenceEqual(
            [s.solver for s in registry.solutions_for(1)], [Solution_1A]
        )

    def test_add_multiple_days(self):
        registry = AdventYearRegistry(year=2000)
        registry.add(solver=Solution_1A, day=1, name="Solution_1A")
        registry.add(solver=Solution_2A, day=2, name="Solution_2A")

        self.assertSequenceEqual(
            [s.solver for s in registry.solutions_for(1)], [Solution_1A]
        )
        self.assertSequenceEqual(
            [s.solver for s in registry.solutions_for(2)], [Solution_2A]
        )

    def test_register_multiple_variants(self):
        registry = AdventYearRegistry(year=2000)
        registry.add(
            solver=Solution_1A,
            day=1,
            name="Solution_1A",
            variant="A",
        )
        registry.add(
            solver=Solution_1B,
            day=1,
            name="Solution_1B",
            variant="B",
        )
        registry.add(solver=Solution_2A, day=2, name="Solution_2A")

        self.assertSequenceEqual(
            [(s.solver, s.variant) for s in registry.solutions_for(1)],
            [(Solution_1A, "A"), (Solution_1B, "B")],
        )
        self.assertSequenceEqual(
            [(s.solver, s.variant) for s in registry.solutions_for(2)],
            [(Solution_2A, "default")],
        )

    def test_get_variants_for_missing_day(self):
        registry = AdventYearRegistry(year=2000)
        self.assertSequenceEqual(registry.solutions_for(1), [])

    def test_get_days_in_order(self):
        registry = AdventYearRegistry(year=2000)
        registry.add(solver=Solution_2A, day=2, name="Solution_2A")
        registry.add(solver=Solution_1A, day=1, name="Solution_1A")
        self.assertSequenceEqual(list(registry.all_days()), [1, 2])

    def test_create_solvers(self):
        registry = AdventYearRegistry(year=2000)
        registry.add(solver=Solution_1A, day=1, name="Solution_1A")
        registry.add(solver=Solution_2A, day=2, name="Solution_2A")

        s1a = registry.create_solver(1)
        self.assertEqual(s1a.part_one(""), "1A_part_one")
        self.assertEqual(s1a.part_two(""), "1A_part_two")

        s2a = registry.create_solver(2, x="%", y="$")
        self.assertEqual(s2a.part_one(""), "2A%_part_one")
        self.assertEqual(s2a.part_two(""), "2A$_part_two")

    def test_create_solver_with_variant_name(self):
        registry = AdventYearRegistry(year=2000)
        registry.add(solver=Solution_1A, day=1, name="A", variant="one")
        registry.add(solver=Solution_1B, day=1, name="B", variant="two")
        registry.add(solver=Solution_1C, day=1, name="C")

        s = registry.create_solver(1, variant="two")
        self.assertIsInstance(s, Solution_1B)

        s = registry.create_solver(1, variant="one")
        self.assertIsInstance(s, Solution_1A)

        s = registry.create_solver(1, variant="default")
        self.assertIsInstance(s, Solution_1C)

    def test_create_default_solver(self):
        registry = AdventYearRegistry(year=2000)
        registry.add(solver=Solution_1A, day=1, name="A", variant="one")
        registry.add(solver=Solution_1B, day=1, name="B", variant="two")
        registry.add(solver=Solution_1C, day=1, name="C")

        s = registry.create_solver(1)
        self.assertIsInstance(s, Solution_1C)

    def test_create_any_if_no_default_solver(self):
        registry = AdventYearRegistry(year=2000)
        registry.add(solver=Solution_1A, day=1, name="A", variant="one")
        registry.add(solver=Solution_1B, day=1, name="B", variant="two")
        registry.add(solver=Solution_1C, day=1, name="C", variant="three")

        s = registry.create_solver(1)
        self.assertTrue(
            type(s) is Solution_1A or type(s) is Solution_1B or type(s) is Solution_1C
        )

    def test_no_solvers_for_day(self):
        registry = AdventYearRegistry(year=2000)
        registry.add(solver=Solution_1A, day=1, name="Solution_1A")

        self.assertRaises(NoSolversForDay, lambda: registry.create_solver(day=2))

    def test_no_solver_with_variant_name(self):
        registry = AdventYearRegistry(year=2000)
        registry.add(solver=Solution_1A, day=1, name="A", variant="one")
        registry.add(solver=Solution_1B, day=1, name="B", variant="two")

        self.assertRaises(
            SolverVariantNotFound, lambda: registry.create_solver(1, variant="C")
        )
