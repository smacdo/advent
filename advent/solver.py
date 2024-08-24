from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from advent.aoc.client import AocClient
from advent.data import AnswerResponse, PartAnswerCache, PuzzleData
from advent.solution import Example, Part, SolverMetadata


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
        self,
        part_one_result: CheckResult | None = None,
        part_two_result: CheckResult | None = None,
    ):
        self.part_one = part_one_result
        self.part_two = part_two_result

    def set_result(self, part: Part, result: CheckResult):
        """Get the result for part one if `part == Part.One` otherwise get the result for part two."""
        if part == Part.One:
            self.part_one = result
        else:
            self.part_two = result

    def get_result(self, part: Part) -> CheckResult | None:
        """Set the result for part one if `part == Part.One` otherwise set the result for part two."""

        if part == Part.One:
            return self.part_one
        else:
            return self.part_two


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
    run_result = RunSolverResult()

    # Validate any examples first to check the state of the solver.
    parts = (Part.One, Part.Two)

    for part in parts:
        for example in solver_metadata.examples(part):
            solver = solver_metadata.create_solver_instance()
            answer = solver.get_part_func(part)(example.input)

            if example.output != answer:
                result = CheckResult_ExampleFailed(
                    actual_answer=answer, example=example
                )

                run_result.set_result(
                    part,
                    result,
                )

                events.on_part_wrong(
                    result=result, solver_metadata=solver_metadata, part=part
                )

                return run_result

    events.on_examples_passed(solver_metadata=solver_metadata)

    # Compute the part one and part two answers using the puzzle's input.
    #
    # Check if the answers for part one and part two match the expected puzzle
    # outputs. If these outputs are not available try to load them from the AOC
    # website.
    #
    # TODO: Submit an answer if the answer data is missing.
    # TODO: Store correct answers when answer data is missing.
    # TODO: Store incorrect answer along with hints.
    for part in parts:
        solver = solver_metadata.create_solver_instance()
        answer = solver.get_part_func(part)(puzzle.input)

        result = check_solution_part(
            part=part, answer=answer, answer_cache=puzzle.get_answer(part=part)
        )

        run_result.set_result(part, result)

        if result.is_ok():
            events.on_part_ok(answer=answer, solver_metadata=solver_metadata, part=part)
        else:
            # Answer is not correct - bail out to exit early.
            break

    # All done - either good or bad return the results.
    return run_result


def check_solution_part(
    part: Part, answer: int | str | None, answer_cache: PartAnswerCache
) -> CheckResult:
    """TODO"""
    # `None` indicates the solver hasn't implemented a solution for this part.
    if answer is None:
        return CheckResult_NotFinished(part)

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
            part=part,
            actual_answer=answer,
            expected_answer=answer_cache.correct_answer,
            hint=None,
        )
    elif answer_response == AnswerResponse.TooLow:
        return CheckResult_Wrong(
            part=part,
            actual_answer=answer,
            expected_answer=answer_cache.correct_answer,
            hint=CheckHint.TooLow,
        )
    elif answer_response == AnswerResponse.TooHigh:
        return CheckResult_Wrong(
            part=part,
            actual_answer=answer,
            expected_answer=answer_cache.correct_answer,
            hint=CheckHint.TooHigh,
        )
    else:
        raise ValueError("Unhandled enum value for AnswerResponse")
