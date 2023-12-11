#!/usr/bin/env python3
import unittest

from advent.solver import AdventDaySolver, AdventDayTestCase, solver_main
from advent.utils import Direction, count_if, Grid, Point, new_grid_from_input_lines


def parse_input(input_lines):
    def is_neighbor_a_pipe(grid, pt, dir):
        neighbor_pt = pt + dir.to_point()
        return grid.check_in_bounds(neighbor_pt) and grid[neighbor_pt] != "."

    char_grid = new_grid_from_input_lines(input_lines)
    tile_rows = []

    for char_row in char_grid.rows():
        row = []

        for c in char_row:
            if c == "|":
                row.append(Tile(north_edge=True, south_edge=True))
            elif c == "-":
                row.append(Tile(east_edge=True, west_edge=True))
            elif c == "L":
                row.append(Tile(north_edge=True, east_edge=True))
            elif c == "J":
                row.append(Tile(north_edge=True, west_edge=True))
            elif c == "7":
                row.append(Tile(south_edge=True, west_edge=True))
            elif c == "F":
                row.append(Tile(south_edge=True, east_edge=True))
            elif c == ".":
                row.append(Tile())
            elif c == "S":
                pt = Point(char_row.x, char_row.row)
                edges = [is_neighbor_a_pipe(char_grid, pt, dir) for dir in Direction.cardinal_dirs()]
                row.append(
                    Tile(
                        east_edge=edges[Direction.East],
                        north_edge=edges[Direction.North],
                        west_edge=edges[Direction.West],
                        south_edge=edges[Direction.South],
                        is_start=True,
                    )
                )

                start_pos = pt
            else:
                raise Exception(f"Unknown tile {c} at {char_row.x}, {char_row.row}")

        tile_rows.append(row)

    return (Grid(char_grid.x_count, char_grid.y_count, tile_rows), start_pos)


def is_valid_pos(grid, x, y):
    return y < len(grid) and x < len(grid[0])


def tile(grid, x, y):
    assert is_valid_pos(grid, x, y)
    return grid[y][x]


class Tile:
    def __init__(
        self,
        east_edge=False,
        north_edge=False,
        west_edge=False,
        south_edge=False,
        is_start=False,
    ):
        self.edges = [False, False, False, False]
        self.is_start = is_start
        self.visited = False

        self.set_edge(Direction.East, east_edge)
        self.set_edge(Direction.North, north_edge)
        self.set_edge(Direction.West, west_edge)
        self.set_edge(Direction.South, south_edge)

        edges = self.edge_count()
        if edges != 0 and edges != 2:
            raise Exception(f"wrong number of edges {edges}")

    def set_edge(self, dir: Direction, value: bool) -> None:
        self.edges[int(dir)] = value

    def edge(self, dir: Direction) -> bool:
        return self.edges[int(dir)]

    def edge_count(self) -> int:
        return count_if(Direction.cardinal_dirs(), lambda dir: self.edge(dir))

    def __str__(self):
        if self.is_start:
            return "S"
        elif self.edge(Direction.North) and self.edge(Direction.South):
            return "|"
        elif self.edge(Direction.East) and self.edge(Direction.West):
            return "-"
        elif self.edge(Direction.North) and self.edge(Direction.East):
            return "L"
        elif self.edge(Direction.North) and self.edge(Direction.West):
            return "J"
        elif self.edge(Direction.South) and self.edge(Direction.West):
            return "7"
        elif self.edge(Direction.South) and self.edge(Direction.East):
            return "F"
        else:
            return "."


def find_furthest_point(grid, start):
    assert is_valid_pos(grid, start[0], start[1])
    assert tile(grid, start[0], start[1]).edge_count() > 0

    # Because this is fully connected cycle, use BFS to keep visiting nodes
    # until we find an already visited node. The iteration count is the maximum
    # distance.
    neighbors = [start]

    while len(neighbors) > 0:
        pass


class Solver(
    AdventDaySolver, day=10, year=2023, name="Pipe Maze", solution=(None, None)
):
    def __init__(self, input):
        super().__init__(input)
        self.grid, self.start = parse_input(input)
        print(self.grid)

    def solve(self):
        return (find_furthest_point(self.grid, self.start), None)


class Tests(AdventDayTestCase):
    def setUp(self):
        super().setUp(Solver)

    def test_sample(self):
        d = self._create_sample_solver(
            """.....
.S-7.
.|.|.
.L-J.
....."""
        )
        s = d.solve()

        self.assertEqual(None, s[0])
        self.assertEqual(None, s[1])


if __name__ == "__main__":
    solver_main(unittest.TestProgram(exit=False), Solver)
