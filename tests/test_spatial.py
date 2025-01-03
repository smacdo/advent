from advent.spatial import (
    ConnectedTile,
    Direction,
    Grid,
    BFS,
    PriorityQueue,
    astar_search,
    manhattan_distance,
)
from advent.utils import new_grid_from_input_lines
from oatmeal import Point

import unittest


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

        with self.assertRaises(ValueError):
            Direction.from_point(Point(1, 1))


class TestGrid(unittest.TestCase):
    def test_create_grid_from_default_value(self):
        g = Grid(2, 3, "f")
        self.assertEqual(2, g.x_count)
        self.assertEqual(3, g.y_count)
        self.assertSequenceEqual(["f", "f", "f", "f", "f", "f"], g.cells)

    def test_create_grid_from_callable(self):
        def foo(x: int, y: int):
            return y * 10 + x

        self.assertSequenceEqual([0, 1, 2, 10, 11, 12], Grid(3, 2, foo).cells)

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

    def test_get_col(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        self.assertSequenceEqual(["1", "a", "7"], list(g.col(0)))
        self.assertSequenceEqual(["2", "b", "8"], list(g.col(1)))

        with self.assertRaises(ValueError):
            list(g.col(-1))

        with self.assertRaises(ValueError):
            list(g.col(2))

    def test_get_row(self):
        g = Grid(2, 3, [["1", "2"], ["a", "b"], ["7", "8"]])
        self.assertSequenceEqual(["1", "2"], list(g.row(0)))
        self.assertSequenceEqual(["a", "b"], list(g.row(1)))
        self.assertSequenceEqual(["7", "8"], list(g.row(2)))

        with self.assertRaises(ValueError):
            list(g.row(-1))

        with self.assertRaises(ValueError):
            list(g.row(3))

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


class TestConnectedTile(unittest.TestCase):
    def test_init_no_connections(self):
        t = ConnectedTile()
        self.assertEqual(t.cost, 0)

    def test_init_no_cost(self):
        t = ConnectedTile()
        self.assertEqual(t.cost, 0)

    def test_init_set_cost_and_connected_tile(self):
        t = ConnectedTile(cost=30)
        self.assertEqual(t.cost, 30)

        t = ConnectedTile(Direction.North, cost=-541)
        self.assertEqual(t.cost, -541)
        self.assertNotEqual(t.edge_connections, 0)

        self.assertTrue(t.edge(Direction.North))
        self.assertFalse(t.edge(Direction.South))
        self.assertFalse(t.edge(Direction.East))
        self.assertFalse(t.edge(Direction.West))

        t = ConnectedTile(Direction.South, Direction.East, cost=-541)
        self.assertEqual(t.cost, -541)

        self.assertFalse(t.edge(Direction.North))
        self.assertTrue(t.edge(Direction.South))
        self.assertTrue(t.edge(Direction.East))
        self.assertFalse(t.edge(Direction.West))

    def test_set_edge_true(self):
        t = ConnectedTile()
        t.set_edge(True, Direction.West)

        self.assertFalse(t.edge(Direction.North))
        self.assertFalse(t.edge(Direction.South))
        self.assertFalse(t.edge(Direction.East))
        self.assertTrue(t.edge(Direction.West))

        t.set_edge(True, Direction.North)

        self.assertTrue(t.edge(Direction.North))
        self.assertFalse(t.edge(Direction.South))
        self.assertFalse(t.edge(Direction.East))
        self.assertTrue(t.edge(Direction.West))

        t.set_edge(True, Direction.East)
        t.set_edge(True, Direction.South)

        self.assertTrue(t.edge(Direction.North))
        self.assertTrue(t.edge(Direction.South))
        self.assertTrue(t.edge(Direction.East))
        self.assertTrue(t.edge(Direction.West))

    def test_set_edge_false(self):
        t = ConnectedTile(Direction.North, Direction.South, Direction.East)

        self.assertTrue(t.edge(Direction.North))
        self.assertTrue(t.edge(Direction.South))
        self.assertTrue(t.edge(Direction.East))
        self.assertFalse(t.edge(Direction.West))

        t.set_edge(False, Direction.North)

        self.assertFalse(t.edge(Direction.North))
        self.assertTrue(t.edge(Direction.South))
        self.assertTrue(t.edge(Direction.East))
        self.assertFalse(t.edge(Direction.West))

        t.set_edge(False, Direction.South)
        t.set_edge(False, Direction.East)

        self.assertFalse(t.edge(Direction.North))
        self.assertFalse(t.edge(Direction.South))
        self.assertFalse(t.edge(Direction.East))
        self.assertFalse(t.edge(Direction.West))

    def test_set_edges_true(self):
        t = ConnectedTile()
        t.set_edges(True, Direction.West)

        self.assertFalse(t.edge(Direction.North))
        self.assertFalse(t.edge(Direction.South))
        self.assertFalse(t.edge(Direction.East))
        self.assertTrue(t.edge(Direction.West))

        t.set_edges(True, Direction.North)

        self.assertTrue(t.edge(Direction.North))
        self.assertFalse(t.edge(Direction.South))
        self.assertFalse(t.edge(Direction.East))
        self.assertTrue(t.edge(Direction.West))

        t.set_edges(True, Direction.East, Direction.South)

        self.assertTrue(t.edge(Direction.North))
        self.assertTrue(t.edge(Direction.South))
        self.assertTrue(t.edge(Direction.East))
        self.assertTrue(t.edge(Direction.West))

    def test_set_edges_false(self):
        t = ConnectedTile(Direction.North, Direction.South, Direction.East)

        self.assertTrue(t.edge(Direction.North))
        self.assertTrue(t.edge(Direction.South))
        self.assertTrue(t.edge(Direction.East))
        self.assertFalse(t.edge(Direction.West))

        t.set_edges(False, Direction.North)

        self.assertFalse(t.edge(Direction.North))
        self.assertTrue(t.edge(Direction.South))
        self.assertTrue(t.edge(Direction.East))
        self.assertFalse(t.edge(Direction.West))

        t.set_edges(False, Direction.South, Direction.West, Direction.East)

        self.assertFalse(t.edge(Direction.North))
        self.assertFalse(t.edge(Direction.South))
        self.assertFalse(t.edge(Direction.East))
        self.assertFalse(t.edge(Direction.West))

    def test_edge_count(self):
        t = ConnectedTile(Direction.North, Direction.South, Direction.East)
        self.assertEqual(t.edge_count(), 3)

        t.set_edges(False, Direction.South, Direction.West, Direction.East)
        self.assertEqual(t.edge_count(), 1)

        t.set_edge(True, Direction.West)
        self.assertEqual(t.edge_count(), 2)

    def test_all_edges_no_params(self):
        t = ConnectedTile()
        self.assertFalse(t.all_edges())

        t = ConnectedTile(Direction.West)
        self.assertFalse(t.all_edges())

        t = ConnectedTile(
            Direction.West, Direction.East, Direction.South, Direction.North
        )
        self.assertTrue(t.all_edges())

    def test_all_edges_one_param(self):
        t = ConnectedTile()
        self.assertFalse(t.all_edges(Direction.West))

        t = ConnectedTile(Direction.West)
        self.assertTrue(t.all_edges(Direction.West))

        t = ConnectedTile(
            Direction.West, Direction.East, Direction.South, Direction.North
        )
        self.assertTrue(t.all_edges(Direction.West))

    def test_all_edges_multi_param(self):
        t = ConnectedTile()
        self.assertFalse(t.all_edges(Direction.West, Direction.East))

        t = ConnectedTile(Direction.West)
        self.assertFalse(t.all_edges(Direction.West, Direction.East))

        t = ConnectedTile(
            Direction.West, Direction.East, Direction.South, Direction.North
        )
        self.assertTrue(t.all_edges(Direction.West, Direction.East))

    def test_any_edges_no_params(self):
        t = ConnectedTile()
        self.assertFalse(t.any_edge())

        t = ConnectedTile(Direction.West)
        self.assertTrue(t.any_edge())

        t = ConnectedTile(
            Direction.West, Direction.East, Direction.South, Direction.North
        )
        self.assertTrue(t.any_edge())

    def test_any_edges_one_param(self):
        t = ConnectedTile()
        self.assertFalse(t.any_edge(Direction.West))

        t = ConnectedTile(Direction.West)
        self.assertTrue(t.any_edge(Direction.West))
        self.assertFalse(t.any_edge(Direction.South))

        t = ConnectedTile(
            Direction.West, Direction.East, Direction.South, Direction.North
        )
        self.assertTrue(t.any_edge(Direction.West))
        self.assertTrue(t.any_edge(Direction.South))

    def test_any_edges_multi_param(self):
        t = ConnectedTile()
        self.assertFalse(t.any_edge(Direction.West))

        t = ConnectedTile(Direction.West)
        self.assertTrue(t.any_edge(Direction.West, Direction.South))
        self.assertFalse(t.any_edge(Direction.North, Direction.East))

        t = ConnectedTile(
            Direction.West, Direction.East, Direction.South, Direction.North
        )
        self.assertTrue(t.any_edge(Direction.West, Direction.South))
        self.assertTrue(t.any_edge(Direction.North, Direction.East))


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
            path,  # type: ignore
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
            TestBFS.FindReachable(None, Point(0, 0), Point(0, 0))  # type: ignore
