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
        if input == "part_one_fail":
            return "part_one_bad_output"
        elif input == "part_one_low":
            return -50
        elif input == "part_one_not_finished":
            return None
        elif input == "part_one_int":
            return 22

        return "part_one_ok"

    def part_two(self, input: str) -> MaybeAnswerType:
        if input == "part_two_fail":
            return "part_two_bad_output"
        elif input == "part_two_high":
            return 128
        elif input == "part_two_not_finished":
            return None
        elif input == "part_two_int":
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
    examples_passed_calls: list[SolverMetadata]
    part_ok_calls: list[tuple[MaybeAnswerType, SolverMetadata, Part]]
    part_wrong_calls: list[tuple[CheckResult, SolverMetadata, Part]]

    def __init__(self):
        super().__init__()
        self.examples_passed_calls = []
        self.part_ok_calls = []
        self.part_wrong_calls = []

    def on_examples_passed(self, solver_metadata: SolverMetadata):
        self.examples_passed_calls.append(solver_metadata)

    def on_part_ok(
        self, answer: MaybeAnswerType, solver_metadata: SolverMetadata, part: Part
    ):
        self.part_ok_calls.append((answer, solver_metadata, part))

    def on_part_wrong(
        self, result: CheckResult, solver_metadata: SolverMetadata, part: Part
    ):
        self.part_wrong_calls.append((result, solver_metadata, part))


class RunSolverResultTests(unittest.TestCase):
    def test_get_result(self):
        part_one_result = CheckResult_Ok(Part.One)
        part_two_result = CheckResult_Wrong(Part.One, "actual", 42, hint=None)

        r = RunSolverResult(
            part_one_result=part_one_result,
            part_two_result=part_two_result,
        )

        self.assertEqual(r.get_result(Part.One), part_one_result)
        self.assertEqual(r.get_result(Part.Two), part_two_result)

        self.assertNotEqual(part_one_result, part_two_result)

    def test_set_result(self):
        part_one_result = CheckResult_Ok(Part.One)
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
        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Ok(Part.One),
                part_two_result=CheckResult_Ok(Part.Two),
            ),
        )

        # Verify only expected events fired.
        self.assertSequenceEqual(events.examples_passed_calls, [solver_m])
        self.assertSequenceEqual(
            events.part_ok_calls,
            [("part_one_ok", solver_m, Part.One), ("part_two_ok", solver_m, Part.Two)],
        )
        self.assertSequenceEqual(events.part_wrong_calls, [])

    def test_examples_fail_and_solver_exits_early(self):
        # Construct and run solver.
        solver_m = SolverMetadata(
            klass=DecoratedTestSolution,
            day=5,
            year=2012,
            puzzle_name="test puzzle",
            examples=[
                Example(input="part_two_fail", output="part_two_output", part=Part.Two)
            ],
        )
        events = MockSolverEventHandlers()

        puzzle = PuzzleData(
            input="",
            part_one_answer=PartAnswerCache(),
            part_two_answer=PartAnswerCache(),
        )

        # Verify part two example fails and no further events happen beyond
        # example checking.
        result = run_solver(solver_m, puzzle, MockAocClient(), events)
        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=None,
                part_two_result=CheckResult_ExampleFailed(
                    "part_two_bad_output", list(solver_m.examples(Part.Two))[0]
                ),
            ),
        )

        self.assertSequenceEqual(events.examples_passed_calls, [])
        self.assertSequenceEqual(events.part_ok_calls, [])
        self.assertSequenceEqual(
            events.part_wrong_calls,
            [
                (
                    CheckResult_ExampleFailed(
                        "part_two_bad_output", solver_m._part_two_examples[0]
                    ),
                    solver_m,
                    Part.Two,
                )
            ],
        )

        # Adjust test so that the next solver run will cause part one to have an
        # incorrect example.
        solver_m.add_example(
            Example(input="part_one_fail", output="part_one_output", part=Part.One)
        )

        # Verify part two example fails and no further events happen beyond
        # example checking.
        events = MockSolverEventHandlers()
        result = run_solver(solver_m, puzzle, MockAocClient(), events=events)

        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_ExampleFailed(
                    "part_one_bad_output", list(solver_m.examples(Part.One))[0]
                ),
                part_two_result=None,
            ),
        )

        self.assertSequenceEqual(events.examples_passed_calls, [])
        self.assertSequenceEqual(events.part_ok_calls, [])
        self.assertSequenceEqual(
            events.part_wrong_calls,
            [
                (
                    CheckResult_ExampleFailed(
                        "part_one_bad_output", solver_m._part_one_examples[0]
                    ),
                    solver_m,
                    Part.One,
                )
            ],
        )

    def test_example_with_str_when_solver_returns_int(self):
        # Construct and run solver.
        solver_m = SolverMetadata(
            klass=DecoratedTestSolution,
            day=5,
            year=2012,
            puzzle_name="test puzzle",
            examples=[
                Example(input="part_one_int", output="22", part=Part.One),
                Example(input="part_two_int", output="-127", part=Part.Two),
            ],
        )
        events = MockSolverEventHandlers()

        puzzle = PuzzleData(
            input="",
            part_one_answer=PartAnswerCache(),
            part_two_answer=PartAnswerCache(),
        )

        # Verify both examples pass.
        result = run_solver(solver_m, puzzle, MockAocClient(), events)
        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Ok(Part.One),
                part_two_result=CheckResult_Ok(Part.Two),
            ),
        )

        self.assertSequenceEqual(events.examples_passed_calls, [solver_m])
        self.assertSequenceEqual(
            events.part_ok_calls, [(22, solver_m, Part.One), (-127, solver_m, Part.Two)]
        )
        self.assertSequenceEqual(events.part_wrong_calls, [])

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
                part_one_result=CheckResult_Ok(Part.One),
                part_two_result=CheckResult_Wrong(
                    part=Part.Two,
                    actual_answer="part_two_bad_output",
                    expected_answer="part_two_ok",
                    hint=None,
                ),
            ),
        )

        self.assertSequenceEqual(events.examples_passed_calls, [solver_m])
        self.assertSequenceEqual(
            events.part_ok_calls, [("part_one_ok", solver_m, Part.One)]
        )
        self.assertSequenceEqual(
            events.part_wrong_calls,
            [
                (
                    result.get_result(Part.Two),
                    solver_m,
                    Part.Two,
                )
            ],
        )

        # Both part one and part two will return wrong answers found in the
        # answer cache. Verify that only the first part is tested and then
        # exited early.
        events = MockSolverEventHandlers()
        result = run_solver(
            solver_m,
            PuzzleData(
                input="part_one_fail",
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
                part_two_result=None,
            ),
        )

        self.assertSequenceEqual(events.examples_passed_calls, [solver_m])
        self.assertSequenceEqual(events.part_ok_calls, [])
        self.assertSequenceEqual(
            events.part_wrong_calls,
            [
                (
                    result.get_result(Part.One),
                    solver_m,
                    Part.One,
                )
            ],
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
                part_one_result=CheckResult_Ok(Part.One),
                part_two_result=CheckResult_Wrong(
                    part=Part.Two,
                    actual_answer=128,
                    expected_answer=None,
                    hint=CheckHint.TooHigh,
                ),
            ),
        )

        self.assertSequenceEqual(events.examples_passed_calls, [solver_m])
        self.assertSequenceEqual(
            events.part_ok_calls, [("part_one_ok", solver_m, Part.One)]
        )
        self.assertSequenceEqual(
            events.part_wrong_calls,
            [
                (
                    result.get_result(Part.Two),
                    solver_m,
                    Part.Two,
                )
            ],
        )

        # Part one and two have wrong answers. Only part one is run.
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
                part_two_result=None,
            ),
        )

        self.assertSequenceEqual(events.examples_passed_calls, [solver_m])
        self.assertSequenceEqual(events.part_ok_calls, [])
        self.assertSequenceEqual(
            events.part_wrong_calls,
            [
                (
                    result.get_result(Part.One),
                    solver_m,
                    Part.One,
                )
            ],
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
                part_one_result=CheckResult_Ok(Part.One),
                part_two_result=CheckResult_NotFinished(part=Part.Two),
            ),
        )

        self.assertSequenceEqual(events.examples_passed_calls, [solver_m])
        self.assertSequenceEqual(
            events.part_ok_calls, [("part_one_ok", solver_m, Part.One)]
        )
        self.assertSequenceEqual(
            events.part_wrong_calls,
            [
                (
                    result.get_result(Part.Two),
                    solver_m,
                    Part.Two,
                )
            ],
        )

        # Part one and two have unfinished answers. Only part one is tried.
        events = MockSolverEventHandlers()
        result = run_solver(
            solver_m,
            PuzzleData(
                input="part_one_not_finished",
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
                part_two_result=None,
            ),
        )

        self.assertSequenceEqual(events.examples_passed_calls, [solver_m])
        self.assertSequenceEqual(events.part_ok_calls, [])
        self.assertSequenceEqual(
            events.part_wrong_calls,
            [
                (
                    result.get_result(Part.One),
                    solver_m,
                    Part.One,
                )
            ],
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
                part_one_result=CheckResult_Ok(Part.One),
                part_two_result=CheckResult_Ok(Part.Two),
            ),
        )

        # Verify only expected events fired.
        self.assertSequenceEqual(events.examples_passed_calls, [solver_m])
        self.assertSequenceEqual(
            events.part_ok_calls,
            [("part_one_ok", solver_m, Part.One), ("part_two_ok", solver_m, Part.Two)],
        )
        self.assertSequenceEqual(events.part_wrong_calls, [])

        self.assertSequenceEqual(
            client.submit_answer_calls,
            [(2012, 5, Part.One, "part_one_ok"), (2012, 5, Part.Two, "part_two_ok")],
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
                part_one_result=CheckResult_Ok(Part.One),
                part_two_result=CheckResult_TooSoon(Part.Two),
            ),
        )

        # Verify only expected events fired.
        self.assertSequenceEqual(events.examples_passed_calls, [solver_m])
        self.assertSequenceEqual(
            events.part_ok_calls,
            [("part_one_ok", solver_m, Part.One)],
        )
        self.assertSequenceEqual(
            events.part_wrong_calls,
            [
                (
                    result.get_result(Part.Two),
                    solver_m,
                    Part.Two,
                )
            ],
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
                part_one_result=CheckResult_Ok(Part.One),
                part_two_result=CheckResult_Ok(Part.Two),
            ),
        )

        # Verify only expected events fired.
        self.assertSequenceEqual(events.examples_passed_calls, [solver_m])
        self.assertSequenceEqual(
            events.part_ok_calls,
            [("part_one_ok", solver_m, Part.One), ("part_two_ok", solver_m, Part.Two)],
        )
        self.assertSequenceEqual(events.part_wrong_calls, [])

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
                part_one_result=CheckResult_Ok(Part.One),
                part_two_result=CheckResult_Wrong(
                    part=Part.Two,
                    actual_answer=128,
                    expected_answer=None,
                    hint=CheckHint.TooHigh,
                ),
            ),
        )

        self.assertSequenceEqual(events.examples_passed_calls, [solver_m])
        self.assertSequenceEqual(
            events.part_ok_calls, [("part_one_ok", solver_m, Part.One)]
        )
        self.assertSequenceEqual(
            events.part_wrong_calls,
            [
                (
                    result.get_result(Part.Two),
                    solver_m,
                    Part.Two,
                )
            ],
        )

        # Verify answer cache has recorded the submitted answer.
        self.assertEqual(answer_cache[0], PartAnswerCache(correct_answer="part_one_ok"))
        self.assertEqual(answer_cache[1], PartAnswerCache(high_boundary=128))

        # Part one and two have wrong answers. Only part one is run.
        client = MockAocClient(part_one_response=SubmitResponse.TooLow)
        events = MockSolverEventHandlers()
        answer_cache = [PartAnswerCache(), PartAnswerCache()]

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
                part_two_result=None,
            ),
        )

        self.assertSequenceEqual(events.examples_passed_calls, [solver_m])
        self.assertSequenceEqual(events.part_ok_calls, [])
        self.assertSequenceEqual(
            events.part_wrong_calls,
            [
                (
                    result.get_result(Part.One),
                    solver_m,
                    Part.One,
                )
            ],
        )

        # Verify answer cache has recorded the submitted answer.
        self.assertEqual(answer_cache[0], PartAnswerCache(low_boundary=-50))
        self.assertEqual(answer_cache[1], PartAnswerCache())
