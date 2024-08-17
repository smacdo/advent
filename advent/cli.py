from abc import ABC, abstractmethod
from advent.aoc.client import AocClient, AocLoginConfig
from advent.data import (
    AnswerResponse,
    FileBackedPuzzleStore,
    PartAnswerCache,
    PuzzleData,
)
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


class CheckSolutionResult(ABC):
    part: Part

    def __init__(self, part: Part):
        self.part = part

    @abstractmethod
    def status_text(self) -> str:
        pass


class CheckSolutionResult_NotFinished(CheckSolutionResult):
    def __init__(self, part: Part):
        super().__init__(part)

    def status_text(self) -> str:
        return f"👻 Answer for {self.part} is not finished"


class CheckSolutionResult_Ok(CheckSolutionResult):
    answer: int | str | None

    def __init__(self, part: Part, answer: int | str):
        super().__init__(part)
        self.answer = answer

    def status_text(self) -> str:
        return f"✅ {self.part}: {self.answer}"


class CheckSolutionResult_Wrong(CheckSolutionResult):
    actual_answer: int | str | None
    expected_answer: int | str | None

    def __init__(
        self, part: Part, actual_answer: int | str, expected_answer: int | str | None
    ):
        super().__init__(part)
        self.actual_answer = actual_answer
        self.expected_answer = expected_answer

    def status_text(self) -> str:
        if self.expected_answer is None:
            return f"❌ Wrong answer for {str(self.part).lower()}: {self.actual_answer}"
        else:
            return (
                f"❌ Wrong answer for {str(self.part).lower()}\n"
                f"       Expected: {self.expected_answer}\n"
                f"         Actual: {self.actual_answer}"
            )


class CheckSolutionResult_TooHigh(CheckSolutionResult):
    actual_answer: int | str | None

    def __init__(self, part: Part, actual_answer: int | str):
        super().__init__(part)
        self.actual_answer = actual_answer

    def status_text(self) -> str:
        return f"❌ Wrong answer for {str(self.part).lower()}: {self.actual_answer} is too high"


class CheckSolutionResult_TooLow(CheckSolutionResult):
    actual_answer: int | str | None

    def __init__(self, part: Part, actual_answer: int | str):
        super().__init__(part)
        self.actual_answer = actual_answer

    def status_text(self) -> str:
        return f"❌ Wrong answer for {str(self.part).lower()}: {self.actual_answer} is too low"


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


def check_solution(
    part: Part, solution: int | str | None, answer_cache: PartAnswerCache
) -> CheckSolutionResult:
    # TODO: Split the printing from the checking and also make it easier to count # OK vs FAIL
    if solution is None:
        return CheckSolutionResult_NotFinished(part)

    if answer_cache.correct_answer is not None:
        if solution == answer_cache.correct_answer:
            return CheckSolutionResult_Ok(part, solution)
        else:
            return CheckSolutionResult_Wrong(
                part, answer_cache.correct_answer, solution
            )
    else:
        # Use the answer cache to see if there is already a result for this
        # solution.
        answer_response = answer_cache.check_answer(solution)

        # The cache doesn't have enough information to check if the answer is
        # correct or not. Try to submit a response to the AOC backend and see
        # what it says about the solution.
        if answer_response == AnswerResponse.Unknown:
            # TODO: Check the answer by submitting it to the client and seeing what
            #       the response is.
            # TODO: Update the answer cache with the response.
            raise Exception("submitting answers not implemented yet")

        # Convert the answer cache's response to a result that can be used by
        # the solution runner framework when returned from this method.
        if answer_response == AnswerResponse.Ok:
            return CheckSolutionResult_Ok(part, solution)
        elif answer_response == AnswerResponse.Wrong:
            return CheckSolutionResult_Wrong(
                part, actual_answer=solution, expected_answer=None
            )
        elif answer_response == AnswerResponse.TooLow:
            return CheckSolutionResult_TooLow(part, solution)
        elif answer_response == AnswerResponse.TooHigh:
            return CheckSolutionResult_TooHigh(part, solution)
        else:
            raise ValueError("Unhandled enum value for AnswerResponse")


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
    print(check_solution(Part.One, part_one, puzzle.part_one_answer).status_text())

    part_two = solver.part_two(puzzle.input)
    print(check_solution(Part.Two, part_two, puzzle.part_two_answer).status_text())

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
