#!/usr/bin/env python3
import logging
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


def main():
    # The maximum number of cubes of each color loaded in the bag (part 1).
    MAX_CUBES = {"red": 12, "green": 13, "blue": 14}

    sum_cube_set_power = 0
    id_sum = 0

    # Open the inputs file and calculate both solutions at the same time:
    with open("inputs/day2.txt", "r", encoding="utf-8") as file:
        # Treat each line in the input file as a separate game result:
        for line in file:
            # Parse the line into structured representation of the text.
            # (game_id, [{"red?": i, "blue?": j, "green?": k}...])
            (game_id, cube_sets) = parse_game_results(line)
            logging.debug(f"GAME {game_id} START: {cube_sets}")

            # Track the maximum number of cubes of each color seen in a set from
            # this game. Each game may have multiple sets.
            max_cubes = dict()

            # Go through each set in this game.
            for cube_set in cube_sets:
                # Go through each color in the game, and track the maximm count
                # of each cube color.
                for color, count in cube_set.items():
                    if color not in max_cubes.keys():
                        max_cubes[color] = count

                    max_cubes[color] = max(max_cubes[color], count)
                    logging.debug(
                        "find max_cubes, curr: {count} {color} -> {max_cubes}"
                    )

            logging.debug(f"max_cubes: {max_cubes}")

            # Part 1 calculation:
            #
            # Check that none of the colored cube counts exceeded the maximum
            # allowed amount set at the start.
            #
            # If the game is valid then add the game_id to the running sum which
            # will be reported as the anwer to part 1.
            valid = True

            for COLOR, COUNT in MAX_CUBES.items():
                if COLOR in max_cubes.keys() and max_cubes[COLOR] > COUNT:
                    logging.debug(f"SKIP {COLOR} {max_cubes[COLOR]} > {COUNT}")
                    valid = False

            if valid:
                id_sum += game_id
                logging.debug(f"ACCEPT {game_id} -> {id_sum}")

            # Part 2 calculation:
            #
            # Calculate the fewest number of cubes of each color that could have
            # been in the bag which is the same as what `max_cubes[]` captured.
            #
            # The part 2 solution is summation of all the minimum cube color
            # counts multiplied together as seen below.
            cube_set_power = 1

            for color, count in max_cubes.items():
                cube_set_power *= count

            sum_cube_set_power += cube_set_power
            logging.debug(f"{cube_set_power} -> {sum_cube_set_power}")

            # Log traces for when we _really_ want to debug what's going on.
            logging.debug("GAME {game_id} DONE")

    # Print the solutions to both parts for day 2.
    logging.info(f"part 1: {id_sum}")
    logging.info(f"part 2: {sum_cube_set_power}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
