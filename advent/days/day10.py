#!/usr/bin/env python3
import unittest

from advent.solver import AdventDaySolver, AdventDayTestCase, solver_main
from advent.utils import Direction


def parse_input(input_lines):
    char_grid = []

    for line in input_lines:
        char_grid.append([c for c in line])

    grid = []
    start_pos = None

    for y, line in enumerate(input_lines):
        row = []

        for x, c in enumerate(line):
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
                # TODO: Detect edges for start.
                east_edge = (
                    is_valid_pos(char_grid, x + 1, y) and char_grid[y][x + 1] != "."
                )
                north_edge = (
                    is_valid_pos(char_grid, x, y - 1) and char_grid[y - 1][x] != "."
                )
                west_edge = (
                    is_valid_pos(char_grid, x - 1, y) and char_grid[y][x - 1] != "."
                )
                south_edge = (
                    is_valid_pos(char_grid, x, y + 1) and char_grid[y + 1][x] != "."
                )

                row.append(
                    Tile(
                        east_edge=east_edge,
                        north_edge=north_edge,
                        west_edge=west_edge,
                        south_edge=south_edge,
                        is_start=True,
                    )
                )

                start_pos = (x, y)
            else:
                raise Exception(f"Unknown tile {c} at {x}, {y}")

        grid.append(row)

    return (grid, start_pos)


def print_grid(grid):
    for y, row in enumerate(grid):
        for x, tile in enumerate(row):
            print((str(tile)), end="")
        print("")


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
        # TODO: `count_if`
        edges = 0
        edges += 1 if self.edge(Direction.East) else 0
        edges += 1 if self.edge(Direction.North) else 0
        edges += 1 if self.edge(Direction.West) else 0
        edges += 1 if self.edge(Direction.South) else 0
        return edges

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
        print_grid(self.grid)

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
