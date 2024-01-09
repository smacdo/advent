#!/usr/bin/env python3

from typing import Type
from advent.solver import AdventDaySolver
from advent.utils import (
    Direction,
    Grid,
    load_input,
    first_and_last,
    unzip,
    count_if,
    new_grid_from_input_lines,
    BFS,
    all_pairs,
    combinations,
    PriorityQueue,
    astar_search,
    manhattan_distance,
)
from oatmeal import Point

import copy
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

    def test_reverse(self):
        self.assertEqual(Direction.West, Direction.East.reverse())
        self.assertEqual(Direction.South, Direction.North.reverse())
        self.assertEqual(Direction.East, Direction.West.reverse())
        self.assertEqual(Direction.North, Direction.South.reverse())

    def test_from_point(self):
        self.assertEqual(Direction.East, Direction.from_point(Point(1, 0)))
        self.assertEqual(Direction.North, Direction.from_point(Point(0, -1)))
        self.assertEqual(Direction.West, Direction.from_point(Point(-1, 0)))
        self.assertEqual(Direction.South, Direction.from_point(Point(0, 1)))

        with self.assertRaises(Exception):
            Direction.from_point(Point(1, 1))

        with self.assertRaises(NotImplementedError):
            Direction.from_point((1, 1))


class TestPoint(unittest.TestCase):
    def test_new_points(self):
        p = Point(-16, 2)
        self.assertEqual(p.x, -16)
        self.assertEqual(p.y, 2)

    def test_point_copy(self):
        p = Point(-16, 2)
        a = p
        b = copy.copy(p)

        a.x = 22
        b.x = 13

        self.assertEqual(22, p.x)
        self.assertEqual(22, a.x)
        self.assertEqual(13, b.x)

    def test_point_clone(self):
        p = Point(-16, 2)
        a = p
        b = p.clone()

        a.x = 22
        b.x = 13

        self.assertEqual(22, p.x)
        self.assertEqual(22, a.x)
        self.assertEqual(13, b.x)

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
        self.assertEqual(Point(-3, 2), Point(-7, 5) // 2)
        self.assertEqual(Point(1, 2), Point(7, 5) % 3)
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

    def test_create_grid_from_callable(self):
        counter = 0

        def foo():
            nonlocal counter
            counter += 1  # noqa: F823
            return counter

        self.assertSequenceEqual([1, 2, 3, 4, 5, 6], Grid(3, 2, foo).cells)

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

        with self.assertRaises(TypeError):
            g[(1, 1)]

        with self.assertRaises(TypeError):
            g[(1, 1)] = "x"

    def test_to_string(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        self.assertEqual("12\nab\n78", str(g))

    def test_get_col(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        self.assertSequenceEqual(["1", "a", "7"], list(g.col(0)))
        self.assertSequenceEqual(["2", "b", "8"], list(g.col(1)))

        with self.assertRaises(ValueError):
            list(g.col(-1))

        with self.assertRaises(ValueError):
            list(g.col(2))

        with self.assertRaises(TypeError):
            list(g.col("1"))

    def test_get_row(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        self.assertSequenceEqual(["1", "2"], list(g.row(0)))
        self.assertSequenceEqual(["a", "b"], list(g.row(1)))
        self.assertSequenceEqual(["7", "8"], list(g.row(2)))

        with self.assertRaises(ValueError):
            list(g.row(-1))

        with self.assertRaises(ValueError):
            list(g.row(3))

        with self.assertRaises(TypeError):
            list(g.row("1"))

    def test_from_input_lines(self):
        g = new_grid_from_input_lines("""hi3\n3$x""".split("\n"))
        self.assertEqual(2, g.row_count())
        self.assertEqual(3, g.col_count())
        self.assertSequenceEqual(["h", "i", "3"], list(g.row(0)))
        self.assertSequenceEqual(["3", "$", "x"], list(g.row(1)))

    def test_iterate_rows(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        vals = [[c for c in row] for row in g.rows()]
        self.assertSequenceEqual(["1", "2"], vals[0])
        self.assertSequenceEqual(["a", "b"], vals[1])
        self.assertSequenceEqual(["7", "8"], vals[2])

    def test_len_is_cell_count(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        self.assertEqual(6, len(g))

    def test_iter_is_flat_cells(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        self.assertSequenceEqual(["1", "2", "a", "b", "7", "8"], list(iter(g)))

    def test_point_in_grid(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        self.assertTrue(Point(0, 0) in g)
        self.assertTrue(Point(1, 0) in g)
        self.assertTrue(Point(0, 2) in g)
        self.assertFalse(Point(2, 0) in g)
        self.assertFalse(Point(1, 3) in g)

    def test_insert_rows(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        g.insert_row(0, ["X", "Y"])
        self.assertSequenceEqual(
            ["X", "Y", "1", "2", "a", "b", "7", "8"], list(iter(g))
        )
        self.assertEqual(4, g.row_count())
        self.assertEqual(2, g.col_count())

        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        g.insert_row(1, ["X", "Y"])
        self.assertSequenceEqual(
            ["1", "2", "X", "Y", "a", "b", "7", "8"], list(iter(g))
        )
        self.assertEqual(4, g.row_count())
        self.assertEqual(2, g.col_count())

        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        g.insert_row(2, ["X", "Y"])
        self.assertSequenceEqual(
            ["1", "2", "a", "b", "X", "Y", "7", "8"], list(iter(g))
        )
        self.assertEqual(4, g.row_count())
        self.assertEqual(2, g.col_count())

        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        g.insert_row(3, ["X", "Y"])
        self.assertSequenceEqual(
            ["1", "2", "a", "b", "7", "8", "X", "Y"], list(iter(g))
        )
        self.assertEqual(4, g.row_count())
        self.assertEqual(2, g.col_count())

    def test_insert_cols(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        g.insert_col(0, ["H", "i", "!"])
        self.assertSequenceEqual(
            ["H", "1", "2", "i", "a", "b", "!", "7", "8"], list(iter(g))
        )
        self.assertEqual(3, g.row_count())
        self.assertEqual(3, g.col_count())

        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        g.insert_col(1, ["H", "i", "!"])
        self.assertSequenceEqual(
            ["1", "H", "2", "a", "i", "b", "7", "!", "8"], list(iter(g))
        )
        self.assertEqual(3, g.row_count())
        self.assertEqual(3, g.col_count())

        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        g.insert_col(2, ["H", "i", "!"])
        self.assertSequenceEqual(
            ["1", "2", "H", "a", "b", "i", "7", "8", "!"], list(iter(g))
        )
        self.assertEqual(3, g.row_count())
        self.assertEqual(3, g.col_count())


class TestPriorityQueue(unittest.TestCase):
    def test_pop_in_min_order(self):
        pq = PriorityQueue()

        for x in [("a", 5), ("b", 2), ("c", 6), ("d", 1), ("e", 3)]:
            pq.add(x[0], x[1])

        self.assertEqual("d", pq.pop())
        self.assertEqual("b", pq.pop())
        self.assertEqual("e", pq.pop())

        pq.add("x", 1)
        pq.add("y", 7)

        self.assertEqual("x", pq.pop())
        self.assertEqual("a", pq.pop())
        self.assertEqual("c", pq.pop())
        self.assertEqual("y", pq.pop())

    def test_init_items(self):
        pq = PriorityQueue([("A", 3), ("B", 1), ("C", 2)])
        self.assertEqual("B", pq.pop())
        self.assertEqual("C", pq.pop())
        self.assertEqual("A", pq.pop())

    def test_is_empty(self):
        pq = PriorityQueue([("A", 2)])
        self.assertFalse(pq.is_empty())

        pq.pop()
        self.assertTrue(pq.is_empty)

        pq.add("B", 5)
        self.assertFalse(pq.is_empty())

    def test_pop_empty(self):
        pq = PriorityQueue()
        with self.assertRaises(Exception):
            pq.pop()


class TestAStar(unittest.TestCase):
    @staticmethod
    def move_cost(grid: Grid[int], a: Point, b: Point) -> float:
        return float(grid[b])

    def test_find_shortest_path(self):
        grid = Grid(
            5,
            4,
            [
                [1, 3, 1, 2, 1],
                [1, 1, 7, 2, 1],
                [1, 4, 5, 1, 1],
                [1, 1, 2, 1, 1],
            ],
        )
        path = astar_search(
            grid,
            Point(1, 1),
            Point(3, 2),
            TestAStar.move_cost,
            lambda a, b: 1.0 * manhattan_distance(a, b),
        )
        self.assertSequenceEqual(
            [
                Point(1, 1),
                Point(0, 1),
                Point(0, 2),
                Point(0, 3),
                Point(1, 3),
                Point(2, 3),
                Point(3, 3),
                Point(3, 2),
            ],
            path,
        )

    def test_find_no_path(self):
        grid = Grid(2, 1, [[1, 1]])
        path = astar_search(
            grid,
            Point(0, 0),
            Point(1, 0),
            lambda grid, a, b: None,
            manhattan_distance,
        )
        self.assertIsNone(path)


class TestBFS(unittest.TestCase):
    class FindReachable(BFS[int]):
        def __init__(self, grid: Grid[int], start_pos: Point, target_pos: Point):
            super().__init__(grid, start_pos)
            self.target_reached = False
            self.target_pos = target_pos

        def on_visit(
            self, from_cell: int, to_cell: int, to_pos: Point, to_dir: Direction
        ) -> None:
            if to_pos == self.target_pos:
                self.target_reached = True
            else:
                if to_cell == 0:
                    self.add_frontier(to_pos)

    def test_find_shortest_dist(self):
        grid = Grid(
            5,
            4,
            [
                [0, 1, 0, 0, 0],
                [0, 1, 0, 1, 0],
                [1, 0, 1, 1, 0],
                [0, 0, 1, 0, 0],
            ],
        )

        visitor = TestBFS.FindReachable(grid, Point(0, 1), Point(3, 3))
        visitor.run()

        self.assertFalse(visitor.target_reached)

        visitor = TestBFS.FindReachable(grid, Point(2, 1), Point(3, 3))
        visitor.run()

        self.assertTrue(visitor.target_reached)

    def create_solver_with_bad_args(self):
        with self.assertRaises(TypeError):
            TestBFS.FindReachable(None, Point(0, 0))


class TestCountIf(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(0, count_if([], lambda x: False))
        self.assertEqual(0, count_if(iter([]), lambda x: False))

    def test_count(self):
        self.assertEqual(2, count_if([1, 2, 3, 4], lambda x: x % 2 == 0))

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            count_if(1)


class TestFirstAndLast(unittest.TestCase):
    def test_one_item_list(self):
        self.assertEqual((10, 10), first_and_last([10]))

    def test_multi_item_list(self):
        self.assertEqual((13, 3), first_and_last([13, 3]))
        self.assertEqual((81, "a"), first_and_last([81, "a"]))

    def test_empty_list_throws_exception(self):
        self.assertRaises(StopIteration, lambda: first_and_last([]))

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            first_and_last(2)


class TestUnzip(unittest.TestCase):
    def test_unzip_2(self):
        A = [5, 8, 10]
        B = [-2, 12, "b"]
        self.assertEqual((A, B), unzip([(5, -2), (8, 12), (10, "b")]))

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            unzip(1)


class TestUtilsModule(unittest.TestCase):
    def test_load_input(self):
        input = load_input(0, 0)
        self.assertEqual(input, ["hello", "123"])


class TestAllPairs(unittest.TestCase):
    def test_empty_list(self):
        self.assertSequenceEqual([], list(all_pairs([])))

    def test_single_element_list(self):
        self.assertSequenceEqual([], list(all_pairs([1])))

    def test_double_element_list(self):
        self.assertSequenceEqual([(1, 2)], list(all_pairs([1, 2])))

    def test_multi_element_list(self):
        self.assertSequenceEqual(
            [("a", "b"), ("a", "c"), ("a", "d"), ("b", "c"), ("b", "d"), ("c", "d")],
            list(all_pairs(["a", "b", "c", "d"])),
        )

    def test_not_list(self):
        with self.assertRaises(TypeError):
            list(all_pairs(5))


class TestCombinations(unittest.TestCase):
    def test_k(self):
        self.assertSequenceEqual(
            [[1], [2], [3], [4]], list(combinations(1, [1, 2, 3, 4]))
        )
        self.assertSequenceEqual(
            [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]],
            list(combinations(2, [1, 2, 3, 4])),
        )
        self.assertSequenceEqual(
            [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]],
            list(combinations(3, [1, 2, 3, 4])),
        )
        self.assertSequenceEqual(
            [[1, 2, 3, 4]],
            list(combinations(4, [1, 2, 3, 4])),
        )

    def test_bad_k(self):
        with self.assertRaises(ValueError):
            list(combinations(0, [1, 2, 3, 4]))
        with self.assertRaises(ValueError):
            list(combinations(5, [1, 2, 3, 4]))

    def test_bad_types(self):
        with self.assertRaises(TypeError):
            list(combinations("2", [1, 2, 3, 4]))
        with self.assertRaises(TypeError):
            list(combinations(5, "abc"))


if __name__ == "__main__":
    unittest.main()
