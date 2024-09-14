from dataclasses import dataclass
from advent.utils import Range, merge_ranges, not_none, split
from donner.annotations import example, solver
from donner.solution import AbstractSolver


@dataclass
class Map:
    name: str
    ranges: list[tuple[Range, Range]]  # [(source, dest)]

    def add(self, source: Range, dest: Range):
        def key(v: tuple[Range, Range]):
            return v[0].start

        self.ranges.append((source, dest))
        self.ranges.sort(key=key)

    def apply(self, value: int) -> int:
        for source, dest in self.ranges:
            if value in source:
                delta = dest.start - source.start
                return value + delta

        return value


@dataclass
class Almanac:
    seeds: list[int]
    maps: list[Map]


def parse_almanac(almanac_text: str) -> Almanac:
    lines = almanac_text.splitlines()
    seeds_line = lines[0]
    map_lines = lines[2:]

    # Parse the seeds
    _, seeds_list_text = split(seeds_line, ":")
    seeds = [int(s) for s in split(seeds_list_text, " ")]

    # Parse each X to Y map section.
    maps: list[Map] = []

    for line in map_lines:
        if len(line) == 0:
            continue

        if line.endswith("map:"):
            name, _ = split(line, " ")
            maps.append(Map(name, []))
        else:
            range_parts = [int(x) for x in split(line, " ")]
            dest = Range(start=range_parts[0], length=range_parts[2])
            source = Range(start=range_parts[1], length=(range_parts[2]))

            maps[-1].add(source=source, dest=dest)

    return Almanac(seeds=seeds, maps=maps)


@solver(day=5, year=2023, name="If You Give A Seed A Fertilizer")
@example(
    input=[
        "seeds: 79 14 55 13",
        "",
        "seed-to-soil map:",
        "50 98 2",
        "52 50 48",
        "",
        "soil-to-fertilizer map:",
        "0 15 37",
        "37 52 2",
        "39 0 15",
        "",
        "fertilizer-to-water map:",
        "49 53 8",
        "0 11 42",
        "42 0 7",
        "57 7 4",
        "",
        "water-to-light map:",
        "88 18 7",
        "18 25 70",
        "",
        "light-to-temperature map:",
        "45 77 23",
        "81 45 19",
        "68 64 13",
        "",
        "temperature-to-humidity map:",
        "0 69 1",
        "1 0 69",
        "",
        "humidity-to-location map:",
        "60 56 37",
        "56 93 4",
    ],
    part_one="35",
    part_two="46",
)
class Day5Solver(AbstractSolver):
    def part_one(self, input: str) -> int | str | None:
        almanac = parse_almanac(input)
        locations: list[int] = []

        for i in range(0, len(almanac.seeds)):
            v = almanac.seeds[i]

            for map in almanac.maps:
                v = map.apply(v)

            locations.append(v)

        return min(locations)

    def part_two(self, input: str) -> int | str | None:
        almanac = parse_almanac(input)

        # Transform each "seed range" in the input to the final location range.
        # Convert the "seeds" in the input to seed ranges.
        location_ranges: list[Range] = []

        for seed_i in range(0, len(almanac.seeds), 2):
            seed_range = Range(almanac.seeds[seed_i], length=almanac.seeds[seed_i + 1])
            ranges_to_map = [seed_range]
            mapped_ranges = []

            # Iterate through each transform in the map for the seed input range.
            for map in almanac.maps:
                mapped_ranges.clear()

                # Iterate through each range that hasn't been transformed yet in
                # this map round.
                for r in ranges_to_map:
                    next_r = r

                    # Iterate through each src -> dest pair in the current map.
                    # Note that this list is ordered meaning every following src
                    # is larger than the previous.
                    for src, dest in map.ranges:
                        if next_r is None:
                            break

                        # If the [src, src+len] range overlaps the unmapped
                        # range then split it up.
                        #
                        # Any range preceding `src` will never be mapped (because
                        # it is sorted) so just add it to the output.
                        #
                        # The inner range (second tuple member) is added to the
                        # output after applying the src -> dest mapping.
                        #
                        # The range after `src` might still have a future src
                        # that will apply. Copy it to `next_r` and process it
                        # next before moving on.
                        if next_r.overlaps(src):
                            before, inner, after = not_none(next_r.split(src))
                            next_r = after

                            if before is not None:
                                mapped_ranges.append(before)

                            # Apply the src -> dest mapping.
                            delta = dest.start - src.start
                            inner.start += delta

                            mapped_ranges.append(inner)

                    # After all the src ranges are checked we can consider any
                    # remaining chunk to be unmapped. Copy it to the output
                    # bucket.
                    if next_r is not None:
                        mapped_ranges.append(next_r)

                # Merge the ranges as an optimization step before moving to the
                # next map round.
                merge_ranges(mapped_ranges)
                ranges_to_map = list(mapped_ranges)

            # Finished iterating through all of the map transforms for this
            # seed range.
            location_ranges += mapped_ranges

        return min(location_ranges, key=lambda x: x.start).start
