from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from advent.aoc.client import AocClient
from advent.data import AnswerResponse, PartAnswerCache, PuzzleData
from advent.solution import AbstractSolver, Example, Part, SolverMetadata


class CheckResult(ABC):
    part: Part

    def __init__(self, part: Part):
        self.part = part

    def is_ok(self) -> bool:
        return False


@dataclass
class CheckResult_Ok(CheckResult):
    def __init__(self, part: Part):
        super().__init__(part)

    def is_ok(self) -> bool:
        return True


@dataclass
class CheckResult_NotFinished(CheckResult):
    def __init__(self, part: Part):
        super().__init__(part)


class CheckHint(Enum):
    TooLow = 1
    TooHigh = 2


@dataclass
class CheckResult_Wrong(CheckResult):
    actual_answer: int | str | None
    expected_answer: int | str | None
    hint: CheckHint | None

    def __init__(
        self,
        part: Part,
        actual_answer: int | str,
        expected_answer: int | str | None,
        hint: CheckHint | None,
    ):
        super().__init__(part)

        self.actual_answer = actual_answer
        self.expected_answer = expected_answer
        self.hint = hint


@dataclass
class CheckResult_ExampleFailed(CheckResult):
    actual_answer: int | str | None
    example: Example

    def __init__(self, actual_answer: int | str | None, example: Example):
        super().__init__(example.part)
        self.actual_answer = actual_answer
        self.example = example


@dataclass
class RunSolverResult:
    part_one: CheckResult | None
    part_two: CheckResult | None

    def __init__(
        self, part_one_result: CheckResult | None, part_two_result: CheckResult | None
    ):
        self.part_one = part_one_result
        self.part_two = part_two_result


class SolverEventHandlers(ABC):
    @abstractmethod
    def on_examples_passed(self, solver_metadata: SolverMetadata):
        pass

    @abstractmethod
    def on_part_ok(
        self, answer: int | str | None, solver_metadata: SolverMetadata, part: Part
    ):
        pass

    @abstractmethod
    def on_part_wrong(
        self, result: CheckResult, solver_metadata: SolverMetadata, part: Part
    ):
        pass


def run_solver(
    solver_metadata: SolverMetadata,
    puzzle: PuzzleData,
    client: AocClient,
    events: SolverEventHandlers,
) -> RunSolverResult:
    solver = solver_metadata.create_solver_instance()

    # Validate any examples first to check the state of the solver.
    example_check_result = check_examples(
        type(solver),
        list(solver_metadata.examples(Part.One)),
        list(solver_metadata.examples(Part.Two)),
    )

    if example_check_result is None:
        events.on_examples_passed(solver_metadata=solver_metadata)
    else:
        events.on_part_wrong(
            result=example_check_result,
            solver_metadata=solver_metadata,
            part=example_check_result.part,
        )

        return RunSolverResult(
            example_check_result if example_check_result.part == Part.One else None,
            example_check_result if example_check_result.part == Part.Two else None,
        )

    # Compute the part one and part two answers using the puzzle's input.
    #
    # Check if the answers for part one and part two match the expected puzzle
    # outputs. If these outputs are not available try to load them from the AOC
    # website.
    #
    # TODO: Refactor to loop part one and part two.
    # TODO: Submit an answer if the answer data is missing.
    # TODO: Store correct answers when answer data is missing.
    # TODO: Store incorrect answer along with hints.
    part_one = solver.part_one(puzzle.input)
    part_one_result = check_solution_part(
        part=Part.One, answer=part_one, answer_cache=puzzle.part_one_answer
    )

    if part_one_result.is_ok():
        events.on_part_ok(
            answer=part_one, solver_metadata=solver_metadata, part=Part.One
        )
    else:
        events.on_part_wrong(
            result=part_one_result, solver_metadata=solver_metadata, part=Part.One
        )

        return RunSolverResult(part_one_result=part_one_result, part_two_result=None)

    part_two = solver.part_two(puzzle.input)
    part_two_result = check_solution_part(Part.Two, part_two, puzzle.part_two_answer)

    if part_two_result.is_ok():
        events.on_part_ok(
            answer=part_two, solver_metadata=solver_metadata, part=Part.Two
        )
    else:
        events.on_part_wrong(
            result=part_two_result, solver_metadata=solver_metadata, part=Part.Two
        )

    # Done!
    return RunSolverResult(
        part_one_result=part_one_result, part_two_result=part_two_result
    )


def check_examples(
    solver_class: type[AbstractSolver],
    part_one_examples: list[Example],
    part_two_examples: list[Example],
) -> CheckResult | None:
    """
    Checks the example inputs for `solver_class` match the example outputs when
    instantiating a new instance of `solver_class` and running the inputs through
     `part_one` and `part_two` methods.
    """
    for example in part_one_examples:
        solver = solver_class()
        result = solver.part_one(example.input)

        if not example.output == result:
            return CheckResult_ExampleFailed(str(result), example)

    for example in part_two_examples:
        solver = solver_class()
        result = solver.part_two(example.input)

        if not example.output == result:
            return CheckResult_ExampleFailed(str(result), example)


def check_solution_part(
    part: Part, answer: int | str | None, answer_cache: PartAnswerCache
) -> CheckResult:
    """TODO"""
    # `None` indicates the solver hasn't implemented a solution for this part.
    if answer is None:
        return CheckResult_NotFinished(part)

    # Try to use the answer cache to check if the solution is correct.
    if answer_cache.correct_answer is not None:
        # The answer cache knows the correct answer which can be included in the
        # result!
        if answer == answer_cache.correct_answer:
            # The solution is correct! Return `None` to indicate there was no
            # error.
            return CheckResult_Ok(part)
        else:
            # The solution is wrong but the correct expected solution can be
            # included in the result.
            return CheckResult_Wrong(
                part=part,
                actual_answer=answer,
                expected_answer=answer_cache.correct_answer,
                hint=None,
            )
    else:
        # Use the previous results in the answer cache to see if the answer is
        # too low, high or otherwise incorrect.
        answer_response = answer_cache.check_answer(answer)

        # The cache doesn't have enough information to check if the answer is
        # incorrect which means this solution _could_ be the correct answer. Use
        # the provided AOC client to submit the solution and see what the result
        # is.
        if answer_response == AnswerResponse.Unknown:
            # TODO: Submit the solution and map the response to `answer_response`.
            # TODO: Write the response to the answer cache.
            raise Exception("submitting answers not implemented yet")

        # Check if the answer is OK, and for any result that is not OK return
        # a matching CheckResult value.
        if answer_response == AnswerResponse.Ok:
            return CheckResult_Ok(part)
        elif answer_response == AnswerResponse.Wrong:
            return CheckResult_Wrong(
                part=part, actual_answer=answer, expected_answer=None, hint=None
            )
        elif answer_response == AnswerResponse.TooLow:
            return CheckResult_Wrong(
                part=part,
                actual_answer=answer,
                expected_answer=None,
                hint=CheckHint.TooLow,
            )
        elif answer_response == AnswerResponse.TooHigh:
            return CheckResult_Wrong(
                part=part,
                actual_answer=answer,
                expected_answer=None,
                hint=CheckHint.TooHigh,
            )
        else:
            raise ValueError("Unhandled enum value for AnswerResponse")
