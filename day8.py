#!/usr/bin/env python3
import logging
import re
import unittest

from utils import AdventDaySolver, AdventDayTestCase, init_logging


class Node:
    def __init__(self, name, left, right):
        self.name = name
        self.left = left
        self.right = right

    def go(self, dirname):
        if dirname == "L":
            return self.left
        elif dirname == "R":
            return self.right
        else:
            raise Exception(f"unknown direction {dirname}")


def parse_input(input_lines):
    commands = input_lines.pop(0)
    input_lines.pop(0)

    nodes = dict()

    for line in input_lines:
        input_matcher = re.search("(\\w+) = \\((\\w+), (\\w+)\\)", line)
        assert input_matcher

        name = input_matcher.group(1)
        left = input_matcher.group(2)
        right = input_matcher.group(3)

        nodes[name] = Node(name, left, right)

    return (commands, nodes)


class Solver(
    AdventDaySolver, day=8, year=2023, name="Haunted Wasteland", solution=(14681, None)
):
    def __init__(self, input):
        super().__init__(input)
        self.commands, self.nodes = parse_input(input)

        self.has_aaa = "AAA" in self.nodes
        self.has_end_a = any(n for n in self.nodes if n.endswith("A"))

    def solve(self):
        part_1 = self.solve_1() if self.has_aaa else None
        part_2 = self.solve_2() if self.has_end_a else None
        return (part_1, part_2)

    def solve_1(self):
        assert "AAA" in self.nodes
        n = self.nodes["AAA"]
        i = 0
        steps = 0

        while n.name != "ZZZ":
            # Infinite loop check:
            # if steps > 10:
            #    raise Exception("solver hit too many steps - infinite loop?")

            # Perform requested move.
            command = self.commands[i]
            next_node_name = n.go(command)
            # logging.debug(
            #    f"{command}: {n.name}, {n.left}, {n.right} -> {next_node_name} step {steps}"
            # )
            assert next_node_name in self.nodes

            n = self.nodes[next_node_name]
            steps += 1

            # Move to next command.
            i += 1
            if i >= len(self.commands):
                i = 0

        return steps

    def solve_2(self):
        nodes = [self.nodes[n] for n in self.nodes if n.endswith("A")]

        i = 0
        steps = 0

        while any(n for n in nodes if not n.name.endswith("Z")):
            # Infinite loop check:
            if steps > 1000000:
                raise Exception("solver hit too many steps - infinite loop?")

            # Perform requested move.
            command = self.commands[i]

            for n_i, n in enumerate(nodes):
                next_node_name = n.go(command)
                assert next_node_name in self.nodes

                nodes[n_i] = self.nodes[next_node_name]

            steps += 1

            # Move to next command.
            i += 1
            if i >= len(self.commands):
                i = 0

        return steps


class Tests(AdventDayTestCase):
    def setUp(self):
        init_logging(logging.DEBUG)
        super().setUp(Solver)

    def test_sample_1(self):
        d = self._create_sample_solver(
            """RL

AAA = (BBB, CCC)
BBB = (DDD, EEE)
CCC = (ZZZ, GGG)
DDD = (DDD, DDD)
EEE = (EEE, EEE)
GGG = (GGG, GGG)
ZZZ = (ZZZ, ZZZ)"""
        )
        s = d.solve()

        self.assertEqual(2, s[0])

    def test_sample_2(self):
        d = self._create_sample_solver(
            """LLR

AAA = (BBB, BBB)
BBB = (AAA, ZZZ)
ZZZ = (ZZZ, ZZZ)"""
        )
        s = d.solve()

        self.assertEqual(6, s[0])

    def test_sample_3(self):
        d = self._create_sample_solver(
            """LR

11A = (11B, XXX)
11B = (XXX, 11Z)
11Z = (11B, XXX)
22A = (22B, XXX)
22B = (22C, 22C)
22C = (22Z, 22Z)
22Z = (22B, 22B)
XXX = (XXX, XXX)"""
        )
        s = d.solve()

        self.assertEqual(6, s[1])

    def test_real_input(self):
        s = self._create_real_solver().solve()
        self.assertEqual(14681, s[0])
        self.assertEqual(None, s[1])
        pass


if __name__ == "__main__":
    unittest.main()
