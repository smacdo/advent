import logging
import re
import unittest

from enum import Enum
from multiprocessing import Pool
from advent.utils import AdventDaySolver, AdventDayTestCase, init_logging


def merge_ranges(ranges):
    in_ranges = list(sorted(ranges, key=lambda x: x[0]))
    out_stack = [in_ranges.pop(0)]

    for r in in_ranges:
        if r[0] > out_stack[-1][1]:
            out_stack.append(r)
        elif r[1] > out_stack[-1][1]:
            out_stack[-1] = (out_stack[-1][0], r[1])

    return out_stack


class ParserState(Enum):
    EXPECT_SEEDS = 1
    EXPECT_MAP_NAME = 2
    READ_MAP_RANGE = 3
    EXPECT_BLANK = 4


def parse_input(input):
    state = ParserState.EXPECT_SEEDS
    seeds = []
    maps = dict()
    last_map_name = None

    for line in input:
        if state == ParserState.EXPECT_SEEDS:
            _, list_input = line.split(":")
            seeds = [int(s) for s in list_input.split()]
            state = ParserState.EXPECT_BLANK
        elif state == ParserState.EXPECT_BLANK:
            assert line == ""
            state = ParserState.EXPECT_MAP_NAME
        elif state == ParserState.EXPECT_MAP_NAME:
            map_name_extractor = re.search("(\\w+)\\-to\\-(\\w+) map:", line)
            assert map_name_extractor

            from_name = map_name_extractor.group(1)
            to_name = map_name_extractor.group(2)

            last_map_name = f"{from_name}-to-{to_name}"
            maps[last_map_name] = RangeMap(from_name, to_name)

            state = ParserState.READ_MAP_RANGE
        elif state == ParserState.READ_MAP_RANGE:
            if line == "":
                state = ParserState.EXPECT_MAP_NAME
            else:
                range_extractor = re.search("(\\d+) (\\d+) (\\d+)", line)
                assert range_extractor

                dest_start = int(range_extractor.group(1))
                source_start = int(range_extractor.group(2))
                range_length = int(range_extractor.group(3))

                maps[last_map_name].add(
                    RangeEntry(source_start, dest_start, range_length)
                )

        else:
            raise Exception("unknown state in parser")

    return (seeds, maps)


class RangeMap:
    def __init__(self, from_name, to_name):
        self.from_name = from_name
        self.to_name = to_name
        self.entries = []

    def add(self, range):
        self.entries.append(range)

    def transform(self, v):
        for r in self.entries:
            v_new = r.map(v)
            if v_new is not None:
                return v_new

        return v


class RangeEntry:
    def __init__(self, source_start, dest_start, length):
        self.source_start = source_start
        self.dest_start = dest_start
        self.length = length

    def is_in_range(self, v):
        return v >= self.source_start and v < (self.source_start + self.length)

    def map(self, v):
        if self.is_in_range(v):
            return v - self.source_start + self.dest_start
        else:
            return None


class Solver(AdventDaySolver, day=5, year=2023, name="", solution=(3374647, 6082852)):
    def __init__(self, input):
        self.map_chain = [
            "seed-to-soil",
            "soil-to-fertilizer",
            "fertilizer-to-water",
            "water-to-light",
            "light-to-temperature",
            "temperature-to-humidity",
            "humidity-to-location",
        ]

        super().__init__(input)

    def transform_seed_to_location(self, seed):
        return self.transform_seed(seed, self.fast_forward_xform_chain)

    def transform_seed(self, seed, chain):
        for m in chain:
            seed = m.transform(seed)
        return seed

    def solve(self):
        self.seeds, self.maps = parse_input(self.input)

        # Asssemble a faster map transform chain w/out needing hashtables.
        self.fast_forward_xform_chain = [self.maps[n] for n in self.map_chain]

        # Part #1: Find the lowest location number of any initial seed.
        part_1 = min([self.transform_seed_to_location(s) for s in self.seeds])

        # Part #2: Same but with seed ranges.
        # range_count = len(self.seeds) / 2
        part_2 = None

        seed_ranges = [
            (self.seeds[i], self.seeds[i] + self.seeds[i + 1])
            for i in range(0, len(self.seeds), 2)
        ]

        with Pool(8) as p:
            part2_mins = p.map(self.find_min_for_seed_range, seed_ranges)
            print(part2_mins)
            part_2 = min(part2_mins)
            print(part_2)

        return (part_1, part_2)

    def find_min_for_seed_range(self, seed_range):
        start_seed = seed_range[0]
        end_seed = seed_range[1]
        total = end_seed - start_seed
        min_location = None

        for x in range(start_seed, end_seed):
            if (x - start_seed) % 1000000 == 0:
                percent = ((x - start_seed) * 100) / (end_seed - start_seed)
                remaining = end_seed - x

                print(
                    f"search seed range: [{start_seed}-{end_seed}] {end_seed-start_seed} seeds, {total} total, {remaining} remaining, {percent}% done"
                )

            location = self.transform_seed_to_location(x)

            if min_location is None or location < min_location:
                min_location = location

        print(f"potential min: {min_location}")
        return min_location


class Tests(AdventDayTestCase):
    def setUp(self):
        init_logging(logging.DEBUG)
        super().setUp(Solver)

    def test_sample(self):
        d = self._create_sample_solver(
            """seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4"""
        )
        s = d.solve()

        self.assertSequenceEqual([79, 14, 55, 13], d.seeds)
        seed_to_soil = d.maps["seed-to-soil"]
        self.assertEqual("seed", seed_to_soil.from_name)
        self.assertEqual(81, d.transform_seed(79, [seed_to_soil]))
        self.assertEqual(14, d.transform_seed(14, [seed_to_soil]))
        self.assertEqual(57, d.transform_seed(55, [seed_to_soil]))
        self.assertEqual(13, d.transform_seed(13, [seed_to_soil]))

        self.assertEqual(82, d.transform_seed_to_location(79))
        self.assertEqual(43, d.transform_seed_to_location(14))
        self.assertEqual(86, d.transform_seed_to_location(55))
        self.assertEqual(35, d.transform_seed_to_location(13))

        self.assertEqual(35, s[0])
        self.assertEqual(46, s[1])

    def test_real_input(self):
        # s = self._create_real_solver().solve()
        # self.assertEqual(3374647, s[0])
        # self.assertEqual(6082852, s[1])
        pass

    def test_merge_ranges(self):
        self.assertSequenceEqual([(10, 20)], merge_ranges([(10, 20)]))

        # merge overlapping
        self.assertSequenceEqual([(10, 25)], merge_ranges([(10, 20), (12, 25)]))
        self.assertSequenceEqual([(10, 25)], merge_ranges([(12, 25), (10, 20)]))

        # merge adjacent
        self.assertSequenceEqual([(10, 30)], merge_ranges([(10, 20), (20, 30)]))
        self.assertSequenceEqual([(6, 77)], merge_ranges([(6, 13), (13, 77)]))

        # skip if not overlapping or adjacent
        self.assertSequenceEqual([(5, 7), (8, 9)], merge_ranges([(5, 7), (8, 9)]))
        self.assertSequenceEqual([(6, 8), (10, 13)], merge_ranges([(10, 13), (6, 8)]))


if __name__ == "__main__":
    unittest.main()
