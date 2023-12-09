#!/usr/bin/env python3
import argparse

from advent.days import *  # noqa: F403
from advent.utils import AdventDaySolver, load_input


def solve(day, year):
    solver_type = AdventDaySolver.get_solver(day, year)
    solver = solver_type(load_input(day=day, year=year))
    solution = solver.solve()

    print(f"Solution for day {day} {year}")
    print(f"    part 1: {solution[0]}")
    print(f"    part 2: {solution[1]}")


def solve_all():
    for year in AdventDaySolver.years():
        for day in AdventDaySolver.days(year):
            s = AdventDaySolver.new_solver(day, year)
            answer = s.solve()

            part_1 = format_answer(answer[0], type(s).solution()[0])
            part_2 = format_answer(answer[0], type(s).solution()[0])

            print(f"Day {s.day()} - {s.name()}: {part_1}, {part_2}")


def format_answer(actual, expected):
    if actual is None:
        # Answer is missing - the solver has not been completed.
        return "❗"
    elif actual != expected:
        return f"{actual} ❌"
    else:
        return f"{actual} ✅"


def pretty_print_year(year):
    print(f"Year {year}:")
    for day in AdventDaySolver.days(year):
        print(f"    - Day {day}")


def main():
    # TODO: Set year default to most recent year for which a solver is available.
    default_year = 2023

    # Parse arguments.
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="", dest="action")

    solve_subparser = subparsers.add_parser("solve", help="run a solver")
    solve_subparser.add_argument("day")
    solve_subparser.add_argument("year", default=default_year)

    list_subparser = subparsers.add_parser("list", help="list of solvers")
    list_subparser.add_argument("year", nargs="?", default=default_year)

    # Dispatch to a solver if requested otherwise print out a list of available
    # solvers.
    args = parser.parse_args()

    if args.action == "solve":
        # Solve the request day.
        solve(args.day, args.year)
    elif args.action == "list":
        # Print a list of available days.
        if args.year is None:
            for year in AdventDaySolver.years():
                pretty_print_year(year)
        else:
            pretty_print_year(args.year)
    else:
        solve_all()


if __name__ == "__main__":
    main()
