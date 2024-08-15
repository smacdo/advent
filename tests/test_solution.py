from advent.solution import AbstractSolver, SolverRegistry, SolverMetadata
from advent.solution import NoSolversFound, SolverVariantNotFound
from advent.solution import Part, Example

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


class SolverMetadataTests(unittest.TestCase):
    def test_default_name(self):
        m = SolverMetadata(klass=Solution_1A, day=15, year=2010)
        self.assertEqual(m.puzzle_name, "2010 day 15")

    def test_variant_name(self):
        m_named_variant = SolverMetadata(
            klass=Solution_1A, day=20, year=1999, variant_name="foobar"
        )
        m_missing_variant = SolverMetadata(klass=Solution_1A, day=20, year=1999)

        self.assertEqual(m_named_variant.variant_name, "foobar")
        self.assertEqual(m_missing_variant.variant_name, "default")


class SolverRegistryTests(unittest.TestCase):
    def test_add_single_solution(self):
        registry = SolverRegistry()
        registry.add(
            SolverMetadata(
                klass=Solution_1A, year=2000, day=1, puzzle_name="Solution_1A"
            )
        )

        self.assertSequenceEqual(
            [s.klass for s in registry.all_solvers_for(2000, 1)], [Solution_1A]
        )

    def test_add_multiple_days(self):
        registry = SolverRegistry()
        registry.add(
            SolverMetadata(
                klass=Solution_1A, year=2000, day=1, puzzle_name="Solution_1A"
            )
        )
        registry.add(
            SolverMetadata(
                klass=Solution_2A, year=2000, day=2, puzzle_name="Solution_2A"
            )
        )

        self.assertSequenceEqual(
            [s.klass for s in registry.all_solvers_for(2000, 1)], [Solution_1A]
        )
        self.assertSequenceEqual(
            [s.klass for s in registry.all_solvers_for(2000, 2)], [Solution_2A]
        )

    def test_add_multiple_years(self):
        registry = SolverRegistry()
        registry.add(
            SolverMetadata(
                klass=Solution_1A, year=2000, day=1, puzzle_name="Solution_1A"
            )
        )
        registry.add(
            SolverMetadata(
                klass=Solution_2A, year=1999, day=1, puzzle_name="Solution_2A"
            )
        )

        self.assertSequenceEqual(
            [s.klass for s in registry.all_solvers_for(2000, 1)], [Solution_1A]
        )
        self.assertSequenceEqual(
            [s.klass for s in registry.all_solvers_for(1999, 1)], [Solution_2A]
        )

    def test_register_multiple_variants(self):
        registry = SolverRegistry()
        registry.add(
            SolverMetadata(
                klass=Solution_1A,
                year=2000,
                day=1,
                puzzle_name="Solution_1A",
                variant_name="A",
            )
        )
        registry.add(
            SolverMetadata(
                klass=Solution_1B,
                year=2000,
                day=1,
                puzzle_name="Solution_1B",
                variant_name="B",
            )
        )
        registry.add(
            SolverMetadata(
                klass=Solution_2A, year=2000, day=2, puzzle_name="Solution_2A"
            )
        )

        self.assertSequenceEqual(
            [(s.klass, s.variant_name) for s in registry.all_solvers_for(2000, 1)],
            [(Solution_1A, "A"), (Solution_1B, "B")],
        )
        self.assertSequenceEqual(
            [(s.klass, s.variant_name) for s in registry.all_solvers_for(2000, 2)],
            [(Solution_2A, "default")],
        )

    def test_get_variants_for_missing_day_or_year(self):
        registry = SolverRegistry()
        self.assertSequenceEqual(registry.all_solvers_for(year=2000, day=1), [])

    def test_get_days_in_order(self):
        registry = SolverRegistry()
        registry.add(
            SolverMetadata(
                klass=Solution_2A, year=2000, day=2, puzzle_name="Solution_2A"
            )
        )
        registry.add(
            SolverMetadata(
                klass=Solution_1A, year=2000, day=1, puzzle_name="Solution_1A"
            )
        )
        self.assertSequenceEqual(list(registry.all_days(year=2000)), [1, 2])

    def test_create_solvers(self):
        registry = SolverRegistry()
        registry.add(
            SolverMetadata(
                klass=Solution_1A, year=2000, day=1, puzzle_name="Solution_1A"
            )
        )
        registry.add(
            SolverMetadata(
                klass=Solution_2A, year=2000, day=2, puzzle_name="Solution_2A"
            )
        )

        s1a = registry.find_solver_for(year=2000, day=1).create_solver_instance()
        self.assertEqual(s1a.part_one(""), "1A_part_one")
        self.assertEqual(s1a.part_two(""), "1A_part_two")

        s2a = registry.find_solver_for(year=2000, day=2).create_solver_instance(
            x="%", y="$"
        )
        self.assertEqual(s2a.part_one(""), "2A%_part_one")
        self.assertEqual(s2a.part_two(""), "2A$_part_two")

    def test_create_solver_with_variant_name(self):
        registry = SolverRegistry()
        registry.add(
            SolverMetadata(
                klass=Solution_1A, year=2000, day=1, puzzle_name="A", variant_name="one"
            )
        )
        registry.add(
            SolverMetadata(
                klass=Solution_1B, year=2000, day=1, puzzle_name="B", variant_name="two"
            )
        )
        registry.add(
            SolverMetadata(klass=Solution_1C, year=2000, day=1, puzzle_name="C")
        )

        s = registry.find_solver_for(2000, 1, variant="two").create_solver_instance()
        self.assertIsInstance(s, Solution_1B)

        s = registry.find_solver_for(2000, 1, variant="one").create_solver_instance()
        self.assertIsInstance(s, Solution_1A)

        s = registry.find_solver_for(
            2000, 1, variant="default"
        ).create_solver_instance()
        self.assertIsInstance(s, Solution_1C)

    def test_create_default_solver(self):
        registry = SolverRegistry()
        registry.add(
            SolverMetadata(
                klass=Solution_1A, year=2000, day=1, puzzle_name="A", variant_name="one"
            )
        )
        registry.add(
            SolverMetadata(
                klass=Solution_1B, year=2000, day=1, puzzle_name="B", variant_name="two"
            )
        )
        registry.add(
            SolverMetadata(klass=Solution_1C, year=2000, day=1, puzzle_name="C")
        )

        s = registry.find_solver_for(2000, 1).create_solver_instance()
        self.assertIsInstance(s, Solution_1C)

    def test_create_any_if_no_default_solver(self):
        registry = SolverRegistry()
        registry.add(
            SolverMetadata(
                klass=Solution_1A, year=2000, day=1, puzzle_name="A", variant_name="one"
            )
        )
        registry.add(
            SolverMetadata(
                klass=Solution_1B, year=2000, day=1, puzzle_name="B", variant_name="two"
            )
        )
        registry.add(
            SolverMetadata(
                klass=Solution_1C,
                year=2000,
                day=1,
                puzzle_name="C",
                variant_name="three",
            )
        )

        s = registry.find_solver_for(2000, 1).create_solver_instance()
        self.assertTrue(
            type(s) is Solution_1A or type(s) is Solution_1B or type(s) is Solution_1C
        )

    def test_no_solvers_for_day(self):
        registry = SolverRegistry()
        registry.add(
            SolverMetadata(
                klass=Solution_1A, year=2000, day=1, puzzle_name="Solution_1A"
            )
        )

        self.assertRaises(
            NoSolversFound, lambda: registry.find_solver_for(year=2000, day=2)
        )

    def test_no_solver_with_variant_name(self):
        registry = SolverRegistry()
        registry.add(
            SolverMetadata(
                klass=Solution_1A, year=2000, day=1, puzzle_name="A", variant_name="one"
            )
        )
        registry.add(
            SolverMetadata(
                klass=Solution_1B, year=2000, day=1, puzzle_name="B", variant_name="two"
            )
        )

        self.assertRaises(
            SolverVariantNotFound,
            lambda: registry.find_solver_for(year=2000, day=1, variant="C"),
        )


class PartTests(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(Part.One, Part.One)
        self.assertEqual(Part.Two, Part.Two)
        self.assertNotEqual(Part.One, Part.Two)
        self.assertNotEqual(Part.Two, Part.One)


class ExampleTests(unittest.TestCase):
    def test_multi_line_input_is_converted_to_single_str_with_newlines(self):
        self.assertEqual(
            Example(["hello world", "test", "  123"], "xyz", Part.Two),
            Example("hello world\ntest\n  123", "xyz", Part.Two),
        )

    def test_equal(self):
        self.assertEqual(
            Example("hello", "world", Part.One), Example("hello", "world", Part.One)
        )
        self.assertNotEqual(
            Example("hello", "world", Part.Two), Example("hello", "world", Part.One)
        )
