from dataclasses import dataclass
from advent.utils import find_ints, find_digits, digits_to_int
from donner.annotations import example, solver
from donner.solution import AbstractSolver
import logging
import math


@dataclass
class Race:
    time: int
    distance_record: int


def parse_race_sheet_many(input: str) -> list[Race]:
    lines = input.splitlines()

    assert len(lines) == 2
    assert lines[0].startswith("Time:")
    assert lines[1].startswith("Distance:")

    all_times = find_ints(lines[0])
    all_distances = find_ints(lines[1])

    return [Race(time=t, distance_record=d) for t, d in zip(all_times, all_distances)]


def parse_race_sheet_single(input: str) -> Race:
    lines = input.splitlines()

    assert len(lines) == 2
    assert lines[0].startswith("Time:")
    assert lines[1].startswith("Distance:")

    time = digits_to_int(find_digits(lines[0]))
    distance = digits_to_int(find_digits(lines[1]))

    return Race(time=time, distance_record=distance)


def count_ways_to_win(time: int, distance_record: int) -> int:
    """
    The minimum and maximum amount of time you can hold the acceleration to
    beat the record is findable by solving a quadratic equation.

    Keys:
     t = total time
     m = time spent holding the button
     r = record

     formula:
      original      : m(t - m) >= r
      move r to left: m(t - m) - r >= 0
      expand        : mt - m^2 - r >= 0
      rearrange     : -m^2 + mt - r >= 0

      apply quadratic formula
       a = -1
       b = t = total time
       c = -r = -record distance

     solution:
      (t - sqrt(t^2 - 4r)) / 2 < m < (t + sqrt(t^2 - 4r)) / 2
    """
    discriminant = (time * time) - 4 * distance_record

    if discriminant < 0:
        raise Exception(f"no solution for time={time}, dist={distance_record}")
    else:
        min_time_to_hold = (time - math.sqrt(discriminant)) / 2
        max_time_to_hold = (time + math.sqrt(discriminant)) / 2

        logging.debug(
            f"min = {min_time_to_hold}, max = {max_time_to_hold}, t = {time}, s = {distance_record}, d = {discriminant}"
        )

        # There is a weird edge case here when when the roots (min, max time)
        # are both integers. This edge arises because you have to _beat_ the
        # record not just match it, so `>=` rather than `=`.
        #
        # A simpler fix than checking for the integer case is to flip the floor
        # and ceil around, and subtract rather than add one.
        #
        # See:
        # https://www.reddit.com/r/adventofcode/comments/18c08xh/2023_day_06_stable_math_solution/
        return int(math.ceil(max_time_to_hold) - math.floor(min_time_to_hold) - 1)


@solver(day=6, year=2023, name="Wait For It")
@example(
    input=["Time:      7  15   30", "Distance:  9  40  200"],
    part_one="288",
    part_two="71503",
)
class Day6Solver(AbstractSolver):
    def part_one(self, input: str) -> int | str | None:
        sum = 1

        for r in parse_race_sheet_many(input):
            sum *= count_ways_to_win(time=r.time, distance_record=r.distance_record)

        return sum

    def part_two(self, input: str) -> int | str | None:
        race = parse_race_sheet_single(input)
        return count_ways_to_win(time=race.time, distance_record=race.distance_record)
