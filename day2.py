#!/usr/bin/env python3
import re


def main_1():
    max_red = 12
    max_green = 13
    max_blue = 14
    id_sum = 0

    with open("inputs/day2.txt", "r", encoding="utf-8") as file:
        for line in file:
            game_extractor = re.search("Game (\d+): (.*)", line)
            assert game_extractor

            game_id = int(game_extractor.group(1))
            sets = game_extractor.group(2).split(";")

            cube_sum = dict()

            for cube_set in sets:
                for cube_color_result in cube_set.split(","):
                    matcher = re.search("(\d+) (\w+)", cube_color_result)
                    assert matcher

                    count = int(matcher.group(1))
                    color = str(matcher.group(2))

                    if color not in cube_sum.keys():
                        cube_sum[color] = 0

                    cube_sum[color] = max(cube_sum[color], count)

            # print(f"{game_id}: {cube_sum}")

            print(cube_sum)

            if "red" in cube_sum.keys() and cube_sum["red"] > max_red:
                # print(f"SKIP red {cube_sum['red']} > {max_red}")
                continue
            elif "blue" in cube_sum.keys() and cube_sum["blue"] > max_blue:
                # print(f"SKIP blue {cube_sum['blue']} > {max_blue}")
                continue
            elif "green" in cube_sum.keys() and cube_sum["green"] > max_green:
                # print(f"SKIP green {cube_sum['green']} > {max_green}")
                continue
            else:
                id_sum += game_id
                print(f"ACCEPT {game_id} -> {id_sum}")
    print(f"sum of game_ids: {id_sum}")


def main_2():
    sum_cube_set_power = 0

    with open("inputs/day2.txt", "r", encoding="utf-8") as file:
        for line in file:
            game_extractor = re.search("Game (\d+): (.*)", line)
            assert game_extractor

            sets = game_extractor.group(2).split(";")
            cubes = dict()

            for cube_set in sets:
                for cube_color_result in cube_set.split(","):
                    matcher = re.search("(\d+) (\w+)", cube_color_result)
                    assert matcher

                    count = int(matcher.group(1))
                    color = str(matcher.group(2))

                    if color not in cubes.keys():
                        cubes[color] = count

                    cubes[color] = max(cubes[color], count)

            cube_set_power = 1

            for color, count in cubes.items():
                cube_set_power *= count

            print(f"{cubes} -> {cube_set_power} -> {sum_cube_set_power}")
            sum_cube_set_power += cube_set_power
    print(f"sum of cube set power: {sum_cube_set_power}")


if __name__ == "__main__":
    main_1()
    main_2()
