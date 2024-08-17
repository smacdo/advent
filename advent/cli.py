from advent.aoc.client import AocClient, AocLoginConfig
from advent.data import FileBackedPuzzleStore, PuzzleData
from advent.plugins import load_all_solutions
from advent.solution import (
    AbstractSolver,
    Example,
    Part,
    SolverMetadata,
    get_global_solver_registry,
)
from pathlib import Path

import argparse
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
    def __init__(self, year: int, day: int) -> None:
        super().__init__(
            f"‼️ There is no code implementing a solution for year {year} day {day} (expected file `advent/solutions/y{year}/day{day}.py`)",
        )


class ExampleFailed(AdventUserException):
    def __init__(self, actual_output: str | None, example: Example):
        super().__init__(
            f"👎 The example output for {example.part} is `{example.output}` but the solver returned `{actual_output}` using input:\n```\n{example.input}\n```",
        )


def output(args):
    # TODO: Print output for the listed day.
    pass


def check_examples(solver_class: type[AbstractSolver]):
    """
    Checks the example inputs for `solver_class` match the example outputs when
    instantiating a new instance of `solver_class` and running the inputs through
     `part_one` and `part_two` methods.
    """
    for example in get_global_solver_registry().get_examples(solver_class, Part.One):
        solver = solver_class()
        result = solver.part_one(example.input)

        if not example.output == result:
            raise ExampleFailed(str(result), example)

    for example in get_global_solver_registry().get_examples(solver_class, Part.Two):
        solver = solver_class()
        result = solver.part_two(example.input)

        if not example.output == result:
            raise ExampleFailed(str(result), example)


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


def cli_solve(args):
    load_all_solutions()
    solve(2023, 1)


# TODO: Modularize this code.
# TODO: Inject a fake AOC client and then test it as well!
# TODO: Inject a fake module discovery interface.
def solve(year: int, day: int):
    #
    aoc_client = create_aoc_client()

    if aoc_client is None:
        return

    # Get a list of available solver classes, and create the requested solver.
    # If there is no solver for the requested day then print an error and return
    # to the caller.
    registry = get_global_solver_registry()

    if not registry.has_solver_for(year, day):
        raise AdventSolutionMissing(year, day)

    # Check if the puzzle input is cached on disk. If the input for this puzzle
    # are missing then load the inputs from the network.
    store = FileBackedPuzzleStore(Path("data"))

    if not store.has_day(year, day):
        logger.debug("puzzle data is missing for year {year} day {day}")

        # The puzzle data for this day is missing. Try to load it from the AOC
        # website.
        # TODO: Raise an exception with helpful text if data cannot be fetched.
        input = aoc_client.fetch_input_for(year, day)
        store.add_day(year, day, input)

        logger.info("puzzle input for year {year} day {day} has been loaded and cached")

    puzzle = store.get(year, day)

    #
    run_solver(
        solver_info=registry.find_solver_for(year, day),
        puzzle=puzzle,
        client=aoc_client,
    )

    # Check if the puzzle answers were modified. If so then persist the new
    # puzzle data to disk.
    og_puzzle = store.get(year, day)

    if puzzle != og_puzzle:
        # TODO: log
        store.set(year, day, puzzle)

    # Print out run time statistics before exiting.


def run_solver(solver_info: SolverMetadata, puzzle: PuzzleData, client: AocClient):
    solver = solver_info.create_solver_instance()
    year = solver_info.year()
    day = solver_info.day()

    # Validate any examples first to check the state of the solver.
    check_examples(type(solver))
    print(f"👍 Tested the examples for year {year} day {day} in the solver")

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
    check_result("Part one", str(part_one), puzzle.part_one_answer.correct_answer)

    part_two = solver.part_two(puzzle.input)
    check_result("Part two", str(part_two), puzzle.part_two_answer.correct_answer)

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

    output_parser = subparsers.add_parser("output")
    output_parser.set_defaults(func=output)

    solve_parser = subparsers.add_parser("solve")
    solve_parser.set_defaults(func=solve)

    sync_parser = subparsers.add_parser("sync")
    sync_parser.set_defaults(func=sync)

    args = parser.parse_args()

    # Dispatch subcommand.
    if args.subparser_name == "output":
        pass
    elif args.subparser_name == "solve":
        return cli_solve(args)
    elif args.subparser_name == "sync":
        return sync(args)


main()
