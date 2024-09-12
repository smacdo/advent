from abc import ABC, abstractmethod
from collections.abc import Iterator
from enum import IntEnum
from oatmeal import Point
from typing import (
    Callable,
    Generic,
    Generator,
    Iterable,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

import heapq
import copy


T = TypeVar("T")


class DirectionCaseNotImplemented(Exception):
    def __init__(self, dir: "Direction"):
        super().__init__(f"Support for direction type {dir} is not implemented")


class Direction(IntEnum):
    """Represents a north/south/east/west direction heading."""

    East = 0
    North = 1
    West = 2
    South = 3

    def to_point(self) -> Point:
        """Convert the direction to a unit point with the same heading."""
        if self == Direction.East:
            return Point(1, 0)
        elif self == Direction.North:
            return Point(0, -1)
        elif self == Direction.West:
            return Point(-1, 0)
        elif self == Direction.South:
            return Point(0, 1)
        else:
            raise DirectionCaseNotImplemented(self)

    def reverse(self) -> "Direction":
        """Get the direction in the opposite direction."""
        if self == Direction.East:
            return Direction.West
        elif self == Direction.North:
            return Direction.South
        elif self == Direction.West:
            return Direction.East
        elif self == Direction.South:
            return Direction.North
        else:
            raise DirectionCaseNotImplemented(self)

    def __str__(self) -> str:
        """Convert the direction to a human readable string"""
        if self == Direction.East:
            return "East"
        elif self == Direction.North:
            return "North"
        elif self == Direction.West:
            return "West"
        elif self == Direction.South:
            return "South"
        else:
            raise DirectionCaseNotImplemented(self)

    @classmethod
    def cardinal_dirs(cls) -> Iterator["Direction"]:
        """Generate all four cardination directions."""
        yield Direction.East
        yield Direction.North
        yield Direction.West
        yield Direction.South

    @classmethod
    def from_point(cls, pt: Point) -> "Direction":
        """Convert from a unit point to a direction or throw an exception."""
        if not isinstance(pt, Point):
            raise NotImplementedError

        if pt.x == 1 and pt.y == 0:
            return Direction.East
        elif pt.x == 0 and pt.y == -1:
            return Direction.North
        elif pt.x == -1 and pt.y == 0:
            return Direction.West
        elif pt.x == 0 and pt.y == 1:
            return Direction.South
        else:
            raise Exception(
                f"Expected a unit point but got {pt} when converting to Direction"
            )


class Grid(Generic[T]):
    """Holds a collection of values in a 2d grid."""

    __slots__ = ("cells", "x_count", "y_count")
    cells: list[T]
    x_count: int
    y_count: int

    def __init__(
        self,
        x_count: int,
        y_count: int,
        initial: Union[T, Callable[[], T], list[list[T]]],
    ):
        if x_count < 1:
            raise ValueError("Column count `x_count` must be larger than zero")
        if y_count < 1:
            raise ValueError("Row count `y_count` must be larger than zero")

        self.x_count = x_count
        self.y_count = y_count

        if isinstance(initial, list):
            if len(initial) != self.y_count:
                raise Exception("Grid initial rows list len must equal `y_count`")

            # Verify all rows are lists of cells and of uniform size.
            for row in initial:
                if not isinstance(row, list):
                    raise Exception(
                        "Grid initial rows must all be lists of column value"
                    )
                if len(row) != self.x_count:
                    raise Exception("Grid initial rows be consistent length")

            # Copy rows.
            self.cells = [c for row in initial for c in row]
        elif callable(initial):
            self.cells = [initial() for _ in range(x_count * y_count)]
        else:
            self.cells = [copy.deepcopy(initial) for _ in range(x_count * y_count)]

    def check_in_bounds(self, pt: Point) -> bool:
        """Test if a point is a valid cell position."""
        if not isinstance(pt, Point):
            raise TypeError("argument `pt` must be type `Point`")

        return pt.x >= 0 and pt.y >= 0 and pt.x < self.x_count and pt.y < self.y_count

    def _validate_in_bounds(self, pt: Point) -> None:
        """Throw an exception if the point is not a valid cell position."""
        if not self.check_in_bounds(pt):
            raise IndexError(
                f"Point out of bounds; x: 0<={pt.x}<{self.x_count}, y: 0<={pt.y}<{self.y_count}"
            )

    def col(self, x_col: int) -> Iterable[T]:
        """Returns an iterator across all the cells in column `x_col`"""
        if not isinstance(x_col, int):
            raise TypeError("argument `x_col` must be type `int`")

        if x_col < 0 or x_col >= self.x_count:
            raise ValueError(f"col {x_col} is out of bounds")

        for i in range(x_col, self.y_count * self.x_count + x_col, self.x_count):
            yield self.cells[i]

    def row(self, y_row: int) -> Iterable[T]:
        """Returns an iterator across all the cells in row `y_row`"""
        if not isinstance(y_row, int):
            raise TypeError("argument `y_col` must be type `int`")

        if y_row < 0 or y_row >= self.y_count:
            raise ValueError(f"row {y_row} is out of bounds")

        for i in range(y_row * self.x_count, (y_row + 1) * self.x_count):
            yield self.cells[i]

    def rows(self) -> "GridMultiRowIterator[T]":
        """Returns an interator that yields each row in the grid."""
        return GridMultiRowIterator(self, 0, self.row_count())

    def row_count(self) -> int:
        """Returns the number of rows in the grid."""
        return self.y_count

    def col_count(self) -> int:
        """Returns the number of cols in the grid."""
        return self.x_count

    def insert_row(
        self, at_index: int, row: Union[T, Callable[[], T], list[T]]
    ) -> None:
        """Inserts `row` before the grid row `at_index`"""

        # Helper function to generate new cells from either original or new
        # row.
        def expand_cells(
            cells: list[T],
            x_count: int,
            y_count: int,
            at_index: int,
            row: Union[T, Callable[[], T], list[T]],
        ) -> Generator[T, None, None]:
            for y in range(y_count + 1):
                for x in range(x_count):
                    if y < at_index:
                        yield cells[y * x_count + x]
                    elif y == at_index:
                        if isinstance(row, list):
                            yield row[x]
                        elif callable(row):
                            yield row()
                        else:
                            yield copy.deepcopy(row)
                    else:
                        yield cells[(y - 1) * x_count + x]

        # New row must be same size as rows in this grid and the index to be
        # inserted at must be within range.
        if isinstance(row, list) and len(row) != self.x_count:
            raise ValueError(
                "`row` to be inserted must be same length as grid col count"
            )

        if at_index < 0 or at_index > self.y_count:
            raise ValueError("`at_index` must be within the row range of existing grid")

        # Copy values into new array and insert the row at the correct location
        # with the helper function.
        self.cells = [
            x
            for x in expand_cells(self.cells, self.x_count, self.y_count, at_index, row)
        ]
        self.y_count += 1

    def insert_col(
        self, at_index: int, col: Union[T, Callable[[], T], list[T]]
    ) -> None:
        # Helper function to generate new cells from either original or new
        # col.
        """Inserts `col` before the grid col `at_index`"""

        def expand_cells(
            cells: list[T],
            x_count: int,
            y_count: int,
            at_index: int,
            col: Union[T, Callable[[], T], list[T]],
        ) -> Generator[T, None, None]:
            for y in range(y_count):
                for x in range(x_count + 1):
                    if x < at_index:
                        yield cells[y * x_count + x]
                    elif x == at_index:
                        if isinstance(col, list):
                            yield col[y]
                        elif callable(col):
                            yield col()
                        else:
                            yield copy.deepcopy(col)
                    else:
                        yield cells[y * x_count + (x - 1)]

        # New col must be same size as cols in this grid, and the index to be
        # inserted at must be within range.
        if isinstance(col, list) and len(col) != self.y_count:
            raise ValueError("`col` to be inserted must be same size as grid row count")

        if at_index < 0 or at_index > self.x_count:
            raise ValueError("`at_index` must be within the col range of existing grid")

        # Copy values into new array and insert the row at the correct location
        # with the helper function.
        self.cells = [
            x
            for x in expand_cells(self.cells, self.x_count, self.y_count, at_index, col)
        ]
        self.x_count += 1

    def __getitem__(self, pt: Point) -> T:
        if not isinstance(pt, Point):
            raise TypeError("argument `pt` must be type `Point`")

        self._validate_in_bounds(pt)
        return self.cells[pt.y * self.x_count + pt.x]

    def __setitem__(self, pt: Point, v: T) -> None:
        if not isinstance(pt, Point):
            raise TypeError("argument `pt` must be type `Point`")

        self._validate_in_bounds(pt)
        self.cells[pt.y * self.x_count + pt.x] = v

    def __delitem__(self, pt: Point) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        return len(self.cells)

    def __iter__(self) -> Iterator[T]:
        return iter(self.cells)

    def __str__(self) -> str:
        return "\n".join(
            "".join(str(self.cells[y * self.x_count + x]) for x in range(self.x_count))
            for y in range(self.y_count)
        )

    def __contains__(self, pt: Point) -> bool:
        if not isinstance(pt, Point):
            raise TypeError("argument `pt` must be type `Point`")
        return pt.x >= 0 and pt.y >= 0 and pt.x < self.x_count and pt.y < self.y_count


class GridRowIterator(Generic[T]):
    __slots__ = ("grid", "row", "x", "end_x")
    grid: Grid[T]
    row: int
    x: int
    end_x: int

    def __init__(self, grid: Grid[T], row: int, x: int, end_x: int):
        # TODO: Bounds check.
        self.grid = grid
        self.row = row
        self.x = x
        self.end_x = end_x

    def __next__(self) -> T:
        if self.x < self.grid.col_count():
            self.x += 1
            return self.grid[Point(self.x - 1, self.row)]
        else:
            raise StopIteration

    def __iter__(self):
        return self


class GridMultiRowIterator(Generic[T]):
    __slots__ = ("grid", "row", "end_row")
    grid: Grid[T]
    row: int
    end_row: int

    def __init__(self, grid: Grid[T], start_row: int, end_row: int):
        if start_row < 0 or start_row >= end_row:
            raise Exception(f"start_row={start_row} out of range")

        if end_row > grid.row_count():
            raise Exception(f"end_row={end_row} larger than row count")

        self.grid = grid
        self.row = start_row
        self.end_row = end_row

    def __next__(self) -> GridRowIterator[T]:
        if self.row < self.grid.row_count():
            self.row += 1
            return GridRowIterator(self.grid, self.row - 1, 0, self.grid.col_count())
        else:
            raise StopIteration

    def __iter__(self):
        return self


ItemWithCost = Tuple[T, Union[float, int]]


class PriorityQueue(Generic[T]):
    """An ergonomic min heap prority queue class built on Python's `heapq`."""

    __slots__ = ("items", "item_counter")
    items: list[Tuple[float, int, T]]
    item_counter: int

    def __init__(self, initial_items: Optional[Iterable[ItemWithCost]] = None):
        self.items = []
        self.item_counter = 0

        if initial_items is not None:
            for item in initial_items:
                if not isinstance(item, tuple):
                    raise TypeError(
                        "argument `initial_items` contains non-tuple values"
                    )

                self.add(item[0], item[1])

    def is_empty(self):
        return len(self.items) == 0

    def add(self, item: T, cost: Union[float, int]) -> None:
        """Add an `item` to the priority with priority `cost`."""
        if not isinstance(cost, float) and not isinstance(cost, int):
            raise TypeError("argument `cost` must be of type `float` or `int`")

        heapq.heappush(self.items, (float(cost), self.item_counter, item))

        # Increment the item counter each time an item is added to the priority
        # queue. This value is used to break ties with items that have the same
        # priority otherwise Python tries to compare the item itself.
        self.item_counter += 1

    def pop(self) -> T:
        """Removes the lowest priority item from the queue and returns it."""
        if len(self.items) < 1:
            raise Exception("cannot pop empty priority queue")

        return heapq.heappop(self.items)[2]


def manhattan_distance(a: Point, b: Point) -> float:
    """Calculate the straight line distance between two points"""
    dx = abs(a.x - b.x)
    dy = abs(a.y - b.y)
    return dx + dy


# (grid, from_point, to_point) -> cost
CellCostFunc = Callable[[Grid, Point, Point], Optional[float]]
CellHeuristicFunc = Callable[[Point, Point], float]


def astar_search(
    grid: Grid[T],
    start_pos: Point,
    goal_pos: Point,
    cell_cost: CellCostFunc,
    heuristic: Optional[CellHeuristicFunc],
) -> Optional[list[Point]]:
    """Returns a potential shortest path from `start_pos` to `goal_pos` using
    the A* search algorithm."""

    # Check input arguments for errors.
    if not isinstance(grid, Grid):
        raise TypeError("argument `grid` must be of type `Grid[T]`")
    if not isinstance(start_pos, Point):
        raise TypeError("argument `start_pos` must be of type `Point")
    if start_pos not in grid:
        raise ValueError("argument `start_pos` is out of bounds")
    if not isinstance(goal_pos, Point):
        raise TypeError("argument `goal_pos` must be of type `Point")
    if goal_pos not in grid:
        raise ValueError("argument `goal_pos` is out of bounds")

    # Use A* to find the shortest path to the goal.
    frontier: PriorityQueue[Point] = PriorityQueue([(start_pos, 0)])

    cost_so_far: dict[Point, float] = {start_pos: 0}
    came_from: dict[Point, Point] = {}
    reached_goal = False

    while not frontier.is_empty():
        current_pos = frontier.pop()

        # Stop searching when we reach the goal.
        if current_pos == goal_pos:
            reached_goal = True
            break

        # Examine all of the cells that are adjacent to this cell.
        for dir in Direction.cardinal_dirs():
            # Ignore any invalid cell positions.
            neighbor_pos = current_pos + dir.to_point()

            if neighbor_pos not in grid:
                continue

            # Calculate of moving to this tile by adding the current cost of
            # moving from the start to the current tile and then adding the cost
            # of moving from current to this adjacent neighbor.
            #
            # A movement cost of `None` implies the movement from current_pos to
            # neighbor_pos is not allowed.
            move_cost = cell_cost(grid, current_pos, neighbor_pos)

            if move_cost is None:
                continue
            elif not isinstance(move_cost, float) and not isinstance(move_cost, int):
                raise TypeError("`cell_cost` return value must be of type float or int")
            elif move_cost <= 0:
                raise ValueError("`cell_cost` return value must be larger than zero")

            new_cost = cost_so_far[current_pos] + move_cost

            # Add this tile to the frontier queue if its the first time the cell
            # was visited, or if the cost to reach it is lower than the previous
            # cost.
            if neighbor_pos not in cost_so_far or new_cost < cost_so_far[neighbor_pos]:
                # Remember the cost it took to reach this cell.
                cost_so_far[neighbor_pos] = new_cost

                # Estimate the total cost of traversing from the start to the
                # goal via this cell.
                estimated_cost = new_cost

                if heuristic:
                    h = heuristic(current_pos, neighbor_pos)

                    if not isinstance(h, float) and not isinstance(h, int):
                        raise TypeError(
                            "`heuristic` return value must be of type float or int"
                        )
                    elif h <= 0:
                        raise ValueError(
                            "`heuristic` return value must be larger than zero"
                        )

                    estimated_cost += h

                # Add the cell to the frontier with the new estimated cost.
                frontier.add(neighbor_pos, estimated_cost)

                # Remember the previous cell in the path leading to this cell.
                # This is used for backgtracking to find the shortest path.
                came_from[neighbor_pos] = current_pos

    # Reconstruct path if the goal was reached, otherwise return an empty path.
    if reached_goal:
        # Start at the goal.
        current_pos = goal_pos
        path: list[Point] = []

        # Walk backwards from the goal to the start and append each node into a
        # path list.
        while current_pos != start_pos:
            path.append(current_pos)
            current_pos = came_from[current_pos]

        path.append(start_pos)
        path.reverse()

        # Return the path from the start to the goal.
        return path
    else:
        # No path was found.
        return None


class BFS(ABC, Generic[T]):
    __slots__ = ("grid", "start_pos", "frontier", "visited")
    grid: Grid[T]
    start_pos: Point
    frontier: list[Point]
    visited: set[Point]

    def __init__(self, grid: Grid[T], start_pos: Point):
        if not isinstance(grid, Grid):
            raise TypeError("`grid` must be of type `Grid[T]`")
        if not isinstance(start_pos, Point):
            raise TypeError("`start_pos` must be of type `Point`")
        if start_pos not in grid:
            raise ValueError("`start_pos` must be a valid position in `grid`")

        self.grid = grid
        self.start_pos = start_pos
        self.frontier = []
        self.visited = set()

    def reset(self) -> None:
        """Reset the BFS solver to its initial state."""
        self.visited.clear()
        self.frontier.clear()

        self.frontier.append(self.start_pos)

    def run(self) -> None:
        """Run a breadth first search operation."""
        self.reset()

        while len(self.frontier) > 0:
            cell_pos = self.frontier.pop(0)
            self.visited.add(cell_pos)

            for dir in Direction.cardinal_dirs():
                neighbor_pos = cell_pos + dir.to_point()

                if (
                    self.grid.check_in_bounds(neighbor_pos)
                    and neighbor_pos not in self.visited
                ):
                    self.on_visit(
                        self.grid[cell_pos], self.grid[neighbor_pos], neighbor_pos, dir
                    )

    def add_frontier(self, cell_pos: Point) -> None:
        """Add a new cell position to the unexplored frontier."""
        if not isinstance(cell_pos, Point):
            raise TypeError("`cell_pos` must be of type `Point`")

        if cell_pos in self.visited:
            raise ValueError(f"Cell position {cell_pos} already visited")
        elif cell_pos not in self.grid:
            raise ValueError(f"Cell position {cell_pos} out of bounds")
        else:
            self.frontier.append(cell_pos)

    @abstractmethod
    def on_visit(
        self, from_cell: T, to_cell: T, to_pos: Point, to_dir: Direction
    ) -> None:
        raise NotImplementedError
