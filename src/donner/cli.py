from dataclasses import dataclass
from donner.client import (
    AocClientConfig,
    AocWebClient,
    ExpectedConfigKeyMissing,
)
from donner.data import (
    FileBackedPuzzleStore,
)
from donner.solution import (
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
import time

from donner.solver import (
    CheckHint,
    CheckResult,
    CheckResult_ExampleFailed,
    CheckResult_Ok,
    CheckResult_NotFinished,
    CheckResult_TooSoon,
    CheckResult_Wrong,
    RunSolverResult,
    SolverEventHandlers,
    run_solver,
)

logger = logging.getLogger(__name__)


# TODO: Rewrite error handling here. All log errors should be exceptions that are
#       caught at the top level and then reported as log errors.


@dataclass
class SolverRunInfo:
    start_time: float
    part_one_start_time: float | None = None
    part_two_start_time: float | None = None

    def try_get_part_start_time(self, part: Part) -> float | None:
        if part == Part.One:
            return self.part_one_start_time
        else:
            return self.part_two_start_time

    def get_part_start_time(self, part: Part) -> float:
        t = self.try_get_part_start_time(part)
        assert t is not None

        return t

    def set_part_start_time(self, part: Part, time: float):
        if part == Part.One:
            self.part_one_start_time = time
        else:
            self.part_two_start_time = time


class TerminalSolverEventHandlers(SolverEventHandlers):
    # example_start_time = time.time()
    # elapsed_seconds=time.time() - example_start_time,
    solver_start_times: dict[SolverMetadata, SolverRunInfo]

    def __init__(self) -> None:
        self.solver_start_times = dict()

    def on_start_solver(self, solver_metadata: SolverMetadata):
        self.solver_start_times[solver_metadata] = SolverRunInfo(time.time())

    def on_finish_solver(
        self, solver_metadata: SolverMetadata, result: RunSolverResult
    ):
        pass

    def on_start_part(self, solver_metadata: SolverMetadata, part: Part):
        pass

    def on_part_examples_pass(
        self, solver_metadata: SolverMetadata, part: Part, count: int
    ):
        if count > 0:
            print(
                f"👍 Tested the examples for year {solver_metadata.year()} day {solver_metadata.day()} {str(part).lower()}"
            )

        # Running the solver with real input happens immediately after this
        # event, so start the solver timer now.
        self.solver_start_times[solver_metadata].set_part_start_time(part, time.time())

    def on_finish_part(
        self,
        solver_metadata: SolverMetadata,
        part: Part,
        result: CheckResult,
    ):
        # Catch the examples failed condition early, and print it before trying
        # to calculate runtime of the solution which isn't possible because the
        # solution never ran.
        if type(result) is CheckResult_ExampleFailed:
            print(
                f"👎 The example output for {result.part} is `{result.example.output}` but the solver returned `{result.actual_answer}` using input:\n```\n{result.example.input}\n```"
            )
            return

        # Calculate the time elapsed since the examples completed and this event
        # indicating it finished.
        elapsed_seconds = time.time() - self.solver_start_times[
            solver_metadata
        ].get_part_start_time(part)

        if type(result) is CheckResult_Ok:
            print(f"✅ {part}: {result.actual_answer} [{elapsed_seconds:2f}s]")
        elif type(result) is CheckResult_TooSoon:
            # TODO: better message for too soon
            print(
                f"!!! Solution for {part} submitted too soon, please wait a bit before trying again !!!"
            )
        elif type(result) is CheckResult_NotFinished:
            print(f"👻 Answer for {part} is not finished")
        elif type(result) is CheckResult_Wrong:
            if result.hint is None:
                if result.expected_answer is None:
                    print(
                        f"❌ Wrong answer for {str(result.part).lower()}: {result.actual_answer} [{elapsed_seconds:2f}s]"
                    )
                else:
                    print(
                        f"❌ Wrong answer for {str(result.part).lower()} [{elapsed_seconds:2f}s]\n"
                        f"       Expected: {result.expected_answer}\n"
                        f"         Actual: {result.actual_answer}"
                    )
            else:
                too_what = "low" if result.hint == CheckHint.TooLow else "high"
                print(
                    f"❌ Wrong answer for {str(result.part).lower()}: {result.actual_answer} is too {too_what} [{elapsed_seconds:2f}s]"
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


def cli_main():
    registry = get_global_solver_registry()

    # Argument parsing.
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d",
        "--debug",
        help="Print debug log entries",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="Print verbose (info) log entries",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )

    subparsers = parser.add_subparsers(title="subcommands", dest="subparser_name")

    output_parser = subparsers.add_parser("output")
    output_parser.set_defaults(func=output)

    solve_parser = subparsers.add_parser("solve")
    solve_parser.add_argument(
        "days", type=int, nargs="+", default=[], help="a list of days to solve for"
    )
    solve_parser.add_argument(
        "-y",
        "--year",
        type=int,
        default=max(registry.all_years()),
        help="the year to solve for",
    )
    solve_parser.set_defaults(func=solve)

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    # Dispatch subcommand.
    #
    # TODO: Intercept common exceptions and print out helpful remediation messages.
    # TODO: cryptography.fernet.InvalidToken --> (probably) incorrect password
    # TODO: .aoc_config password or session_id missing

    try:
        if args.subparser_name == "output":
            pass
        elif args.subparser_name == "solve":
            year = args.year
            days = args.days if len(args.days) > 0 else registry.all_days(year)

            for day in days:
                solve(year=year, day=day)
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
