from dataclasses import dataclass
import enum
import logging
import math
import re
from donner.annotations import solver, example
from donner.solution import AbstractSolver
from advent.utils import not_none

MAX_STEPS = 100000


@dataclass
class Node:
    name: str
    left: str
    right: str

    def is_start(self):
        return self.name.endswith("A")

    def is_end(self):
        return self.name.endswith("Z")


class Direction(enum.Enum):
    Left = 0
    Right = 1

    @staticmethod
    def parse(s: str) -> "Direction":
        if s == "R":
            return Direction.Right
        elif s == "L":
            return Direction.Left
        else:
            raise ValueError(f"unknown direction text `{s}`")


@dataclass
class Map:
    instructions: list[Direction]
    network: dict[str, Node]

    @staticmethod
    def parse(input_text: str) -> "Map":
        lines = input_text.splitlines()
        instructions = [Direction.parse(d) for d in lines[0]]

        network: dict[str, Node] = {}

        for line in lines[2:]:
            m = not_none(re.match(r"^(\w+) = \((\w+), (\w+)\)$", line))

            node_name = m.group(1)
            left_name = m.group(2)
            right_name = m.group(3)

            network[node_name] = Node(node_name, left_name, right_name)

        return Map(instructions, network)


def path_length(map: Map, start_node_name: str) -> int:
    steps = 0
    i = 0
    node = map.network[start_node_name]

    while not node.is_end():
        steps += 1
        instruction = map.instructions[i]

        if instruction == Direction.Left:
            node = map.network[node.left]
        else:
            node = map.network[node.right]

        if i < len(map.instructions) - 1:
            i += 1
        else:
            i = 0

        if steps > MAX_STEPS:
            raise Exception(f"step count exceeded {steps} > {MAX_STEPS}")

    return steps


@solver(day=8, year=2023, name="Haunted Wasteland")
@example(
    input=[
        "RL",
        "",
        "AAA = (BBB, CCC)",
        "BBB = (DDD, EEE)",
        "CCC = (ZZZ, GGG)",
        "DDD = (DDD, DDD)",
        "EEE = (EEE, EEE)",
        "GGG = (GGG, GGG)",
        "ZZZ = (ZZZ, ZZZ)",
    ],
    part_one="2",
)
@example(
    input=[
        "LLR",
        "",
        "AAA = (BBB, BBB)",
        "BBB = (AAA, ZZZ)",
        "ZZZ = (ZZZ, ZZZ)",
    ],
    part_one="6",
)
@example(
    input=[
        "LR",
        "",
        "11A = (11B, XXX)",
        "11B = (XXX, 11Z)",
        "11Z = (11B, XXX)",
        "22A = (22B, XXX)",
        "22B = (22C, 22C)",
        "22C = (22Z, 22Z)",
        "22Z = (22B, 22B)",
        "XXX = (XXX, XXX)",
    ],
    part_two="6",
)
class Day8Solver(AbstractSolver):
    def part_one(self, input: str) -> int | str | None:
        map = Map.parse(input)
        return path_length(map, "AAA")

    def part_two(self, input: str) -> int | str | None:
        map = Map.parse(input)

        # Find the length of each path. A path is defined by a start node that
        # ends in "A" and has a end node ending in "Z". Paths may loop back on
        # themselves.
        start_nodes = [n for n in map.network.values() if n.is_start()]
        path_lengths = [path_length(map, n.name) for n in start_nodes]

        logging.debug(f"{map.network}")

        for start_node, plen in zip(start_nodes, path_lengths):
            logging.info(f"{start_node} length = {plen}")

        # There is a undocumented set of conditions in this problem that lead to
        # a "trick" solution using least common multiple. Specifically, the
        # conditions are:
        #
        #  1. Each path wil loop back onto itself
        #  2. Each path contains exactly one exit node
        #  3. The length to reach the exit node from the start is exactly the
        #     same as the length to loop back to the exit node.
        return math.lcm(*path_lengths)
