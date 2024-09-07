from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from donner.client import AocClient, SubmitResponse
from donner.data import AnswerResponse, PartAnswerCache, PuzzleData
from donner.solution import AnswerType, Example, MaybeAnswerType, Part, SolverMetadata


class CheckResult(ABC):
    """Abstract base class for the various conditions that can occur when checking the answer for one of the puzzle parts."""

    part: Part

    def __init__(self, part: Part):
        self.part = part

    def is_ok(self) -> bool:
        """Returns true if the condition is one where the answer is correct, otherwise false if it is not correct."""
        return False


@dataclass
class CheckResult_Ok(CheckResult):
    """Represents the condition where the answer was correct for the part."""

    def __init__(self, part: Part):
        super().__init__(part)

    def is_ok(self) -> bool:
        return True


@dataclass
class CheckResult_ExampleFailed(CheckResult):
    """Represents the condition where the output of this part didn't match one of the solution's example outputs"""

    actual_answer: MaybeAnswerType
    example: Example

    def __init__(self, actual_answer: MaybeAnswerType, example: Example):
        super().__init__(example.part)
        self.actual_answer = actual_answer
        self.example = example


@dataclass
class CheckResult_TooSoon(CheckResult):
    """Represents the condition where too many answers are submitted in too short of a timeframe, and the backend judge is telling us to wait before submitting a new answer"""

    def __init__(self, part: Part):
        super().__init__(part)


@dataclass
class CheckResult_NotFinished(CheckResult):
    """Represents the condition where the answer for this part has not been implemented"""

    def __init__(self, part: Part):
        super().__init__(part)


class CheckHint(Enum):
    TooLow = 1
    TooHigh = 2


@dataclass
class CheckResult_Wrong(CheckResult):
    """
    Represents the condition where the answer was not correct.

    Slots:
    `actual_answer`:   The answer that was returned when running the solver.
    `expected_answer`: The correct answer if available, otherwise this will be `None`.
    `hint`:            A hint that `actual_answer` is too low or hi if available, otherwise `None`.
    """

    actual_answer: MaybeAnswerType
    expected_answer: MaybeAnswerType
    hint: CheckHint | None

    def __init__(
        self,
        part: Part,
        actual_answer: AnswerType,
        expected_answer: MaybeAnswerType,
        hint: CheckHint | None,
    ):
        super().__init__(part)

        self.actual_answer = actual_answer
        self.expected_answer = expected_answer
        self.hint = hint


@dataclass
class RunSolverResult:
    """Holds the results of running a solver."""

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
        self, answer: MaybeAnswerType, solver_metadata: SolverMetadata, part: Part
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

    # Run the solver twice - the first time to get the part one answer, and the
    # second time to get the part two answer.
    for part in parts:
        solver = solver_metadata.create_solver_instance()
        answer = solver.get_part_func(part)(puzzle.input)

        result = check_solution_part(
            solver_metadata=solver_metadata,
            part=part,
            answer=answer,
            answer_cache=puzzle.get_answer(part=part),
            client=client,
        )

        run_result.set_result(part, result)

        if result.is_ok():
            events.on_part_ok(answer=answer, solver_metadata=solver_metadata, part=part)
        else:
            # Answer is not correct - bail out to exit early.
            events.on_part_wrong(
                result=result, solver_metadata=solver_metadata, part=part
            )
            break

    # All done - either good or bad return the results.
    return run_result


def check_solution_part(
    solver_metadata: SolverMetadata,
    part: Part,
    answer: MaybeAnswerType,
    answer_cache: PartAnswerCache,
    client: AocClient,
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
        # TODO: Submit an answer if the answer data is missing.
        # TODO: Store correct answers when answer data is missing.
        # TODO: Store incorrect answer along with hints.
        # TODO: Submit the solution and map the response to `answer_response`.
        # TODO: Write the response to the answer cache.
        submit_response = client.submit_answer(
            year=solver_metadata.year(),
            day=solver_metadata.day(),
            part=part,
            answer=str(answer),
        )

        if (
            submit_response == SubmitResponse.Ok
            or submit_response == SubmitResponse.AlreadyAnswered
        ):
            answer_cache.set_correct_answer(str(answer))
            return CheckResult_Ok(part)
        elif submit_response == SubmitResponse.TooSoon:
            return CheckResult_TooSoon(part)
        elif submit_response == SubmitResponse.Wrong:
            answer_cache.add_wrong_answer(str(answer))
            return CheckResult_Wrong(
                part=part,
                actual_answer=answer,
                expected_answer=answer_cache.correct_answer,
                hint=None,
            )
        elif submit_response == SubmitResponse.TooLow:
            answer_cache.set_low_boundary(int(answer))
            return CheckResult_Wrong(
                part=part,
                actual_answer=answer,
                expected_answer=answer_cache.correct_answer,
                hint=CheckHint.TooLow,
            )
        elif submit_response == SubmitResponse.TooHigh:
            answer_cache.set_high_boundary(int(answer))
            return CheckResult_Wrong(
                part=part,
                actual_answer=answer,
                expected_answer=answer_cache.correct_answer,
                hint=CheckHint.TooHigh,
            )
        else:
            raise ValueError(
                f"Unhandled enum value `{submit_response}` for SubmitResponse"
            )

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
        raise ValueError(f"Unhandled enum value `{answer_response}` for AnswerResponse")
