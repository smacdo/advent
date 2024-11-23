from dataclasses import dataclass
from advent.spatial import ConnectedTile, Direction, Grid
from donner.annotations import solver, example
from donner.solution import AbstractSolver
from enum import IntEnum

from oatmeal import Point


class TileType(IntEnum):
    """

    0000 SWNE

    bit 0: East     2**0 = 1
        1: North    2**1 = 2
        2: West     2**2 = 4
        3: South    2**3 = 8

    Name          | Edge 1       | Edge 2       | Bits         |
    --------------+--------------+--------------+--------------+
    Vertical      | North        | South        | 10 = 1010    |
    Horizontal    | East         | West         |  5 = 0101    |
    NorthToEast   | North        | East         |  3 = 0011    |
    NorthToWest   | North        | West         |  6 = 0110    |
    SouthToWest   | West         | South        | 12 = 1100    |
    SouthToEast   | East         | South        |  9 = 1001    |
    """

    Ground = 0
    Vertical = 10
    Horizontal = 5
    NorthToEast = 3
    NorthToWest = 6
    SouthToWest = 12
    SouthToEast = 9
    Start = 16


TILE_TYPE_TO_DIRS = {
    TileType.Ground: (),
    TileType.Vertical: (Direction.North, Direction.South),
    TileType.Horizontal: (Direction.East, Direction.West),
    TileType.NorthToEast: (Direction.North, Direction.East),
    TileType.NorthToWest: (Direction.North, Direction.West),
    TileType.SouthToWest: (Direction.South, Direction.West),
    TileType.SouthToEast: (Direction.South, Direction.East),
}


TILE_TO_LETTER = {
    TileType.Ground: ".",
    TileType.Vertical: "|",
    TileType.Horizontal: "-",
    TileType.NorthToEast: "L",
    TileType.NorthToWest: "J",
    TileType.SouthToWest: "7",
    TileType.SouthToEast: "F",
}

TILE_TO_UNICODE = {
    TileType.Ground: ".",
    TileType.Vertical: "│",
    TileType.Horizontal: "─",
    TileType.NorthToEast: "└",
    TileType.NorthToWest: "┘",
    TileType.SouthToWest: "┐",
    TileType.SouthToEast: "┌",
}

LETTER_TO_TILE = {
    ".": TileType.Ground,
    "|": TileType.Vertical,
    "-": TileType.Horizontal,
    "L": TileType.NorthToEast,
    "J": TileType.NorthToWest,
    "7": TileType.SouthToWest,
    "F": TileType.SouthToEast,
    "S": TileType.Start,
}

NEIGHBORS = [
    (TileType.NorthToEast, Direction.North, Direction.East),
    (TileType.NorthToWest, Direction.North, Direction.South),
    (TileType.SouthToWest, Direction.South, Direction.West),
    (TileType.SouthToEast, Direction.South, Direction.East),
]


# TODO: Verify <= 2 edges set.
@dataclass
class Tile(ConnectedTile):
    is_start: bool

    def __init__(self, tile_type: TileType, is_start=False):
        # super().__init__(0, tile_type if tile_type != TileType.Start else None)

        # if tile_type == TileType.Start:
        #    self.edge_connections = 0
        #    self.is_start = True
        # else:
        #    self.edge_connections = int(tile_type)
        #    self.is_start = is_start
        pass

    @staticmethod
    def parse(c: str) -> "Tile":
        if c in LETTER_TO_TILE:
            return Tile(LETTER_TO_TILE[c])
        else:
            raise ValueError(f"unknown tile letter `{c}`")

    def type(self):
        edges = self.edge_connections

        if edges == 0:
            return TileType.Ground
        elif edges == 10:
            return TileType.Vertical
        elif edges == 5:
            return TileType.Horizontal
        elif edges == 3:
            return TileType.NorthToEast
        elif edges == 6:
            return TileType.NorthToWest
        elif edges == 12:
            return TileType.SouthToWest
        elif edges == 9:
            return TileType.SouthToEast
        else:
            raise ValueError("unknown tile type value = {edges}")

    def __str__(self):
        return TILE_TO_UNICODE[self.type()]


def parse_grid_input(input: str) -> Grid[Tile]:
    lines = input.splitlines()
    y_count = len(lines)
    x_count = len(lines[0])
    grid = Grid(x_count, y_count, lambda x, y: Tile.parse(lines[y][x]))

    for y in range(0, y_count):
        for x in range(0, x_count):
            pt = Point(x, y)
            tile = grid[pt]

            if tile.is_start:
                print(f"is_start tile at {pt}")
                did_find_neighbor = False

                for tile_type, dir_a, dir_b in NEIGHBORS:
                    pt_a = pt + dir_a.to_point()
                    pt_b = pt + dir_b.to_point()

                    print(
                        f"check {dir_a} {pt_a} has {grid[pt_a].edge_connections} = {grid[pt_a].edge(dir_a.reverse())} and {dir_b} {pt_b} has {grid[pt_b].edge_connections} = {grid[pt_b].edge(dir_b.reverse())}"
                    )

                    if (
                        grid.check_in_bounds(pt_a)
                        and grid.check_in_bounds(pt_b)
                        and grid[pt_a].edge(dir_a.reverse())
                        and grid[pt_b].edge(dir_b.reverse())
                    ):
                        grid[pt] = Tile(tile_type, is_start=True)
                        did_find_neighbor = True

                if not did_find_neighbor:
                    raise Exception("could not find a neighbor for start tile")

    return grid


@solver(day=10, year=2023, name="Pipe Maze")
@example(
    input=[
        ".....",
        ".S-7.",
        ".|.|.",
        ".L-J.",
        ".....",
    ],
    part_one="4",
)
@example(
    input=[
        "..F7.",
        ".FJ|.",
        "SJ.L7",
        "|F--J",
        "LJ...",
    ],
    part_one="8",
)
class Day10Solver(AbstractSolver):
    def part_one(self, input: str) -> int | str | None:
        # grid = parse_grid_input(input)
        # print(grid)
        print("testing 123")
        return 1

    def part_two(self, input: str) -> int | str | None:
        return None
