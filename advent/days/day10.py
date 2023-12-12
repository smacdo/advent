#!/usr/bin/env python3
from typing import Iterable, Optional, Tuple
import unittest

from advent.solver import AdventDaySolver, AdventDayTestCase, solver_main
from advent.utils import Direction, count_if, Grid, Point, new_grid_from_input_lines


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
        self.visited = False
        self.distance = 0
        self.filled = False
        self.connections = connections if connections is not None else ConnectionSet()

        edges = self.connections.count()
        if edges != 0 and edges != 2:
            raise Exception(f"wrong number of edges {edges}")

    def __str__(self):
        if self.filled:
            return "X"

        if self.is_start:
            return "S"
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


def find_furthest_distance(grid: Grid[Tile], start: Point) -> int:
    assert grid.check_in_bounds(start)
    assert grid[start].connections.count() > 0

    # Because this is fully connected cycle, use BFS to keep visiting nodes
    # until we find an already visited node. The iteration count is the maximum
    # distance.
    neighbors = [start]
    max_distance = 0

    while len(neighbors) > 0:
        node_pos = neighbors.pop(0)
        node = grid[node_pos]
        node.visited = True

        for dir in Direction.cardinal_dirs():
            if node.connections.has(dir):
                to_pos = node_pos + dir.to_point()

                assert grid.check_in_bounds(to_pos)
                ##print(
                ##    f"{node_pos} -> {to_pos} connected {dir} -> {dir.reverse()}?  {grid[to_pos].connections.has(dir.reverse())}"
                ##)
                assert grid[to_pos].connections.has(dir.reverse())

                to_node = grid[to_pos]

                if not to_node.visited:
                    to_node.visited = True
                    to_node.distance = node.distance + 1

                    neighbors.append(to_pos)

                    max_distance = max(max_distance, to_node.distance)

    return max_distance


def mark_main_loop(grid: Grid[Tile], start: Point) -> None:
    # Clear visited state.
    for tile in grid:
        tile.visited = False

    # TODO: Can we make a BFS helper for grid?
    frontier = [start]

    while len(frontier) > 0:
        node_pos = frontier.pop(0)
        node = grid[node_pos]
        node.visited = True
        node.part_of_main_loop = True

        for dir in Direction.cardinal_dirs():
            neighbor_pos = node_pos + dir.to_point()

            if not grid.check_in_bounds(neighbor_pos) or grid[neighbor_pos].visited:
                continue

            # neighbor = grid[neighbor_pos]

            if node.connections.has(dir):
                frontier.append(neighbor_pos)


def flood_fill(grid: Grid[Tile], start: Point):
    print(f"START: {start}")
    # Clear visited state.
    for tile in grid:
        tile.visited = False

    # TODO: Can we make a BFS helper for grid?
    frontier = [start]

    while len(frontier) > 0:
        node_pos = frontier.pop(0)
        node = grid[node_pos]
        node.visited = True
        node.filled = True

        for dir in Direction.cardinal_dirs():
            neighbor_pos = node_pos + dir.to_point()

            if not grid.check_in_bounds(neighbor_pos) or grid[neighbor_pos].visited:
                continue

            neighbor = grid[neighbor_pos]

            if not neighbor.part_of_main_loop:
                frontier.append(neighbor_pos)


def find_area_enclosed(grid: Grid[Tile], start: Point) -> int:
    # Mark all pipes belonging to the main loop.
    mark_main_loop(grid, start)

    # Clear visited state.
    for tile in grid:
        tile.visited = False

    # Scan top down, left to right. Anytime a vertical way is encountered start
    # flood filling until another vertical wall from the main loop is found.
    tile_count = 0

    for y in range(grid.y_count):
        is_inside = False

        for x in range(grid.x_count):
            pt = Point(x, y)
            t = grid[pt]

            # if not t.part_of_main_loop:
            #    continue
            if t.filled:
                continue

            s = str(t)

            if is_inside:
                is_inside = False
            elif t.part_of_main_loop and (s == "-" or "F"):
                is_inside = True
            elif t.part_of_main_loop and (s == "|" or s == "7" or s == "J"):
                fill_start = pt + Point(1, 0)

                if grid.check_in_bounds(fill_start):
                    fill_tile = grid[fill_start]

                    if (
                        not fill_tile.part_of_main_loop
                        and fill_tile.connections.count() == 0
                    ):
                        flood_fill(grid, fill_start)
                # print(f"VISIT {x}, {y} count {tile_count}")

    # Count number of flood filled tiles
    # TODO: count_if
    count = 0
    for tile in grid:
        if tile.filled:
            count += 1

    print(f"\n\n{grid}")
    return tile_count


class Solver(
    AdventDaySolver, day=10, year=2023, name="Pipe Maze", solution=(None, None)
):
    def __init__(self, input):
        super().__init__(input)
        self.grid, self.start = parse_input(input)
        # print(self.grid)

    def solve(self):
        return (
            find_furthest_distance(self.grid, self.start),
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
