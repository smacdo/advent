from dataclasses import dataclass
from advent.spatial import Grid
from advent.utils import new_grid_from_input_lines
from donner.annotations import example, solver
from donner.solution import AbstractSolver
from oatmeal import Point
import logging


@dataclass
class Symbol:
    sym: str
    part_numbers: list[int]


def find_symbols_and_adjacent_part_numbers(schematic: Grid[str]) -> list[Symbol]:
    # Walk through the schematic grid starting at the top left. For each
    # symbol (any non-numeric non-period) record all of the numbers adjacent
    # to it.
    symbols: list[Symbol] = []

    for y in range(0, schematic.row_count()):
        for x in range(0, schematic.col_count()):
            xy_pos = Point(x, y)
            c = schematic[xy_pos]

            # Skip cells that are not a gear symbol.
            if c.isdigit() or c == ".":
                continue

            logging.debug(f"found symbol {c} at {xy_pos}")

            # Look at the cells that neighbor this symbol. Are any of those
            # cells part of a number?
            numbers: list[int] = []

            for n_pos in schematic.diagonal_neighbors(xy_pos):
                if schematic[n_pos].isdigit():
                    # This cell is a digit in a larger number that is adjacent
                    # to the current symbol.
                    #
                    # Scan to the left to find the start of the number, and scan
                    # to the right to find the end of the number.
                    left = n_pos.x
                    while left > 0 and schematic[Point(left - 1, n_pos.y)].isdigit():
                        left -= 1

                    right = n_pos.x
                    while (
                        right < schematic.x_count - 1
                        and schematic[Point(right + 1, n_pos.y)].isdigit()
                    ):
                        right += 1

                    # Extract the number by walking through each digit from left
                    # to right. Make sure to zero out each digit after scanning
                    # it to prevent the number from being attached to more than
                    # one symbol
                    number = 0

                    for xi in range(left, right + 1):
                        xi_pos = Point(xi, n_pos.y)
                        number = int(schematic[xi_pos]) + number * 10

                        schematic[xi_pos] = "."

                    logging.debug(
                        f"adding number `{number}` from {n_pos} part of {c} at {xy_pos}"
                    )

                    # Add the part number to the current symbol.
                    numbers.append(number)

            # Add the symbol to the list of all symbols found in the schematic.
            symbols.append(Symbol(c, numbers))

    return symbols


@solver(day=3, year=2023, name="Gear Ratios")
@example(
    input=[
        "467..114..",
        "...*......",
        "..35..633.",
        "......#...",
        "617*......",
        ".....+.58.",
        "..592.....",
        "......755.",
        "...$.*....",
        ".664.598..",
    ],
    part_one="4361",
    part_two="467835",
)
class Day2Solver(AbstractSolver):
    def part_one(self, input: str) -> int | str | None:
        schematic = new_grid_from_input_lines(input.splitlines())
        symbols = find_symbols_and_adjacent_part_numbers(schematic)

        # Sum all of the part numbers associated with a symbol in the schematic.
        sum = 0

        for s in symbols:
            for n in s.part_numbers:
                sum += n

        return sum

    def part_two(self, input: str) -> int | str | None:
        schematic = new_grid_from_input_lines(input.splitlines())
        symbols = find_symbols_and_adjacent_part_numbers(schematic)

        # Sum the gear ratios which are all the gear symbols `*` with exactly
        # two part numbers.
        sum = 0

        for s in symbols:
            if s != "*" and len(s.part_numbers) != 2:
                continue

            sum += s.part_numbers[0] * s.part_numbers[1]

        return sum
