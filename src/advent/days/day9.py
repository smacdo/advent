#!/usr/bin/env python3
import unittest

from advent.solver import AdventDaySolver, AdventDayTestCase, solver_main
from advent.utils import unzip


def parse_inputs(input_lines):
    entries = []
    for line in input_lines:
        entries.append([int(s) for s in line.split()])

    return entries


def reduce(entry):
    # reduce the entry to zero, and return an array containing the last col
    # of each row starting from the bottom (but not including the zero).
    # logging.debug(f"REDUCE: {entry}")
    first_cols = []
    placeholder_sum = 0
    steps = 0

    while not all(x == 0 for x in entry):
        if steps > 100:
            raise Exception("debug tripwire")

        steps += 1

        # save the first column
        first_cols.append(entry[0])

        # reduce the row
        for i in range(0, len(entry) - 1):
            entry[i] = entry[i + 1] - entry[i]

        # Remove last element from entry, and use that value to extrapolate
        # forwards.
        last_element = entry.pop()
        placeholder_sum += last_element

    # Extrapolate backwards.
    first_cols.reverse()
    new_first = 0

    for x in first_cols:
        new_first = x - new_first

    return (placeholder_sum, new_first)


class Solver(
    AdventDaySolver,
    day=9,
    year=2023,
    name="Mirage Maintenance",
    solution=(2005352194, 1077),
):
    def __init__(self, input):
        super().__init__(input)
        self.entries = parse_inputs(input)

    def solve(self):
        part_1, part_2 = unzip(reduce(e) for e in self.entries)
        return (sum(part_1), sum(part_2))


class Tests(AdventDayTestCase):
    def setUp(self):
        super().setUp(Solver)

    def test_sample_1a(self):
        d = self._create_sample_solver("""0   3   6   9  12  15""")
        self.assertSequenceEqual([[0, 3, 6, 9, 12, 15]], d.entries)

        s = d.solve()

        self.assertEqual(18, s[0])

    def test_sample_1b(self):
        d = self._create_sample_solver("""1   3   6  10  15  21""")
        s = d.solve()

        self.assertEqual(28, s[0])

    def test_sample_1c(self):
        d = self._create_sample_solver("""10  13  16  21  30  45""")
        s = d.solve()

        self.assertEqual(68, s[0])

    def test_sample_2a(self):
        d = self._create_sample_solver("""10  13  16  21  30  45""")
        s = d.solve()

        self.assertEqual(5, s[1])

    def test_sample_all(self):
        d = self._create_sample_solver(
            """0   3   6   9  12  15
1   3   6  10  15  21
10  13  16  21  30  45"""
        )
        s = d.solve()

        self.assertEqual(114, s[0])
        self.assertEqual(2, s[1])


if __name__ == "__main__":
    solver_main(unittest.TestProgram(exit=False), Solver)
