from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from advent.utils import not_none
from donner.client import AocClient, SubmitResponse
from donner.data import AnswerResponse, PartAnswerCache, PuzzleData
from donner.solution import AnswerType, Example, MaybeAnswerType, Part, SolverMetadata


class CheckResult(ABC):
    """Abstract base class for the various conditions that can occur when checking the answer for one of the puzzle parts."""

    part: Part
    actual_answer: MaybeAnswerType

    def __init__(self, part: Part, actual_answer: MaybeAnswerType):
        self.part = part
        self.actual_answer = actual_answer

    def is_ok(self) -> bool:
        """Returns true if the condition is one where the answer is correct, otherwise false if it is not correct."""
        return False


@dataclass
class CheckResult_Ok(CheckResult):
    """Represents the condition where the answer was correct for the part."""

    def __init__(self, part: Part, actual_answer: AnswerType):
        super().__init__(part, actual_answer)

    def is_ok(self) -> bool:
        return True


@dataclass
class CheckResult_ExampleFailed(CheckResult):
    """Represents the condition where the output of this part didn't match one of the solution's example outputs"""

    example: Example

    def __init__(self, actual_answer: MaybeAnswerType, example: Example):
        super().__init__(example.part, actual_answer)
        self.example = example


@dataclass
class CheckResult_TooSoon(CheckResult):
    """Represents the condition where too many answers are submitted in too short of a timeframe, and the backend judge is telling us to wait before submitting a new answer"""

    def __init__(self, part: Part, actual_answer: AnswerType):
        super().__init__(part, actual_answer)


@dataclass
class CheckResult_NotFinished(CheckResult):
    """Represents the condition where the answer for this part has not been implemented"""

    def __init__(self, part: Part):
        super().__init__(part, actual_answer=None)


@dataclass
class CheckResult_Skipped(CheckResult):
    """
    Represents the condition where the answer for this part was not run.

    It is possible that when a part is skipped some or all of the examples
    were still run prior to skipping the real input. Any examples that were run
    have passed otherwise this `CheckResult` would be `CheckResult_ExampleFailed`.
    Check the `examples` attribute to see which examples passed.
    """

    examples: list[Example]

    def __init__(self, part: Part, examples: list[Example]):
        super().__init__(part, actual_answer=None)
        self.examples = examples


class CheckHint(Enum):
    TooLow = 1
    TooHigh = 2


@dataclass
class CheckResult_Wrong(CheckResult):
    """
    Represents the condition where the answer was not correct.

    # Slots:
    - `expected_answer`: The correct answer if available, otherwise this will be `None`.
    - `hint`:            A hint that `actual_answer` is too low or hi if available, otherwise `None`.
    """

    expected_answer: MaybeAnswerType
    hint: CheckHint | None

    def __init__(
        self,
        part: Part,
        actual_answer: AnswerType,
        expected_answer: MaybeAnswerType,
        hint: CheckHint | None,
    ):
        super().__init__(part, actual_answer)

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
    """
    Receives callbacks from the puzzle runner (solver) that can be used to display progress details
    to the user.

    # Events:
    - `on_start_solver`: A solver is started for a puzzle.
    - `on_finish_solver`: A solver has finished a puzzle, correctly or incorrectly.
    """

    @abstractmethod
    def on_start_solver(
        self,
        solver_metadata: SolverMetadata,
    ):
        pass

    @abstractmethod
    def on_finish_solver(
        self,
        solver_metadata: SolverMetadata,
        result: RunSolverResult,
    ):
        pass

    @abstractmethod
    def on_start_part(self, solver_metadata: SolverMetadata, part: Part):
        pass

    @abstractmethod
    def on_finish_part(
        self,
        solver_metadata: SolverMetadata,
        part: Part,
        result: CheckResult,
    ):
        pass

    @abstractmethod
    def on_part_examples_pass(
        self, solver_metadata: SolverMetadata, part: Part, count: int
    ):
        pass


def run_solver(
    solver_metadata: SolverMetadata,
    puzzle: PuzzleData,
    client: AocClient,
    events: SolverEventHandlers,
    submit_answer: bool = True,
    part: Part | None = None,
    example_index: int | None = None,
    input: str | None = None,
) -> RunSolverResult:
    """
    Runs a solver provided by `solver_metadata` on `puzzle` and upon succesful execution attempts to
    submit the answer using `client`.

    # Parameters
    - `solver_metadata`: Metadata about the solver class that should be run for the puzzle.
    - `puzzle`:          The puzzle that should be solved.
    - `client`:          Object that can submit answers to the AoC service.
    - `events`:          A custom event manager that this function will call when certain events
                         happen while running a solver. See docs for `SolverEventHandlers` to
                         understand what events would be called.
    - `submit_answer`:   Optional, defaults to True. If this flag is set to True the runner will
                         submit answers (using `client`) to the AoC service when the solver returns
                         succesfully, and the associated answer cache does not have sufficient
                         information to know if the answer is correct or incorrect.
    - `part`:            Optional. Tells the runner to only run this part instead of all parts.
    - `example_index`:   Optional. Tells the runner to only run this example. This argument also
                         disables running the real puzzle input. It also requires that the `part`
                         argument be specified.
    - `input`:           Optional. Overrides the puzzle's default input with this value when running
                         the solver. Callers must also specify `part` when using this parameter.
    """
    run_result = RunSolverResult()

    # Make sure if example index is used that part is also passed.
    if example_index is not None and part is None:
        raise ValueError(
            "`example_index` parameter requires caller to also specify `part` parameter"
        )

    # Custom input also requires that a part is specified.
    if input is not None and part is None:
        raise ValueError(
            "`input` parameter requires caller to also specify `part` parameter"
        )

    # Run the solver for part one and then part two by default, unless the caller
    # has specified the specific part to be run.
    if part is None:
        parts = (Part.One, Part.Two)
    else:
        parts = (part,)

    # Run the selected parts.
    events.on_start_solver(solver_metadata=solver_metadata)

    for part in parts:
        events.on_start_part(solver_metadata=solver_metadata, part=part)

        # Validate examples listed for the current part prior to running the
        # part on real input. Use all of the examples associated with the solver
        # unless the caller has requested a specific example be run.
        examples_pass = True
        examples = list(solver_metadata.examples(part))

        if example_index is not None:
            if example_index < 0 or example_index >= len(examples):
                raise IndexError(
                    f"example index {example_index} is out of range (examples count for {part} is {len(examples)})"
                )

            examples = [examples[example_index]]

        # Validate the selected examples.
        for example in examples:
            solver = solver_metadata.create_solver_instance()
            answer = str(solver.get_part_func(part)(example.input))

            if example.output != answer:
                # Example failed - set the result for this part as
                # "example failed". Stop testing examples for this part.
                run_result.set_result(
                    part,
                    CheckResult_ExampleFailed(actual_answer=answer, example=example),
                )

                examples_pass = False
                break

        # Notify the event manager that examples have passed, otherwise if any
        # have failed then skip running the part with real input.
        if examples_pass:
            events.on_part_examples_pass(
                solver_metadata=solver_metadata, part=part, count=len(examples)
            )
        else:
            events.on_finish_part(
                solver_metadata=solver_metadata,
                part=part,
                result=not_none(run_result.get_result(part=part)),
            )

            continue

        # Run the solver against real puzzle input so long as the caller didn't
        # request a specific example to be run (implying that the real input
        # shouldn't be used).
        if example_index is None:
            solver = solver_metadata.create_solver_instance()
            answer = solver.get_part_func(part)(
                puzzle.input if input is None else input
            )

            result = check_solution_part(
                solver_metadata=solver_metadata,
                part=part,
                answer=answer,
                answer_cache=puzzle.get_answer(part=part),
                client=client,
                submit_answer=submit_answer,
            )
        else:
            result = CheckResult_Skipped(part=part, examples=examples)

        # Set the final result for this part and notify the event manager that
        # the part has finished running.
        run_result.set_result(part, result)
        events.on_finish_part(solver_metadata=solver_metadata, part=part, result=result)

    # All done - either good or bad return the results.
    events.on_finish_solver(solver_metadata=solver_metadata, result=run_result)
    return run_result


def check_solution_part(
    solver_metadata: SolverMetadata,
    part: Part,
    answer: MaybeAnswerType,
    answer_cache: PartAnswerCache,
    client: AocClient,
    submit_answer: bool,
) -> CheckResult:
    """
    Checks if the puzzle `answer` is correct or incorrect.

    This function will first check if `answer` is in `answer_cache`. If the cache is unable to
    determine if the answer is correct it will be submitted to the AoC website using `client`. The
    response from `client` will be recorded into `answer_cache`, and the result returned to the
    caller.

    # Parameters
    - `solver_metadata`: Metadata about the solver class that should be run for the puzzle.
    - `part`:            Optional. Tells the runner to only run this part instead of all parts.
    - `answer`:          The output of the solver when run against the puzzle's input.
    - `answer_cache`:    Object holding previously submitted answers.
    - `client`:          Object that can submit answers to the AoC service.
    - `submit_answer`:   Optional, defaults to True. If this flag is set to `True` the runner will
                         submit answers (using `client`) to the AoC website when the solver returns
                         succesfully, and `answer_cache` cannot determine if the answer is correct
                         or incorrect.
    """
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
    if answer_response == AnswerResponse.Unknown and submit_answer:
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
            return CheckResult_Ok(part, answer)
        elif submit_response == SubmitResponse.TooSoon:
            return CheckResult_TooSoon(part, answer)
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
        return CheckResult_Ok(part, answer)
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
    elif answer_response == AnswerResponse.Unknown and not submit_answer:
        raise ValueError("cannot submit answer when `submit_answer == False`")
    else:
        raise ValueError(f"Unhandled enum value `{answer_response}` for AnswerResponse")
