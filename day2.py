#!/usr/bin/env python3
import re


def parse_game_results(s):
    game_extractor = re.search("Game (\d+): (.*)", s)
    assert game_extractor

    game_id = int(game_extractor.group(1))
    cube_sets_results = game_extractor.group(2).split(";")
    cube_sets = []

    for cube_set_result in cube_sets_results:
        cube_sets.append(parse_cube_set(cube_set_result))

    return (game_id, cube_sets)


def parse_cube_set(s):
    """NUM COLOR, NUM COLOR..."""
    cubes = dict()

    for cube_color_result in s.split(","):
        (color, count) = parse_cube_color_count(cube_color_result)
        cubes[color] = count

    return cubes


def parse_cube_color_count(s):
    """Parses a count followed by a cube color, eg '3 blue'"""
    matcher = re.search("(\d+) (\w+)", s)
    assert matcher

    count = int(matcher.group(1))
    color = str(matcher.group(2))

    return (color, count)


def main_1():
    MAX_CUBES = {"red": 12, "green": 13, "blue": 14}
    id_sum = 0

    with open("inputs/day2.txt", "r", encoding="utf-8") as file:
        for line in file:
            (game_id, cube_sets) = parse_game_results(line)
            max_cubes = dict()

            for cube_set in cube_sets:
                for color, count in cube_set.items():
                    if color not in max_cubes.keys():
                        max_cubes[color] = count

                    max_cubes[color] = max(max_cubes[color], count)

            valid = True

            for COLOR, COUNT in MAX_CUBES.items():
                if COLOR in max_cubes.keys() and max_cubes[COLOR] > COUNT:
                    # print(f"SKIP {COLOR} {max_cubes[COLOR]} > {COUNT}")
                    valid = False

            if valid:
                id_sum += game_id
                # print(f"ACCEPT {game_id} -> {id_sum}")
    print(f"sum of game_ids: {id_sum}")


def main_2():
    sum_cube_set_power = 0

    with open("inputs/day2.txt", "r", encoding="utf-8") as file:
        for line in file:
            (game_id, cube_sets) = parse_game_results(line)
            max_cubes = dict()

            for cube_set in cube_sets:
                for color, count in cube_set.items():
                    if color not in max_cubes.keys():
                        max_cubes[color] = count

                    max_cubes[color] = max(max_cubes[color], count)

            cube_set_power = 1

            for color, count in max_cubes.items():
                cube_set_power *= count

            sum_cube_set_power += cube_set_power

    print(f"sum of cube set power: {sum_cube_set_power}")


if __name__ == "__main__":
    main_1()
    main_2()
