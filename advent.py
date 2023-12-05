#!/usr/bin/env python3
import argparse

# TODO: Is it possible to eliminate all of the imports and auto-discover?
import day1
import day2
import day3
import day4

from utils import AdventDaySolver

def solve(day, year):
  solver = AdventDaySolver.new_solver(day, year)
  solution = solver.solve()

  print(f"Solution for day {day} {year}")
  print(f"    part 1: {solution[0]}")
  print(f"    part 2: {solution[1]}")

def list(year = None):
  if year is None:
    for year in AdventDaySolver.years():
      pretty_print_year(year)
  else:
    pretty_print_year(year)

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
  args.action = args.action if args.action is not None else "list"
  
  if args.action == "solve":
    solve(args.day, args.year)
  elif args.action == "list":
    year = args.year if "year" in args else None
    list(year)


if __name__ == "__main__":
  main()