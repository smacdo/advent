#!/usr/bin/env python3
import logging
import unittest

from advent.utils import (
    AdventDaySolver,
    AdventDayTestCase,
    init_logging,
    run_tests_for_solver,
)


class Solver(AdventDaySolver, day=0, year=0, name="", solution=(None, None)):
    def __init__(self, input):
        super().__init__(input)

    def solve(self):
        return (None, None)


class Tests(AdventDayTestCase):
    def setUp(self):
        init_logging(logging.DEBUG)
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
    run_tests_for_solver(unittest.TestProgram(exit=False), Solver)
