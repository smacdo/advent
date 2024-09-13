from dataclasses import dataclass
from advent.utils import split
from donner.annotations import example, solver
from donner.solution import AbstractSolver
import logging


@dataclass
class CubeSubset:
    blue: int
    red: int
    green: int


def parse_subset_text(text: str) -> CubeSubset:
    blue = 0
    red = 0
    green = 0

    for cube_text in split(text, ","):
        count, color_name = split(cube_text, " ")

        count = int(count.strip())

        if color_name == "blue":
            blue = count
        elif color_name == "red":
            red = count
        elif color_name == "green":
            green = count
        else:
            raise ValueError(f"unknown color name `{color_name}`")

    return CubeSubset(blue=blue, red=red, green=green)


def parse_game_line(line: str) -> tuple[int, list[CubeSubset]]:
    game_text, all_subsets_text = split(line, ":")
    subset_texts = split(all_subsets_text, ";")
    subsets = [parse_subset_text(c) for c in subset_texts]

    _, game_id = split(game_text, " ")

    return (int(game_id), subsets)


@solver(day=2, year=2023, name="Cube Conundrum")
@example(
    input=[
        "Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green",
        "Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue",
        "Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red",
        "Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red",
        "Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green",
    ],
    part_one="8",
    part_two="2286",
)
class Day2Solver(AbstractSolver):
    def part_one(self, input: str) -> int | str | None:
        MAX_RED = 12
        MAX_GREEN = 13
        MAX_BLUE = 14

        sum = 0

        for line in input.splitlines():
            logging.debug(line)
            game_id, cube_subsets = parse_game_line(line)

            # Examine each set of cubes in the game and make sure all of the sets
            # fit within the maximum allowed.
            all_ok = True

            for s in cube_subsets:
                if s.red > MAX_RED or s.green > MAX_GREEN or s.blue > MAX_BLUE:
                    logging.debug(
                        f"FAIL game={game_id} red={s.red} blue={s.blue} green={s.green}"
                    )
                    all_ok = False
                    break
                else:
                    logging.debug(
                        f"OK game={game_id} red={s.red} blue={s.blue} green={s.green}"
                    )

            # All of the subsets fit within the allowed cube color count. Add
            # this game to the running sum.
            if all_ok:
                logging.debug(f"SUCCEEDED {game_id}")
                sum += game_id

        return sum

    def part_two(self, input: str) -> int | str | None:
        sum = 0

        for line in input.splitlines():
            logging.debug(line)
            game_id, cube_subsets = parse_game_line(line)

            # To find the minimum number of cubes per color simply iterate
            # through each set and record the maximum number per color seen so
            # far.
            max_red = 0
            max_green = 0
            max_blue = 0

            for s in cube_subsets:
                max_red = max(max_red, s.red)
                max_green = max(max_green, s.green)
                max_blue = max(max_blue, s.blue)

            sum += max_red * max_green * max_blue

        return sum
