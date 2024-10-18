from typing import List
import unittest

from donner.client import AocDay, AocClient, SubmitResponse
from donner.data import PartAnswerCache, PuzzleData
from donner.solution import (
    AbstractSolver,
    Example,
    MaybeAnswerType,
    Part,
    SolverMetadata,
)
from donner.solver import (
    CheckHint,
    CheckResult,
    CheckResult_ExampleFailed,
    CheckResult_NotFinished,
    CheckResult_Ok,
    CheckResult_TooSoon,
    CheckResult_Wrong,
    RunSolverResult,
    SolverEventHandlers,
    run_solver,
)


class DecoratedTestSolution(AbstractSolver):
    def part_one(self, input: str) -> MaybeAnswerType:
        if input == "part_one_fail" or input == "fail":
            return "part_one_bad_output"
        elif input == "part_one_low":
            return -50
        elif input == "part_one_not_finished" or input == "not_finished":
            return None
        elif input == "int":
            return 22

        return "part_one_ok"

    def part_two(self, input: str) -> MaybeAnswerType:
        if input == "part_two_fail" or input == "fail":
            return "part_two_bad_output"
        elif input == "part_two_high":
            return 128
        elif input == "part_two_not_finished" or input == "not_finished":
            return None
        elif input == "int":
            return -127

        return "part_two_ok"


class MockAocClient(AocClient):
    submit_answer_calls: list[tuple[int, int, Part, str]]
    part_one_response: SubmitResponse | None
    part_two_response: SubmitResponse | None

    def __init__(
        self,
        part_one_response: SubmitResponse | None = None,
        part_two_response: SubmitResponse | None = None,
    ):
        super().__init__()
        self.submit_answer_calls = []
        self.part_one_response = part_one_response
        self.part_two_response = part_two_response

    def fetch_input_for(self, year: int, day: int) -> str:
        raise NotImplementedError

    def fetch_days(self, year: int) -> List[AocDay]:
        raise NotImplementedError

    def submit_answer(
        self, year: int, day: int, part: Part, answer: str
    ) -> SubmitResponse:
        self.submit_answer_calls.append((year, day, part, answer))
        response = (
            self.part_one_response if part == Part.One else self.part_two_response
        )

        if response is None:
            raise NotImplementedError
        else:
            return response


class MockSolverEventHandlers(SolverEventHandlers):
    start_solver_calls: list[SolverMetadata]
    finish_solver_calls: list[tuple[SolverMetadata, RunSolverResult]]

    start_part_calls: list[tuple[SolverMetadata, Part]]
    finish_part_calls: list[tuple[SolverMetadata, Part, CheckResult]]

    examples_passed_calls: list[tuple[SolverMetadata, Part, int]]

    def __init__(self):
        super().__init__()
        self.start_solver_calls = []
        self.finish_solver_calls = []
        self.start_part_calls = []
        self.finish_part_calls = []
        self.examples_passed_calls = []

    def on_start_solver(
        self,
        solver_metadata: SolverMetadata,
    ):
        self.start_solver_calls.append(solver_metadata)

    def on_finish_solver(
        self,
        solver_metadata: SolverMetadata,
        result: RunSolverResult,
    ):
        self.finish_solver_calls.append((solver_metadata, result))

    def on_start_part(self, solver_metadata: SolverMetadata, part: Part):
        self.start_part_calls.append((solver_metadata, part))

    def on_finish_part(
        self,
        solver_metadata: SolverMetadata,
        part: Part,
        result: CheckResult,
    ):
        self.finish_part_calls.append((solver_metadata, part, result))

    def on_part_examples_pass(
        self,
        solver_metadata: SolverMetadata,
        part: Part,
        count: int,
    ):
        self.examples_passed_calls.append((solver_metadata, part, count))


class CheckResultTests(unittest.TestCase):
    def test_check_actual_answer(self):
        self.assertEqual(
            CheckResult_Ok(Part.One, "hello world").actual_answer, "hello world"
        )
        self.assertEqual(
            CheckResult_ExampleFailed(
                1234, Example("input", "output", Part.One)
            ).actual_answer,
            1234,
        )
        self.assertEqual(CheckResult_TooSoon(Part.Two, "123").actual_answer, "123")
        self.assertEqual(CheckResult_NotFinished(Part.One).actual_answer, None)
        self.assertEqual(
            CheckResult_Wrong(Part.Two, "foo", "bar", None).actual_answer, "foo"
        )


class RunSolverResultTests(unittest.TestCase):
    def test_get_result(self):
        part_one_result = CheckResult_Ok(Part.One, "foobar")
        part_two_result = CheckResult_Wrong(Part.One, "actual", 42, hint=None)

        r = RunSolverResult(
            part_one_result=part_one_result,
            part_two_result=part_two_result,
        )

        self.assertEqual(r.get_result(Part.One), part_one_result)
        self.assertEqual(r.get_result(Part.Two), part_two_result)

        self.assertNotEqual(part_one_result, part_two_result)

    def test_set_result(self):
        part_one_result = CheckResult_Ok(Part.One, "foobar")
        part_two_result = CheckResult_Wrong(Part.One, "actual", 42, hint=None)

        r = RunSolverResult(
            part_one_result=None,
            part_two_result=None,
        )

        r.set_result(Part.One, part_one_result)
        r.set_result(Part.Two, part_two_result)

        self.assertEqual(r.get_result(Part.One), part_one_result)
        self.assertEqual(r.get_result(Part.Two), part_two_result)

        self.assertNotEqual(part_one_result, part_two_result)


class RunSolverTests(unittest.TestCase):
    def test_both_correct_using_answer_cache(self):
        # Construct and run solver.
        solver_m = SolverMetadata(
            klass=DecoratedTestSolution, day=5, year=2012, puzzle_name="test puzzle"
        )
        events = MockSolverEventHandlers()

        result = run_solver(
            solver_m,
            PuzzleData(
                input="plz_work",
                part_one_answer=PartAnswerCache(correct_answer="part_one_ok"),
                part_two_answer=PartAnswerCache(correct_answer="part_two_ok"),
            ),
            MockAocClient(),
            events=events,
        )

        # Verify solver returned expected results [part one, part two passed].
        run_result = RunSolverResult(
            part_one_result=CheckResult_Ok(Part.One, "part_one_ok"),
            part_two_result=CheckResult_Ok(Part.Two, "part_two_ok"),
        )

        self.assertEqual(result, run_result)

        # Verify only expected events fired.
        self.assertSequenceEqual(events.start_solver_calls, [solver_m])
        self.assertSequenceEqual(events.finish_solver_calls, [(solver_m, result)])

        self.assertSequenceEqual(
            events.start_part_calls, [(solver_m, Part.One), (solver_m, Part.Two)]
        )
        self.assertSequenceEqual(
            events.finish_part_calls,
            [
                (solver_m, Part.One, result.part_one),
                (solver_m, Part.Two, result.part_two),
            ],
        )

        self.assertSequenceEqual(
            events.examples_passed_calls,
            [(solver_m, Part.One, 0), (solver_m, Part.Two, 0)],
        )

    def test_first_part_example_fail_and_first_part_not_run(self):
        solver_m = SolverMetadata(
            klass=DecoratedTestSolution,
            day=5,
            year=2012,
            puzzle_name="test puzzle",
            examples=[
                Example(input="part_one_fail", output="part_one_ok", part=Part.One),
                Example(input="part_two_ok", output="part_two_ok", part=Part.Two),
            ],
        )
        events = MockSolverEventHandlers()

        # Verify part two example fails and part two solver is never run.
        result = run_solver(
            solver_m,
            PuzzleData(
                input="plz_work",
                part_one_answer=PartAnswerCache(correct_answer="part_one_ok"),
                part_two_answer=PartAnswerCache(correct_answer="part_two_ok"),
            ),
            MockAocClient(),
            events,
        )

        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_ExampleFailed(
                    "part_one_bad_output", list(solver_m.examples(Part.One))[0]
                ),
                part_two_result=CheckResult_Ok(Part.Two, "part_two_ok"),
            ),
        )

        self.assertSequenceEqual(events.start_solver_calls, [solver_m])
        self.assertSequenceEqual(events.finish_solver_calls, [(solver_m, result)])
        self.assertSequenceEqual(
            events.start_part_calls, [(solver_m, Part.One), (solver_m, Part.Two)]
        )
        self.assertSequenceEqual(
            events.finish_part_calls,
            [
                (solver_m, Part.One, result.part_one),
                (solver_m, Part.Two, result.part_two),
            ],
        )

        self.assertSequenceEqual(
            events.examples_passed_calls,
            [(solver_m, Part.Two, 1)],
        )

    def test_second_part_example_fail_and_second_part_not_run(self):
        solver_m = SolverMetadata(
            klass=DecoratedTestSolution,
            day=5,
            year=2012,
            puzzle_name="test puzzle",
            examples=[
                Example(input="part_one_ok", output="part_one_ok", part=Part.One),
                Example(input="part_two_fail", output="part_two_ok", part=Part.Two),
            ],
        )
        events = MockSolverEventHandlers()

        # Verify part two example fails and part two solver is never run.
        result = run_solver(
            solver_m,
            PuzzleData(
                input="plz_work",
                part_one_answer=PartAnswerCache(correct_answer="part_one_ok"),
                part_two_answer=PartAnswerCache(correct_answer="part_two_ok"),
            ),
            MockAocClient(),
            events,
        )

        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Ok(Part.One, "part_one_ok"),
                part_two_result=CheckResult_ExampleFailed(
                    "part_two_bad_output", list(solver_m.examples(Part.Two))[0]
                ),
            ),
        )

        self.assertSequenceEqual(events.start_solver_calls, [solver_m])
        self.assertSequenceEqual(events.finish_solver_calls, [(solver_m, result)])

        self.assertSequenceEqual(
            events.start_part_calls, [(solver_m, Part.One), (solver_m, Part.Two)]
        )
        self.assertSequenceEqual(
            events.finish_part_calls,
            [
                (solver_m, Part.One, result.part_one),
                (solver_m, Part.Two, result.part_two),
            ],
        )

        self.assertSequenceEqual(
            events.examples_passed_calls,
            [(solver_m, Part.One, 1)],
        )

    def test_example_with_str_when_solver_returns_int(self):
        # Construct and run solver.
        solver_m = SolverMetadata(
            klass=DecoratedTestSolution,
            day=5,
            year=2012,
            puzzle_name="test puzzle",
            examples=[
                Example(input="int", output="22", part=Part.One),
                Example(input="int", output="-127", part=Part.Two),
            ],
        )
        events = MockSolverEventHandlers()

        puzzle = PuzzleData(
            input="int",
            part_one_answer=PartAnswerCache(correct_answer="22"),
            part_two_answer=PartAnswerCache(correct_answer="-127"),
        )

        # Verify both examples pass.
        result = run_solver(solver_m, puzzle, MockAocClient(), events)
        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Ok(Part.One, 22),
                part_two_result=CheckResult_Ok(Part.Two, -127),
            ),
        )

        self.assertSequenceEqual(events.start_solver_calls, [solver_m])
        self.assertSequenceEqual(events.finish_solver_calls, [(solver_m, result)])

        self.assertSequenceEqual(
            events.start_part_calls, [(solver_m, Part.One), (solver_m, Part.Two)]
        )
        self.assertSequenceEqual(
            events.finish_part_calls,
            [
                (solver_m, Part.One, result.part_one),
                (solver_m, Part.Two, result.part_two),
            ],
        )

        self.assertSequenceEqual(
            events.examples_passed_calls,
            [(solver_m, Part.One, 1), (solver_m, Part.Two, 1)],
        )

    def test_generic_wrong_answer_using_answer_cache(self):
        # Construct and run solver.
        solver_m = SolverMetadata(
            klass=DecoratedTestSolution,
            day=5,
            year=2012,
            puzzle_name="test puzzle",
        )
        events = MockSolverEventHandlers()

        # The solver should return that the first part returned the correct
        # answer but the second part has the wrong answer.
        result = run_solver(
            solver_m,
            PuzzleData(
                input="part_two_fail",
                part_one_answer=PartAnswerCache(correct_answer="part_one_ok"),
                part_two_answer=PartAnswerCache(correct_answer="part_two_ok"),
            ),
            MockAocClient(),
            events=events,
        )

        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Ok(Part.One, "part_one_ok"),
                part_two_result=CheckResult_Wrong(
                    part=Part.Two,
                    actual_answer="part_two_bad_output",
                    expected_answer="part_two_ok",
                    hint=None,
                ),
            ),
        )

        self.assertSequenceEqual(events.start_solver_calls, [solver_m])
        self.assertSequenceEqual(events.finish_solver_calls, [(solver_m, result)])

        self.assertSequenceEqual(
            events.start_part_calls, [(solver_m, Part.One), (solver_m, Part.Two)]
        )
        self.assertSequenceEqual(
            events.finish_part_calls,
            [
                (solver_m, Part.One, result.part_one),
                (solver_m, Part.Two, result.part_two),
            ],
        )

        self.assertSequenceEqual(
            events.examples_passed_calls,
            [(solver_m, Part.One, 0), (solver_m, Part.Two, 0)],
        )

        # Both part one and part two will return wrong answers found in the
        # answer cache. Verify that both parts are tested rather than exiting
        # early.
        events = MockSolverEventHandlers()
        result = run_solver(
            solver_m,
            PuzzleData(
                input="fail",
                part_one_answer=PartAnswerCache(correct_answer="part_one_ok"),
                part_two_answer=PartAnswerCache(correct_answer="part_two_ok"),
            ),
            MockAocClient(),
            events=events,
        )

        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Wrong(
                    part=Part.One,
                    actual_answer="part_one_bad_output",
                    expected_answer="part_one_ok",
                    hint=None,
                ),
                part_two_result=CheckResult_Wrong(
                    part=Part.Two,
                    actual_answer="part_two_bad_output",
                    expected_answer="part_two_ok",
                    hint=None,
                ),
            ),
        )

        self.assertSequenceEqual(events.start_solver_calls, [solver_m])
        self.assertSequenceEqual(events.finish_solver_calls, [(solver_m, result)])

        self.assertSequenceEqual(
            events.start_part_calls, [(solver_m, Part.One), (solver_m, Part.Two)]
        )
        self.assertSequenceEqual(
            events.finish_part_calls,
            [
                (solver_m, Part.One, result.part_one),
                (solver_m, Part.Two, result.part_two),
            ],
        )

        self.assertSequenceEqual(
            events.examples_passed_calls,
            [(solver_m, Part.One, 0), (solver_m, Part.Two, 0)],
        )

    def test_wrong_answer_hint_with_answer_cache(self):
        # Construct and run solver.
        solver_m = SolverMetadata(
            klass=DecoratedTestSolution,
            day=5,
            year=2012,
            puzzle_name="test puzzle",
        )
        events = MockSolverEventHandlers()

        # Part one has the right answer but two is too high.
        result = run_solver(
            solver_m,
            PuzzleData(
                input="part_two_high",
                part_one_answer=PartAnswerCache(correct_answer="part_one_ok"),
                part_two_answer=PartAnswerCache(high_boundary=10),
            ),
            MockAocClient(),
            events=events,
        )

        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Ok(Part.One, "part_one_ok"),
                part_two_result=CheckResult_Wrong(
                    part=Part.Two,
                    actual_answer=128,
                    expected_answer=None,
                    hint=CheckHint.TooHigh,
                ),
            ),
        )

        self.assertSequenceEqual(events.start_solver_calls, [solver_m])
        self.assertSequenceEqual(events.finish_solver_calls, [(solver_m, result)])

        self.assertSequenceEqual(
            events.start_part_calls, [(solver_m, Part.One), (solver_m, Part.Two)]
        )
        self.assertSequenceEqual(
            events.finish_part_calls,
            [
                (solver_m, Part.One, result.part_one),
                (solver_m, Part.Two, result.part_two),
            ],
        )

        self.assertSequenceEqual(
            events.examples_passed_calls,
            [(solver_m, Part.One, 0), (solver_m, Part.Two, 0)],
        )

        # Part one and two have wrong answers.
        events = MockSolverEventHandlers()

        result = run_solver(
            solver_m,
            PuzzleData(
                input="part_one_low",
                part_one_answer=PartAnswerCache(correct_answer="hello", low_boundary=3),
                part_two_answer=PartAnswerCache(correct_answer="part_two_ok"),
            ),
            MockAocClient(),
            events=events,
        )

        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Wrong(
                    part=Part.One,
                    actual_answer=-50,
                    expected_answer="hello",
                    hint=CheckHint.TooLow,
                ),
                part_two_result=CheckResult_Ok(
                    part=Part.Two, actual_answer="part_two_ok"
                ),
            ),
        )

        self.assertSequenceEqual(events.start_solver_calls, [solver_m])
        self.assertSequenceEqual(events.finish_solver_calls, [(solver_m, result)])

        self.assertSequenceEqual(
            events.start_part_calls, [(solver_m, Part.One), (solver_m, Part.Two)]
        )
        self.assertSequenceEqual(
            events.finish_part_calls,
            [
                (solver_m, Part.One, result.part_one),
                (solver_m, Part.Two, result.part_two),
            ],
        )

        self.assertSequenceEqual(
            events.examples_passed_calls,
            [(solver_m, Part.One, 0), (solver_m, Part.Two, 0)],
        )

    def test_not_finished_answer(self):
        # Construct solver.
        solver_m = SolverMetadata(
            klass=DecoratedTestSolution,
            day=5,
            year=2012,
            puzzle_name="test puzzle",
        )
        events = MockSolverEventHandlers()

        # Part one has the right answer but two is not complete.
        result = run_solver(
            solver_m,
            PuzzleData(
                input="part_two_not_finished",
                part_one_answer=PartAnswerCache(correct_answer="part_one_ok"),
                part_two_answer=PartAnswerCache(correct_answer="part_two_ok"),
            ),
            MockAocClient(),
            events=events,
        )

        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Ok(Part.One, "part_one_ok"),
                part_two_result=CheckResult_NotFinished(part=Part.Two),
            ),
        )

        self.assertSequenceEqual(events.start_solver_calls, [solver_m])
        self.assertSequenceEqual(events.finish_solver_calls, [(solver_m, result)])

        self.assertSequenceEqual(
            events.start_part_calls, [(solver_m, Part.One), (solver_m, Part.Two)]
        )
        self.assertSequenceEqual(
            events.finish_part_calls,
            [
                (solver_m, Part.One, result.part_one),
                (solver_m, Part.Two, result.part_two),
            ],
        )

        self.assertSequenceEqual(
            events.examples_passed_calls,
            [(solver_m, Part.One, 0), (solver_m, Part.Two, 0)],
        )

        # Part one and two have unfinished answers.
        events = MockSolverEventHandlers()
        result = run_solver(
            solver_m,
            PuzzleData(
                input="not_finished",
                part_one_answer=PartAnswerCache(correct_answer="part_one_ok"),
                part_two_answer=PartAnswerCache(correct_answer="part_two_ok"),
            ),
            MockAocClient(),
            events=events,
        )

        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_NotFinished(Part.One),
                part_two_result=CheckResult_NotFinished(Part.Two),
            ),
        )

        self.assertSequenceEqual(events.start_solver_calls, [solver_m])
        self.assertSequenceEqual(events.finish_solver_calls, [(solver_m, result)])

        self.assertSequenceEqual(
            events.start_part_calls, [(solver_m, Part.One), (solver_m, Part.Two)]
        )
        self.assertSequenceEqual(
            events.finish_part_calls,
            [
                (solver_m, Part.One, result.part_one),
                (solver_m, Part.Two, result.part_two),
            ],
        )

        self.assertSequenceEqual(
            events.examples_passed_calls,
            [(solver_m, Part.One, 0), (solver_m, Part.Two, 0)],
        )

    def test_correct_answer_in_cache_skips_clients(self):
        # Construct and run solver.
        solver_m = SolverMetadata(
            klass=DecoratedTestSolution, day=5, year=2012, puzzle_name="test puzzle"
        )
        client = MockAocClient(
            part_one_response=SubmitResponse.Ok, part_two_response=SubmitResponse.Ok
        )
        events = MockSolverEventHandlers()
        answer_cache = [
            PartAnswerCache(correct_answer="part_one_ok"),
            PartAnswerCache(correct_answer="part_two_ok"),
        ]

        run_solver(
            solver_m,
            PuzzleData(
                input="plz_work",
                part_one_answer=answer_cache[0],
                part_two_answer=answer_cache[1],
            ),
            client=client,
            events=events,
        )

        # Verify client was not called.
        self.assertSequenceEqual(client.submit_answer_calls, [])

    def test_correct_answer_in_cache_skips_clients_even_if_answer_wrong(self):
        # Construct and run solver.
        solver_m = SolverMetadata(
            klass=DecoratedTestSolution, day=5, year=2012, puzzle_name="test puzzle"
        )
        client = MockAocClient(
            part_one_response=SubmitResponse.Ok, part_two_response=SubmitResponse.Ok
        )
        events = MockSolverEventHandlers()
        answer_cache = [
            PartAnswerCache(correct_answer="part_one_fail"),
            PartAnswerCache(correct_answer="part_one_fail"),
        ]

        run_solver(
            solver_m,
            PuzzleData(
                input="plz_work",
                part_one_answer=answer_cache[0],
                part_two_answer=answer_cache[1],
            ),
            client=client,
            events=events,
        )

        # Verify client was not called.
        self.assertSequenceEqual(client.submit_answer_calls, [])

    def test_unknown_submit_answer_both_ok(self):
        # Construct and run solver.
        solver_m = SolverMetadata(
            klass=DecoratedTestSolution, day=5, year=2012, puzzle_name="test puzzle"
        )
        client = MockAocClient(
            part_one_response=SubmitResponse.Ok, part_two_response=SubmitResponse.Ok
        )
        events = MockSolverEventHandlers()
        answer_cache = [PartAnswerCache(), PartAnswerCache()]

        result = run_solver(
            solver_m,
            PuzzleData(
                input="plz_work",
                part_one_answer=answer_cache[0],
                part_two_answer=answer_cache[1],
            ),
            client=client,
            events=events,
        )

        # Verify solver returned expected results [part one, part two passed].
        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Ok(Part.One, "part_one_ok"),
                part_two_result=CheckResult_Ok(Part.Two, "part_two_ok"),
            ),
        )

        # Verify only expected events fired.
        self.assertSequenceEqual(events.start_solver_calls, [solver_m])
        self.assertSequenceEqual(events.finish_solver_calls, [(solver_m, result)])

        self.assertSequenceEqual(
            events.start_part_calls, [(solver_m, Part.One), (solver_m, Part.Two)]
        )
        self.assertSequenceEqual(
            events.finish_part_calls,
            [
                (solver_m, Part.One, result.part_one),
                (solver_m, Part.Two, result.part_two),
            ],
        )

        self.assertSequenceEqual(
            events.examples_passed_calls,
            [(solver_m, Part.One, 0), (solver_m, Part.Two, 0)],
        )

        # Verify answer cache has recorded the submitted answer.
        self.assertEqual(answer_cache[0], PartAnswerCache(correct_answer="part_one_ok"))
        self.assertEqual(answer_cache[1], PartAnswerCache(correct_answer="part_two_ok"))

    def test_client_returns_too_soon_result(self):
        # Construct and run solver.
        solver_m = SolverMetadata(
            klass=DecoratedTestSolution, day=5, year=2012, puzzle_name="test puzzle"
        )
        client = MockAocClient(
            part_one_response=SubmitResponse.Ok,
            part_two_response=SubmitResponse.TooSoon,
        )
        events = MockSolverEventHandlers()
        answer_cache = [PartAnswerCache(), PartAnswerCache()]

        result = run_solver(
            solver_m,
            PuzzleData(
                input="plz_work",
                part_one_answer=answer_cache[0],
                part_two_answer=answer_cache[1],
            ),
            client=client,
            events=events,
        )

        # Verify that running the solver will OK the first part and then raise an
        # exception on the second part.
        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Ok(Part.One, "part_one_ok"),
                part_two_result=CheckResult_TooSoon(Part.Two, "part_two_ok"),
            ),
        )

        # Verify only expected events fired.
        self.assertSequenceEqual(events.start_solver_calls, [solver_m])
        self.assertSequenceEqual(events.finish_solver_calls, [(solver_m, result)])

        self.assertSequenceEqual(
            events.start_part_calls, [(solver_m, Part.One), (solver_m, Part.Two)]
        )
        self.assertSequenceEqual(
            events.finish_part_calls,
            [
                (solver_m, Part.One, result.part_one),
                (solver_m, Part.Two, result.part_two),
            ],
        )

        self.assertSequenceEqual(
            events.examples_passed_calls,
            [(solver_m, Part.One, 0), (solver_m, Part.Two, 0)],
        )

        self.assertSequenceEqual(
            client.submit_answer_calls,
            [(2012, 5, Part.One, "part_one_ok"), (2012, 5, Part.Two, "part_two_ok")],
        )

        # Verify answer cache has recorded the submitted answer.
        self.assertEqual(answer_cache[0], PartAnswerCache(correct_answer="part_one_ok"))
        self.assertEqual(answer_cache[1], PartAnswerCache())

    def test_client_returns_already_answered(self):
        # Construct and run solver.
        solver_m = SolverMetadata(
            klass=DecoratedTestSolution, day=5, year=2012, puzzle_name="test puzzle"
        )
        client = MockAocClient(
            part_one_response=SubmitResponse.AlreadyAnswered,
            part_two_response=SubmitResponse.AlreadyAnswered,
        )
        events = MockSolverEventHandlers()
        answer_cache = [PartAnswerCache(), PartAnswerCache()]

        result = run_solver(
            solver_m,
            PuzzleData(
                input="plz_work",
                part_one_answer=answer_cache[0],
                part_two_answer=answer_cache[1],
            ),
            client=client,
            events=events,
        )

        # Verify that running the solver will OK the first part and then raise an
        # exception on the second part.
        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Ok(Part.One, "part_one_ok"),
                part_two_result=CheckResult_Ok(Part.Two, "part_two_ok"),
            ),
        )

        # Verify only expected events fired.
        self.assertSequenceEqual(events.start_solver_calls, [solver_m])
        self.assertSequenceEqual(events.finish_solver_calls, [(solver_m, result)])

        self.assertSequenceEqual(
            events.start_part_calls, [(solver_m, Part.One), (solver_m, Part.Two)]
        )
        self.assertSequenceEqual(
            events.finish_part_calls,
            [
                (solver_m, Part.One, result.part_one),
                (solver_m, Part.Two, result.part_two),
            ],
        )

        self.assertSequenceEqual(
            events.examples_passed_calls,
            [(solver_m, Part.One, 0), (solver_m, Part.Two, 0)],
        )

        # Verify answer cache has recorded the submitted answer.
        self.assertEqual(answer_cache[0], PartAnswerCache(correct_answer="part_one_ok"))
        self.assertEqual(answer_cache[1], PartAnswerCache(correct_answer="part_two_ok"))

    def test_client_returns_wrong_with_hint(self):
        # Construct and run solver.
        solver_m = SolverMetadata(
            klass=DecoratedTestSolution,
            day=5,
            year=2012,
            puzzle_name="test puzzle",
        )
        client = MockAocClient(
            part_one_response=SubmitResponse.AlreadyAnswered,
            part_two_response=SubmitResponse.TooHigh,
        )
        events = MockSolverEventHandlers()
        answer_cache = [PartAnswerCache(), PartAnswerCache()]

        # Part one has the right answer but two is too high.
        result = run_solver(
            solver_m,
            PuzzleData(
                input="part_two_high",
                part_one_answer=answer_cache[0],
                part_two_answer=answer_cache[1],
            ),
            client=client,
            events=events,
        )

        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Ok(Part.One, "part_one_ok"),
                part_two_result=CheckResult_Wrong(
                    part=Part.Two,
                    actual_answer=128,
                    expected_answer=None,
                    hint=CheckHint.TooHigh,
                ),
            ),
        )

        self.assertSequenceEqual(events.start_solver_calls, [solver_m])
        self.assertSequenceEqual(events.finish_solver_calls, [(solver_m, result)])

        self.assertSequenceEqual(
            events.start_part_calls, [(solver_m, Part.One), (solver_m, Part.Two)]
        )
        self.assertSequenceEqual(
            events.finish_part_calls,
            [
                (solver_m, Part.One, result.part_one),
                (solver_m, Part.Two, result.part_two),
            ],
        )

        self.assertSequenceEqual(
            events.examples_passed_calls,
            [(solver_m, Part.One, 0), (solver_m, Part.Two, 0)],
        )

        # Verify answer cache has recorded the submitted answer.
        self.assertEqual(answer_cache[0], PartAnswerCache(correct_answer="part_one_ok"))
        self.assertEqual(answer_cache[1], PartAnswerCache(high_boundary=128))

        # Part one is too high but part two is fine.
        client = MockAocClient(part_one_response=SubmitResponse.TooLow)
        events = MockSolverEventHandlers()
        answer_cache = [
            PartAnswerCache(),
            PartAnswerCache(correct_answer="part_two_ok"),
        ]

        result = run_solver(
            solver_m,
            PuzzleData(
                input="part_one_low",
                part_one_answer=answer_cache[0],
                part_two_answer=answer_cache[1],
            ),
            client=client,
            events=events,
        )

        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Wrong(
                    part=Part.One,
                    actual_answer=-50,
                    expected_answer=None,
                    hint=CheckHint.TooLow,
                ),
                part_two_result=CheckResult_Ok(Part.One, "part_two_ok"),
            ),
        )

        self.assertSequenceEqual(events.start_solver_calls, [solver_m])
        self.assertSequenceEqual(events.finish_solver_calls, [(solver_m, result)])

        self.assertSequenceEqual(
            events.start_part_calls, [(solver_m, Part.One), (solver_m, Part.Two)]
        )
        self.assertSequenceEqual(
            events.finish_part_calls,
            [
                (solver_m, Part.One, result.part_one),
                (solver_m, Part.Two, result.part_two),
            ],
        )

        self.assertSequenceEqual(
            events.examples_passed_calls,
            [(solver_m, Part.One, 0), (solver_m, Part.Two, 0)],
        )

        # Verify answer cache has recorded the submitted answer.
        self.assertEqual(answer_cache[0], PartAnswerCache(low_boundary=-50))
        self.assertEqual(answer_cache[1], PartAnswerCache(correct_answer="part_two_ok"))
