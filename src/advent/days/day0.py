#!/usr/bin/env python3
import unittest

from advent.solver import AdventDaySolver, AdventDayTestCase, solver_main


class Solver(AdventDaySolver, day=0, year=0, name="", solution=(None, None)):
    def __init__(self, input):
        super().__init__(input)

    def solve(self):
        return (None, None)


class Tests(AdventDayTestCase):
    def setUp(self):
        super().setUp(Solver)

    def test_sample(self):
        d = self._create_sample_solver(
            """line_1
line_2
line_3"""
        )
        s = d.solve()

        self.assertEqual(None, s[0])
        self.assertEqual(None, s[1])


if __name__ == "__main__":
    solver_main(unittest.TestProgram(exit=False), Solver)
