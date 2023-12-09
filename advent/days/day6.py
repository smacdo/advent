#!/usr/bin/env python3
import logging
import re
import unittest

from advent.utils import (
    AdventDaySolver,
    AdventDayTestCase,
    init_logging,
    run_tests_for_solver,
)
from functools import reduce


def parse_input_line(input):
    input_matcher = re.search("(\\w+): (.*)", input)
    assert input_matcher

    field_name = input_matcher.group(1)
    values = [int(s) for s in input_matcher.group(2).split()]

    return (field_name, values)


def find_distances(max_time, min_distance=None):
    if min_distance:
        return [
            t * (max_time - t)
            for t in range(1, max_time)
            if (t * (max_time - t) > min_distance)
        ]
    else:
        return [t * (max_time - t) for t in range(1, max_time)]


class Solver(
    AdventDaySolver, day=6, year=2023, name="Wait For It", solution=(4403592, 38017587)
):
    def __init__(self, input):
        super().__init__(input)

        input_fields = [parse_input_line(line) for line in self.input]
        assert input_fields[0][0] == "Time"
        assert input_fields[1][0] == "Distance"
        assert len(input_fields[0][1]) == len(input_fields[1][1])

        self.input_times = input_fields[0][1]
        self.input_distances = input_fields[1][1]

        # A simple but hacky way to merge the inputs together for part2
        self.p2_input_time = int(
            reduce(lambda acc, x: acc + str(x), self.input_times, "")
        )
        self.p2_input_distance = int(
            reduce(lambda acc, x: acc + str(x), self.input_distances, "")
        )

    def solve(self):
        # Part 1:
        part_1 = 1

        for i in range(0, len(self.input_times)):
            max_time = self.input_times[i]
            min_distance = self.input_distances[i]
            num_ways_to_win = len(find_distances(max_time, min_distance))
            part_1 *= num_ways_to_win

        # Part 2: <3 brute force
        part_2 = len(find_distances(self.p2_input_time, self.p2_input_distance))

        return (part_1, part_2)


class Tests(AdventDayTestCase):
    def setUp(self):
        init_logging(logging.DEBUG)
        super().setUp(Solver)

    def test_sample(self):
        d = self._create_sample_solver(
            """Time:      7  15   30
Distance:  9  40  200"""
        )

        self.assertSequenceEqual([7, 15, 30], d.input_times)
        self.assertSequenceEqual([9, 40, 200], d.input_distances)
        self.assertEqual(71530, d.p2_input_time)
        self.assertEqual(940200, d.p2_input_distance)

        s = d.solve()

        self.assertEqual(288, s[0])
        self.assertEqual(71503, s[1])

    def test_parse_input_line(self):
        field_name, values = parse_input_line("Time:      7  15   30")
        self.assertEqual("Time", field_name)
        self.assertSequenceEqual([7, 15, 30], values)

    def test_find_distances(self):
        self.assertSequenceEqual([6, 10, 12, 12, 10, 6], find_distances(7))
        self.assertSequenceEqual([10, 12, 12, 10], find_distances(7, 8))


if __name__ == "__main__":
    run_tests_for_solver(unittest.TestProgram(exit=False), Solver)
