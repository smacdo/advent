#!/usr/bin/env python3

from typing import Type
from advent.solver import AdventDaySolver
from advent.utils import Direction, Grid, Point, load_input, first_and_last, unzip, count_if, new_grid_from_input_lines

import typing
import unittest


class AdventDaySolverTests(unittest.TestCase):
    class Day0_0(AdventDaySolver, year=0, day=0, name="", solution=None):
        pass

    class Day1(AdventDaySolver, year=2023, day=1, name="", solution=None):
        def secret_token(self):
            return 22

    class Day2(AdventDaySolver, year=2023, day=2, name="", solution=None):
        pass

    class Day4(AdventDaySolver, year=2023, day=4, name="", solution=None):
        def secret_token(self):
            return "hello"

    class Day2_2022(AdventDaySolver, year=2022, day=2, name="", solution=None):
        pass

    def test_get_years(self):
        years = AdventDaySolver.years()
        years.sort()

        self.assertSequenceEqual(years, [0, 2022, 2023])

    def test_get_days(self):
        days = AdventDaySolver.days(2023)
        days.sort()

        self.assertSequenceEqual(days, [1, 2, 4])

        days = AdventDaySolver.days(2022)
        days.sort()

        self.assertSequenceEqual(days, [2])

    def test_create_day(self):
        d = typing.cast(
            Type[AdventDaySolverTests.Day1],
            AdventDaySolver.get_solver(day=1, year=2023)([[]]),
        )
        self.assertEqual(22, d.secret_token())

        d = typing.cast(
            Type[AdventDaySolverTests.Day4],
            AdventDaySolver.get_solver(day=4, year=2023)([[]]),
        )
        self.assertEqual("hello", d.secret_token())


class TestDirection(unittest.TestCase):
    def test_get_cardinal_directions(self):
        self.assertSequenceEqual(
            [Direction.East, Direction.North, Direction.West, Direction.South],
            [d for d in Direction.cardinal_dirs()],
        )

    def test_get_names(self):
        self.assertEqual("East", str(Direction.East))
        self.assertEqual("North", str(Direction.North))
        self.assertEqual("West", str(Direction.West))
        self.assertEqual("South", str(Direction.South))

    def test_to_point(self):
        self.assertEqual(Point(1, 0), Direction.East.to_point())
        self.assertEqual(Point(0, -1), Direction.North.to_point())
        self.assertEqual(Point(-1, 0), Direction.West.to_point())
        self.assertEqual(Point(0, 1), Direction.South.to_point())


class TestPoint(unittest.TestCase):
    def test_new_points(self):
        p = Point(-16, 2)
        self.assertEqual(p.x, -16)
        self.assertEqual(p.y, 2)

    def test_point_to_string(self):
        self.assertEqual("-4, -123", f"{Point(-4, -123)}")

    def test_point_repr(self):
        self.assertEqual("Point(x=-4, y=-123)", repr(Point(-4, -123)))

    def test_get_set_by_index(self):
        p = Point(16, 8123)
        self.assertEqual(p[0], 16)
        self.assertEqual(p[1], 8123)

        p[0] = 2
        p[1] = -4

        self.assertEqual(p[0], 2)
        self.assertEqual(p[1], -4)

    def test_get_set_by_index_throw_exception_if_not_0_or_1(self):
        def try_get_invalid():
            p = Point(5, 6)
            p[2]

        def try_set_invalid():
            p = Point(5, 6)
            p[2] = 0

        self.assertRaises(Exception, try_get_invalid)
        self.assertRaises(Exception, try_set_invalid)

    def test_equal_not_equal(self):
        self.assertEqual(Point(5, 13), Point(5 + 0, 15 - 2))
        self.assertNotEqual(Point(5, 13), Point(6, 13))
        self.assertNotEqual(Point(5, 13), Point(5, 12))

    def test_math_ops(self):
        self.assertEqual(Point(18, -4), Point(20, -5) + Point(-2, 1))
        self.assertEqual(Point(17, 1), Point(20, -5) - Point(3, -6))
        self.assertEqual(Point(-24, -8), Point(6, 2) * -4)
        self.assertEqual(Point(6, 2), Point(-24, -8) / -4)
        self.assertEqual(Point(4, -123), -Point(-4, 123))
        self.assertEqual(Point(4, 123), abs(Point(-4, 123)))

    def test_hash(self):
        points = dict()
        points[Point(3, -15)] = "hello"

        self.assertIn(Point(3, -15), points)
        self.assertEqual(points[Point(3, -15)], "hello")
        self.assertEqual(points[Point(2, -18) + Point(1, 3)], "hello")

        self.assertIn(Point(3, -15), points)
        self.assertNotIn(Point(3, 15), points)
        self.assertNotIn(Point(16, 7), points)


class TestGrid(unittest.TestCase):
    def test_create_grid_from_default_value(self):
        g = Grid(2, 3, "f")
        self.assertEqual(2, g.x_count)
        self.assertEqual(3, g.y_count)
        self.assertSequenceEqual(["f", "f", "f", "f", "f", "f"], g.cells)

    def test_create_grid_from_2d_array(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        self.assertEqual(2, g.x_count)
        self.assertEqual(3, g.y_count)
        self.assertSequenceEqual(["1", "2", "a", "b", "7", "8"], g.cells)

    def test_get_set_values(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        self.assertEqual("2", g[Point(1, 0)])
        self.assertEqual("7", g[Point(0, 2)])

        g[Point(1, 1)] = "$"
        g[Point(0, 2)] = "&"

        self.assertEqual("$", g[Point(1, 1)])
        self.assertEqual("&", g[Point(0, 2)])

    def test_to_string(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        self.assertEqual("12\nab\n78", str(g))

    def test_yield_row(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        self.assertSequenceEqual([(Point(0, 0), "1"), (Point(1, 0), "2")], list(g.yield_row(0)))
        self.assertSequenceEqual([(Point(0, 1), "a"), (Point(1, 1), "b")], list(g.yield_row(1)))
        self.assertSequenceEqual([(Point(0, 2), "7"), (Point(1, 2), "8")], list(g.yield_row(2)))

    def test_from_input_lines(self):
        g = new_grid_from_input_lines("""hi3\n3$x""".split("\n"))
        self.assertEqual(2, g.row_count())
        self.assertEqual(3, g.col_count())
        self.assertSequenceEqual(["h", "i", "3"], g.row(0))
        self.assertSequenceEqual(["3", "$", "x"], g.row(1))

    def test_iterate_rows(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        vals = [[c for c in row] for row in g.rows()]
        self.assertSequenceEqual(["1", "2"], vals[0])
        self.assertSequenceEqual(["a", "b"], vals[1])
        self.assertSequenceEqual(["7", "8"], vals[2])


class TestCountIf(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(0, count_if([], lambda x: False))
        self.assertEqual(0, count_if(iter([]), lambda x: False))

    def test_count(self):
        self.assertEqual(2, count_if([1, 2, 3, 4], lambda x: x % 2 == 0))

class TestFirstAndLast(unittest.TestCase):
    def test_one_item_list(self):
        self.assertEqual((10, 10), first_and_last([10]))

    def test_multi_item_list(self):
        self.assertEqual((13, 3), first_and_last([13, 3]))
        self.assertEqual((81, "a"), first_and_last([81, "a"]))

    def test_empty_list_throws_exception(self):
        self.assertRaises(StopIteration, lambda: first_and_last([]))


class TestUnzip(unittest.TestCase):
    def test_unzip_2(self):
        A = [5, 8, 10]
        B = [-2, 12, "b"]
        self.assertEqual((A, B), unzip([(5, -2), (8, 12), (10, "b")]))


class TestUtilsModule(unittest.TestCase):
    def test_load_input(self):
        input = load_input(0, 0)
        self.assertEqual(input, ["hello", "123"])


if __name__ == "__main__":
    unittest.main()
