#!/usr/bin/env python3
import logging
import unittest


from advent.solver import AdventDaySolver, AdventDayTestCase, solver_main

SYMBOLS = "`~!@#$%^&*()_-=+[]{}|\\;:'<>,/?"

# FIXME: Solution breaks when `load_input()  ... rstrip()` is removed?


def make_schematic(lines):
    schematic = []

    for line in lines:
        chars = []

        for c in line:
            chars.append(c)

        schematic.append(chars)

    return schematic


def sum_part_numbers(part_numbers):
    sum = 0

    for pn in part_numbers:
        sum += pn

    return sum


def capture_number(lines, start_x, start_y):
    logging.debug(f"capture_number START at ({start_x}, {start_y}): '{lines[start_y]}'")

    # Scan left and right to find the number's left/right bounds.
    # First left:
    first_x = start_x

    for x in range(start_x, -1, -1):
        if not lines[start_y][x].isdigit():
            break
        else:
            first_x = x

    end_x = start_x

    for x in range(start_x, len(lines[start_y])):
        end_x = x

        if not lines[start_y][x].isdigit():
            break

    number = 0

    for x in range(first_x, end_x):
        number = number * 10 + int(lines[start_y][x])

    logging.debug(f"capture_number DONE capured {number} [{first_x}:{end_x}]")

    # Remove the captured number from the schematic
    for x in range(first_x, end_x):
        lines[start_y][x] = "."

    return int(number)


class Solver(
    AdventDaySolver, day=3, year=2023, name="Gear Ratios", solution=(533784, 78826761)
):
    def __init__(self, input):
        super().__init__(input)

    def solve(self):
        return self.find_part_numbers(make_schematic(self.input))

    def find_part_numbers(self, lines):
        NEIGHBORS = [
            (1, 0),
            (1, -1),
            (0, -1),
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
        ]

        part_numbers = []
        gear_ratio_sum = 0

        y_count = len(lines)
        x_count = len(lines[0])  # TODO: Is this always true?

        for y, line in enumerate(lines):
            for x, c in enumerate(line):
                # Skip any characters that are not a symbol.
                if c not in SYMBOLS:
                    continue

                # This is a symbol - search the neighbor tiles to see if they
                # contain a number
                logging.debug(f"({x}, {y}) is symbol {c}")
                neighbor_numbers = []

                for n in NEIGHBORS:
                    n_x = x + n[0]
                    n_y = y + n[1]

                    # Skip if not in bounds
                    if n_x < 0 or n_x >= x_count or n_y < 0 or n_y >= y_count:
                        logging.debug(f"skip ({n_x}, {n_y}) because out of bounds")
                        continue

                    # Skip if the neighbor is not a number:
                    if not lines[n_y][n_x].isdigit():
                        logging.debug(
                            f"skip ({n_x}, {n_y}) because {lines[n_y][n_x]} not a digit"
                        )
                        continue

                    # Capture the number.
                    number = capture_number(lines, n_x, n_y)
                    logging.debug(f"captured {number}")
                    neighbor_numbers.append(number)

                # Add captured numbers to parts list
                part_numbers += neighbor_numbers

                # Is this a gear ratio? If so add it the product of the two numbers
                # to a running sum.
                if len(neighbor_numbers) == 2:
                    gear_ratio_sum += neighbor_numbers[0] * neighbor_numbers[1]

        return (sum_part_numbers(part_numbers), gear_ratio_sum)


class TestPartNumberFinder(AdventDayTestCase):
    def setUp(self):
        super().setUp(Solver)

    def test_sample(self):
        d = self._create_sample_solver(
            """467..114..
...*......
..35..633.
......#...
617*......
.....+.58.
..592.....
......755.
...$.*....
.664.598.."""
        )
        s = d.solve()

        self.assertEqual(4361, s[0])
        self.assertEqual(467835, s[1])


if __name__ == "__main__":
    solver_main(unittest.TestProgram(exit=False), Solver)
