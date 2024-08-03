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
        if self.galaxy_id:
            return str(self.galaxy_id)
        else:
            return "."


def parse_input(lines: Iterable[Iterable[str]]) -> Grid[Tile]:
    char_grid = new_grid_from_input_lines(lines)
    tile_grid: Grid[Tile] = Grid(char_grid.x_count, char_grid.y_count, Tile)
    next_galaxy_id = 1

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
    num_cols_expanded = 0
    num_rows_expanded = 0

    for i in range(grid.col_count()):
        xi = i + num_cols_expanded

        if count_if(grid.col(xi), lambda x: x.galaxy_id is not None) == 0:
            grid.insert_col(xi, Tile)
            num_cols_expanded += 1

    for i in range(grid.row_count()):
        xi = i + num_rows_expanded

        if count_if(grid.row(xi), lambda x: x.galaxy_id is not None) == 0:
            grid.insert_row(xi, Tile)
            num_rows_expanded += 1


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

        counter = 50

        for a, b in all_pairs(galaxies):
            if counter > 0:
                counter -= 1
            else:
                return total_cost

            path = astar_search(
                self.tile_grid,
                galaxy_tiles[a],
                galaxy_tiles[b],
                lambda grid, ta, tb: grid[tb].cost,
                manhattan_distance,
            )

            if path is None:
                raise Exception("path should be valid")

            cost = len(path) - 1
            total_cost += cost
            print(f"{a} -> {b} is {cost}")

        return total_cost


class Tests(AdventDayTestCase):
    def setUp(self):
        super().setUp(Solver)

    def test_sample(self):
        d = self._create_sample_solver(
            """...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#....."""
        )

        self.assertEqual(374, d[0])
        self.assertEqual(None, d[1])


if __name__ == "__main__":
    solver_main(unittest.TestProgram(exit=False), Solver)
