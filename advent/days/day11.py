#!/usr/bin/env python3
from typing import Iterable, Optional
import unittest

from advent.solver import AdventDaySolver, AdventDayTestCase, solver_main
from advent.utils import (
    Grid,
    new_grid_from_input_lines,
    count_if,
    all_pairs,
    astar_search,
    manhattan_distance,
    Point,
)


class Tile:
    __slots__ = ("galaxy_id", "cost")
    galaxy_id: Optional[int]
    cost: int

    def __init__(self):
        self.galaxy_id = None
        self.cost = 1

    def __str__(self):
        return f"{self.cost}"


def parse_input(lines: Iterable[Iterable[str]]) -> Grid[Tile]:
    char_grid = new_grid_from_input_lines(lines)
    tile_grid: Grid[Tile] = Grid(char_grid.x_count, char_grid.y_count, Tile())
    next_galaxy_id = 0

    for y in range(char_grid.y_count):
        for x, c in enumerate(char_grid.row(y)):
            pos = Point(x, y)

            if c == "#":
                tile_grid[pos].galaxy_id = next_galaxy_id
                next_galaxy_id += 1

    return tile_grid


def apply_space_expansion(grid: Grid[Tile]) -> None:
    # Check all columns to see if they are totally empty, and if so apply an
    # expansion cost.
    for i in range(grid.col_count()):
        has_galaxies = count_if(grid.col(i), lambda x: x.galaxy_id is not None) > 0

        if not has_galaxies:
            for c in grid.col(i):
                c.cost *= 2

    for i in range(grid.row_count()):
        has_galaxies = count_if(grid.row(i), lambda x: x.galaxy_id is not None) > 0

        if not has_galaxies:
            for c in grid.row(i):
                c.cost *= 2

    print(grid)


class Solver(AdventDaySolver, day=11, year=2023, name="", solution=(None, None)):
    def __init__(self, input: Iterable[Iterable[str]]):
        super().__init__(input)
        self.tile_grid = parse_input(input)
        apply_space_expansion(self.tile_grid)

    def solve(self):
        return (self.solve_1(), None)

    def solve_1(self) -> int:
        # Collect all the galaxies and generate a pairing between all galaxies
        # without repeats.
        galaxy_tiles: dict[int, Point] = dict()

        for y in range(self.tile_grid.y_count):
            for x, tile in enumerate(self.tile_grid.row(y)):
                if tile.galaxy_id is not None:
                    galaxy_tiles[tile.galaxy_id] = Point(x, y)

        galaxies = [
            tile.galaxy_id for tile in self.tile_grid if tile.galaxy_id is not None
        ]
        total_cost = 0

        for a, b in all_pairs(galaxies):
            path = astar_search(
                self.tile_grid,
                galaxy_tiles[a],
                galaxy_tiles[b],
                lambda grid, ta, tb: grid[tb].cost,
                manhattan_distance,
            )

            if path is None:
                raise Exception("path should be valid")

            cost = sum(self.tile_grid[pos].cost for pos in path)
            total_cost += cost
            print(f"{a} -> {b}: {cost}")

        return total_cost


class Tests(AdventDayTestCase):
    def setUp(self):
        super().setUp(Solver)

    def test_sample(self):
        d = self._create_sample_solver(
            """....#........
.........#...
#............
.............
.............
........#....
.#...........
............#
.............
.............
.........#...
#....#......."""
        )
        s = d.solve()

        self.assertEqual(374, s[0])
        self.assertEqual(None, s[1])


if __name__ == "__main__":
    solver_main(unittest.TestProgram(exit=False), Solver)
