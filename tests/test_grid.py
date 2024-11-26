from oatmeal import Grid, Point

import unittest


# TODO:


class TestGrid(unittest.TestCase):
    def test_create_grid_from_default_value(self):
        g = Grid(2, 3, "$")

        self.assertEqual(g.x_count, 2)
        self.assertEqual(g.col_count, 2)

        self.assertEqual(g.y_count, 3)
        self.assertEqual(g.row_count, 3)

        self.assertEqual(g[Point(0, 0)], "$")
        self.assertEqual(g[Point(1, 0)], "$")
        self.assertEqual(g[Point(0, 1)], "$")
        self.assertEqual(g[Point(1, 1)], "$")
        self.assertEqual(g[Point(0, 2)], "$")
        self.assertEqual(g[Point(1, 2)], "$")

    def test_create_grid_from_callable(self):
        def foo(x: int, y: int) -> int:
            return y * 10 + x

        g = Grid(3, 2, foo)

        self.assertEqual(g.x_count, 3)
        self.assertEqual(g.y_count, 2)

        self.assertEqual(g[Point(0, 0)], 0)
        self.assertEqual(g[Point(1, 0)], 1)
        self.assertEqual(g[Point(2, 0)], 2)
        self.assertEqual(g[Point(0, 1)], 10)
        self.assertEqual(g[Point(1, 1)], 11)
        self.assertEqual(g[Point(2, 1)], 12)

    def test_iterate_cells_in_grid(self):
        def foo(x: int, y: int) -> int:
            return y * 10 + x

        g = Grid(3, 2, foo)
        self.assertSequenceEqual([0, 1, 2, 10, 11, 12], [x for x in g])

    def test_set_cells_in_grid(self):
        g = Grid(3, 2, 0)

        g[Point(0, 0)] = 200
        g[Point(1, 0)] = 211
        g[Point(2, 0)] = 222
        g[Point(0, 1)] = 400
        g[Point(1, 1)] = 411
        g[Point(2, 1)] = 422

        self.assertSequenceEqual([200, 211, 222, 400, 411, 422], list(g))

    def test_create_grid_from_2d_array(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        self.assertEqual(2, g.x_count)
        self.assertEqual(3, g.y_count)
        self.assertSequenceEqual(["1", "2", "a", "b", "7", "8"], list(g))

    def test_out_of_bounds_access_raises_exception(self):
        g = Grid(3, 2, 0)

        with self.assertRaises(IndexError):
            g[Point(-1, 0)]

        with self.assertRaises(IndexError):
            g[Point(0, -1)]

        with self.assertRaises(IndexError):
            g[Point(-1, -1)]

        with self.assertRaises(IndexError):
            g[Point(3, 0)]

        with self.assertRaises(IndexError):
            g[Point(0, 2)]

        with self.assertRaises(IndexError):
            g[Point(2, 3)]
