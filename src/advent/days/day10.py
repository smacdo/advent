#!/usr/bin/env python3
from typing import Iterable, Optional, Tuple
import unittest

from advent.solver import AdventDaySolver, AdventDayTestCase, solver_main
from advent.utils import (
    Direction,
    count_if,
    Grid,
    Point,
    new_grid_from_input_lines,
    BFS,
)


class ConnectionSet:
    def __init__(self, east=False, north=False, west=False, south=False):
        self.edges = [False, False, False, False]

        self.set(Direction.East, east)
        self.set(Direction.North, north)
        self.set(Direction.West, west)
        self.set(Direction.South, south)

    def clone(self) -> "ConnectionSet":
        return ConnectionSet(
            east=self.edges[Direction.East],
            north=self.edges[Direction.North],
            west=self.edges[Direction.West],
            south=self.edges[Direction.South],
        )

    def set(self, dir: Direction, value: bool = True) -> None:
        self.edges[int(dir)] = value

    def has(self, dir: Direction) -> bool:
        return self.edges[int(dir)]

    def count(self) -> int:
        return count_if(Direction.cardinal_dirs(), lambda dir: self.has(dir))


TILE_CONNECTIONS = {
    "|": ConnectionSet(north=True, south=True),
    "-": ConnectionSet(east=True, west=True),
    "L": ConnectionSet(north=True, east=True),
    "J": ConnectionSet(north=True, west=True),
    "7": ConnectionSet(south=True, west=True),
    "F": ConnectionSet(south=True, east=True),
    ".": ConnectionSet(),
}


class Tile:
    def __init__(
        self,
        connections: Optional[ConnectionSet] = None,
        is_start: bool = False,
    ):
        self.is_start = is_start
        self.part_of_main_loop = False
        self.distance = 0
        self.filled = False
        self.connections = connections if connections is not None else ConnectionSet()

        edges = self.connections.count()
        if edges != 0 and edges != 2:
            raise Exception(f"wrong number of edges {edges}")

    def __str__(self):
        if self.filled:
            return "X"
        elif self.connections.has(Direction.North) and self.connections.has(
            Direction.South
        ):
            return "|"
        elif self.connections.has(Direction.East) and self.connections.has(
            Direction.West
        ):
            return "-"
        elif self.connections.has(Direction.North) and self.connections.has(
            Direction.East
        ):
            return "L"
        elif self.connections.has(Direction.North) and self.connections.has(
            Direction.West
        ):
            return "J"
        elif self.connections.has(Direction.South) and self.connections.has(
            Direction.West
        ):
            return "7"
        elif self.connections.has(Direction.South) and self.connections.has(
            Direction.East
        ):
            return "F"
        else:
            return "."


def parse_input(input_lines: Iterable[Iterable[str]]) -> Tuple[Grid[Tile], Point]:
    def does_neighbor_connect_to_me(grid: Grid[str], pt: Point, dir: Direction) -> bool:
        neighbor_pt = pt + dir.to_point()
        if grid.check_in_bounds(neighbor_pt) and grid[neighbor_pt] in TILE_CONNECTIONS:
            connections = TILE_CONNECTIONS[grid[neighbor_pt]]
            return connections.has(dir.reverse())
        else:
            return False

    char_grid = new_grid_from_input_lines(input_lines)
    tile_rows = []

    for y, char_row in enumerate(char_grid.rows()):
        row: list[Tile] = []

        for x, c in enumerate(char_row):
            if c in TILE_CONNECTIONS:
                row.append(Tile(connections=TILE_CONNECTIONS[c].clone()))
            elif c == "S":
                pt = Point(x, y)
                connections = ConnectionSet()

                for dir in Direction.cardinal_dirs():
                    if does_neighbor_connect_to_me(char_grid, pt, dir):
                        connections.set(dir)

                row.append(
                    Tile(
                        connections=connections,
                        is_start=True,
                    )
                )

                start_pos = pt
            else:
                raise Exception(f"Unknown tile {c} at {char_row.x}, {char_row.row}")

        tile_rows.append(row)

    return (Grid(char_grid.x_count, char_grid.y_count, tile_rows), start_pos)


class FindFurthestDistance(BFS[Tile]):
    __slots__ = "max_distance"
    max_distance: int

    def __init__(self, grid: Grid[Tile], start_pos: Point):
        super().__init__(grid, start_pos)
        self.max_distance = 0

    def on_visit(
        self, from_cell: Tile, to_cell: Tile, to_pos: Point, to_dir: Direction
    ) -> None:
        if from_cell.connections.has(to_dir):
            assert self.grid[to_pos].connections.has(to_dir.reverse())
            to_cell.distance = from_cell.distance + 1
            self.max_distance = max(self.max_distance, to_cell.distance)

            self.add_frontier(to_pos)


class MarkMainLoop(BFS[Tile]):
    def on_visit(
        self, from_cell: Tile, to_cell: Tile, to_pos: Point, to_dir: Direction
    ) -> None:
        from_cell.part_of_main_loop = True

        if from_cell.connections.has(to_dir):
            self.add_frontier(to_pos)


def find_area_enclosed(grid: Grid[Tile], start: Point) -> int:
    # Mark all pipes belonging to the main loop.
    MarkMainLoop(grid, start).run()

    # Count the number of points that are enclosed by scanning each line left to
    # right. Any point that crosses an odd number of lines to the left is inside
    # the enclosure, and even times is outside.
    #
    # This is made trickier with the straight lines, but only "|", "FJ" and "L7"
    # form vertical lines that separate the interior region from exterior. The
    # other segments like "F7" or "LJ" do not segment the interior from exterior.
    #
    # More info on the algorithm:
    # https://en.wikipedia.org/wiki/Point_in_polygon#Ray_casting_algorithm
    for y in range(grid.y_count):
        wall_count = 0
        prev_corner = None

        for x in range(grid.x_count):
            pos = Point(x, y)
            tile = grid[pos]
            tile_str = str(tile)

            if tile.part_of_main_loop:
                # Tile forms the walls of the main loop.
                if tile_str == "|":
                    wall_count += 1
                    prev_corner = None
                elif tile_str == "F" or tile_str == "L":
                    prev_corner = tile_str
                elif tile_str == "J":
                    if prev_corner == "F":
                        wall_count += 1
                    else:
                        prev_corner = None
                elif tile_str == "7":
                    if prev_corner == "L":
                        wall_count += 1
                    else:
                        prev_corner = None
                elif tile_str == "-":
                    # ignore a horizontal wall.
                    pass
                else:
                    raise Exception(f"unexpected tile {tile_str} at {x}, {y}:\n{grid}")
            else:
                # A tile that lies inside or outside the main loop but is not
                # part of the main loop.
                if wall_count > 0 and wall_count % 2 == 1:
                    tile.filled = True

    # Return the number of counted interior tiles.
    return count_if(grid, lambda x: x.filled)


class Solver(
    AdventDaySolver, day=10, year=2023, name="Pipe Maze", solution=(6870, 287)
):
    def __init__(self, input):
        super().__init__(input)
        self.grid, self.start = parse_input(input)

    def solve(self):
        distance_finder = FindFurthestDistance(self.grid, self.start)
        distance_finder.run()

        return (
            distance_finder.max_distance,
            find_area_enclosed(self.grid, self.start),
        )


class Tests(AdventDayTestCase):
    def setUp(self):
        super().setUp(Solver)

    def test_sample_1(self):
        d = self._create_sample_solver(
            """.....
.S-7.
.|.|.
.L-J.
....."""
        )
        s = d.solve()
        self.assertEqual(4, s[0])

    def test_sample_2(self):
        d = self._create_sample_solver(
            """..F7.
.FJ|.
SJ.L7
|F--J
LJ..."""
        )
        s = d.solve()
        self.assertEqual(8, s[0])

    def test_sample_3(self):
        d = self._create_sample_solver(
            """...........
.S-------7.
.|F-----7|.
.||.....||.
.||.....||.
.|L-7.F-J|.
.|..|.|..|.
.L--J.L--J.
..........."""
        )
        s = d.solve()
        self.assertEqual(4, s[1])


if __name__ == "__main__":
    solver_main(unittest.TestProgram(exit=False), Solver)
