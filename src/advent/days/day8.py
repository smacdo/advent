#!/usr/bin/env python3
import logging
import re
import unittest

from math import lcm

from advent.solver import AdventDaySolver, AdventDayTestCase, solver_main


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


def solve_path(commands, nodes, start_node_name, end_node_name):
    def is_target(node, end_node_name):
        if end_node_name:
            return node.name == end_node_name
        else:
            return node.name.endswith("Z")

    n = nodes[start_node_name]
    i = 0
    steps = 0

    while not is_target(n, end_node_name):
        # Infinite loop check:
        # if steps > 10:
        #    raise Exception("solver hit too many steps - infinite loop?")

        # Perform requested move.
        command = commands[i]
        next_node_name = n.go(command)

        # logging.debug(
        #    f"{command}: {n.name}, {n.left}, {n.right} -> {next_node_name} step {steps}"
        # )
        assert next_node_name in nodes

        n = nodes[next_node_name]
        steps += 1

        # Move to next command.
        i += 1
        if i >= len(commands):
            i = 0

    return steps


class Solver(
    AdventDaySolver,
    day=8,
    year=2023,
    name="Haunted Wasteland",
    solution=(14681, 14321394058031),
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
        return solve_path(self.commands, self.nodes, "AAA", "ZZZ")

    def solve_2(self):
        # This one is a bit nasty. My initial solution was to copy the solution
        # to part #1, and modify it work for multiple nodes at once. Turns out
        # the input set has cycles that (in theory) eventually sync up to put
        # all the nodes on target BUT the number of steps to get there is huge.
        #
        # Another solution is to calculate the number of steps each node needs
        # from its starting location, and then find the lowest common multiple
        # which gives us the answer without having to simulate every step. This
        # solution is similiar to problems in AoC question in part years. A more
        # generic solution would be to use the Chinese remainder theorem (CRT).
        #
        # Using LCM works because the input is constructed in a specific manner
        # such that the number of nodes BEFORE the "head" of the cycle is
        # exactly same as the number of nodes IN the cycle.
        start_nodes = [self.nodes[n] for n in self.nodes if n.endswith("A")]
        end_nodes = [
            solve_path(self.commands, self.nodes, n.name, None) for n in start_nodes
        ]

        logging.debug(f"ends: {end_nodes}")

        return lcm(*end_nodes)


class Tests(AdventDayTestCase):
    def setUp(self):
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


if __name__ == "__main__":
    solver_main(unittest.TestProgram(exit=False), Solver)
