from advent.aoc.client import AocClient, AocLoginConfig
from advent.data import FileBackedPuzzleStore, PuzzleData
from advent.solution import (
    AbstractSolver,
    Example,
    Part,
    get_global_advent_year_registry,
    get_part_examples_for_solver,
)
from pathlib import Path

import argparse
import importlib
import logging

logger = logging.getLogger(__name__)

# TODO: Rewrite error handling here. All log errors should be exceptions that are
#       caught at the top level and then reported as log errors.


def create_aoc_client() -> AocClient | None:
    # Load the AOC session cookie
    login_config = AocLoginConfig.try_load_from_file(".aoc_login")

    if login_config is None:
        logging.error(".aoc_login file is missing")
        logging.error(
            "***** Please copy your adventofcode.com session cookie to .aoc_session *****"
        )
        return None

    # OK
    return AocClient(login_config)


class AdventUserException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AdventSolutionMissing(AdventUserException):
    def __init__(self, year: int, day: int, expected_module: str) -> None:
        super().__init__(
            f"There is no solution implemented for year {year} day {day} (expected module at: {expected_module})"
        )


class ExampleFailed(AdventUserException):
    def __init__(self, actual_output: str | None, example: Example):
        super().__init__(
            f"Example for {example.part} expected `{example.output}` but solver returned `{actual_output}` with input:\n```\n{example.input}\n```"
        )


def check_examples(solver_class: type[AbstractSolver]):
    for example in get_part_examples_for_solver(solver_class, Part.One):
        solver = solver_class()
        result = solver.part_one(example.input)

        if not example.output == result:
            raise ExampleFailed(result, example)

    for example in get_part_examples_for_solver(solver_class, Part.Two):
        solver = solver_class()
        result = solver.part_two(example.input)

        if not example.output == result:
            raise ExampleFailed(result, example)


def check_result(part_name: str, expected: str | None, actual: str | None) -> bool:
    # TODO: Split the printing from the checking and also make it easier to count # OK vs FAIL
    if actual is None:
        # TODO: Better exception
        raise Exception(f"{part_name} answer data is missing")

    if expected is None:
        print("👻 Answer for {part_name} is not finished")
    else:
        if expected == actual:
            print(f"✅ {part_name}: {actual}")
            return True
        else:
            print(f"❌ Wrong answer for {part_name}")
            print(f"  Expected: {expected}")
            print(f"    Actual: {actual}")

    return False


# TODO: Modularize this code.
# TODO: Inject a fake AOC client and then test it as well!
# TODO: Inject a fake module discovery interface.
def solve(args):
    year = 2023
    day = 1

    #
    aoc_client = create_aoc_client()

    if aoc_client is None:
        return

    # Get a list of available solver classes, and create the requested solver.
    # If there is no solver for the requested day then print an error and return
    # to the caller.
    # TODO: Do the discovery and loading dynamically.
    module_name = f"advent.solutions.y2023.day{day}"
    importlib.import_module(module_name)

    registry = get_global_advent_year_registry(year)

    if not registry.has_solution_for_day(day):
        raise AdventSolutionMissing(year, day, module_name)

    solver = registry.create_solver(day)

    # Load puzzle data (inputs and answers) from disk. If there is no puzzle
    # data for the selected day then try to load it from the AOC website.
    # TODO: Handle if the data is missing.
    puzzle_store = FileBackedPuzzleStore(Path("data"), year)

    if not puzzle_store.has_day(day):
        logger.debug("puzzle data is missing for year {year} day {day}")

        # The puzzle data for this day is missing. Try to load it from the AOC
        # website.
        # TODO: Raise an exception with helpful text if data cannot be fetched.
        input = aoc_client.fetch_input_for(year, day)
        puzzle_store.set(
            day, PuzzleData(input=input, part_one_answer=None, part_two_answer=None)
        )

        logger.info("puzzle input for year {year} day {day} has been loaded and cached")

    puzzle = puzzle_store.get(day)

    # Validate any examples first to check the state of the solver.
    check_examples(type(solver))
    print("✅ examples are good")

    # Compute the part one and part two answers using the puzzle's input.
    #
    # Check if the answers for part one and part two match the expected puzzle
    # outputs. If these outputs are not available try to load them from the AOC
    # website.
    #
    # TODO: Submit an answer if the answer data is missing.
    # TODO: Store correct answers when answer data is missing.
    # TODO: Store incorrect answer along with hints.
    part_one = solver.part_one(puzzle.input)
    check_result("part one", part_one, puzzle.part_one_answer)

    part_two = solver.part_two(puzzle.input)
    check_result("part two", part_two, puzzle.part_two_answer)

    # Print out run time statistics before exiting.

    # Done!
    return


def sync(args):
    # Load the AOC session cookie
    login_config = AocLoginConfig.try_load_from_file(".aoc_login")

    if login_config is None:
        logging.error(".aoc_login file is missing")
        logging.error(
            "***** Please copy your adventofcode.com session cookie to .aoc_session *****"
        )
        return

    # OK
    aoc_client = AocClient(login_config)
    print([str(s) for s in aoc_client.fetch_days(2023)])

    print("TODO: sync")


def main():
    # Argument parsing.
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="subcommands", dest="subparser_name")

    sync_parser = subparsers.add_parser("sync")
    sync_parser.set_defaults(func=sync)

    solve_parser = subparsers.add_parser("solve")
    solve_parser.set_defaults(func=solve)

    args = parser.parse_args()

    # Dispatch subcommand.
    if args.subparser_name == "sync":
        return sync(args)
    elif args.subparser_name == "solve":
        return solve(args)


main()
