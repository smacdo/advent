from advent.client import (
    AocClientConfig,
    AocWebClient,
    ExpectedConfigKeyMissing,
)
from advent.data import (
    FileBackedPuzzleStore,
)
from advent.plugins import load_all_solutions
from advent.solution import (
    MaybeAnswerType,
    Part,
    SolverMetadata,
    get_global_solver_registry,
)
from pathlib import Path

import argparse
import cryptography.fernet
import logging
import os
import shutil
import sys

from advent.solver import (
    CheckHint,
    CheckResult,
    CheckResult_ExampleFailed,
    CheckResult_NotFinished,
    CheckResult_Wrong,
    SolverEventHandlers,
    run_solver,
)

logger = logging.getLogger(__name__)


# TODO: Rewrite error handling here. All log errors should be exceptions that are
#       caught at the top level and then reported as log errors.


class TerminalSolverEventHandlers(SolverEventHandlers):
    def on_examples_passed(self, solver_metadata: SolverMetadata):
        print(
            f"👍 Tested the examples for year {solver_metadata.year()} day {solver_metadata.day()} in the solver"
        )

    def on_part_ok(
        self, answer: MaybeAnswerType, solver_metadata: SolverMetadata, part: Part
    ):
        print(f"✅ {part}: {answer}")

    def on_part_wrong(
        self, result: CheckResult, solver_metadata: SolverMetadata, part: Part
    ):
        if type(result) is CheckResult_ExampleFailed:
            print(
                f"👎 The example output for {result.part} is `{result.example.output}` but the solver returned `{result.actual_answer}` using input:\n```\n{result.example.input}\n```"
            )
        elif type(result) is CheckResult_NotFinished:
            print(f"👻 Answer for {part} is not finished")
        elif type(result) is CheckResult_Wrong:
            if result.hint is None:
                if result.expected_answer is None:
                    print(
                        f"❌ Wrong answer for {str(result.part).lower()}: {result.actual_answer}"
                    )
                else:
                    print(
                        f"❌ Wrong answer for {str(result.part).lower()}\n"
                        f"       Expected: {result.expected_answer}\n"
                        f"         Actual: {result.actual_answer}"
                    )
            else:
                too_what = "low" if result.hint == CheckHint.TooLow else "high"
                print(
                    f"❌ Wrong answer for {str(result.part).lower()}: {result.actual_answer} is too {too_what}"
                )


def create_aoc_client() -> AocWebClient | None:
    # Check for the existence of the AOC client config on disk. If it doesn't
    # exist try to create it, and then exit early with a message to the user to
    # finish configuring it.
    if not os.path.exists(".aoc_config"):
        shutil.copy(".aoc_config.template", ".aoc_config")

        # TODO: better message to the user.
        logging.error(".aoc_config initialized - please fill out correct values")

    # Load the AOC client configuration file from disk.
    return AocWebClient(AocClientConfig.load_from_file(".aoc_config"))


class AdventUserException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AdventSolutionMissing(AdventUserException):
    def __init__(self, year: int, day: int) -> None:
        super().__init__(
            f"‼️ There is no code implementing a solution for year {year} day {day} (expected file `advent/solutions/y{year}/day{day}.py`)",
        )


def output(args):
    # TODO: Print output for the listed day.
    pass


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
    store = FileBackedPuzzleStore(Path("data"), password=aoc_client.config.password)

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
        solver_metadata=registry.find_solver_for(year, day),
        puzzle=puzzle,
        client=aoc_client,
        events=TerminalSolverEventHandlers(),
    )

    # Check if the puzzle answers were modified. If so then persist the new
    # puzzle data to disk.
    og_puzzle = store.get(year, day)

    if puzzle != og_puzzle:
        # TODO: log
        store.set(year, day, puzzle)

    # Print out run time statistics before exiting.


def sync(args):
    # Load the AOC session cookie
    # TODO: error handling fix
    login_config = AocClientConfig.load_from_file(".aoc_login")

    if login_config is None:
        logging.error(".aoc_login file is missing")
        logging.error(
            "***** Please copy your adventofcode.com session cookie to .aoc_session *****"
        )
        return

    # OK
    aoc_client = AocWebClient(login_config)
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
    #
    # TODO: Intercept common exceptions and print out helpful remediation messages.
    # TODO: cryptography.fernet.InvalidToken --> (probably) incorrect password
    # TODO: .aoc_config password or session_id missing
    try:
        if args.subparser_name == "output":
            pass
        elif args.subparser_name == "solve":
            return cli_solve(args)
        elif args.subparser_name == "sync":
            return sync(args)
        else:
            parser.print_help(sys.stderr)
            sys.exit(1)
    except cryptography.fernet.InvalidToken as e:
        logging.exception(e)

        print("")
        print("Could not decrypt puzzle inputs stored on the local machine")
        print(
            "Try checking the password setting in your .aoc_config to make sure it is correct. If the issue persists you can delete the puzzle data cache and start over."
        )
        print("")
    except ExpectedConfigKeyMissing as e:
        logging.exception(e)

        print("")
        print(f"The configuration setting `{e.key}` was missing or empty")
        print(f"Fix the `{e.key} = ...` line in the file {e.config_path}")
        print("")


main()
