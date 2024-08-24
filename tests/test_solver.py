from typing import List
import unittest

from advent.aoc.client import AocCalendarDay, AocClient, SubmitResponse
from advent.data import PartAnswerCache, PuzzleData
from advent.solution import AbstractSolver, Example, Part, SolverMetadata
from advent.solver import (
    CheckHint,
    CheckResult,
    CheckResult_ExampleFailed,
    CheckResult_NotFinished,
    CheckResult_Ok,
    CheckResult_Wrong,
    RunSolverResult,
    SolverEventHandlers,
    run_solver,
)


class DecoratedTestSolution(AbstractSolver):
    def part_one(self, input: str) -> int | str | None:
        if input == "part_one_fail":
            return "part_one_bad_output"
        elif input == "part_one_low":
            return -50
        elif input == "part_one_not_finished":
            return None

        return "part_one_ok"

    def part_two(self, input: str) -> int | str | None:
        if input == "part_two_fail":
            return "part_two_bad_output"
        elif input == "part_two_high":
            return 128
        elif input == "part_two_not_finished":
            return None

        return "part_two_ok"


class MockAocClient(AocClient):
    def fetch_input_for(self, year: int, day: int) -> str:
        raise NotImplementedError

    def fetch_days(self, year: int) -> List[AocCalendarDay]:
        raise NotImplementedError

    def submit_answer(
        self, year: int, day: int, part: Part, answer: str
    ) -> SubmitResponse:
        raise NotImplementedError


class MockSolverEventHandlers(SolverEventHandlers):
    def on_examples_passed(self, solver_metadata: SolverMetadata):
        pass

    def on_part_ok(
        self, answer: int | str | None, solver_metadata: SolverMetadata, part: Part
    ):
        pass

    def on_part_wrong(
        self, result: CheckResult, solver_metadata: SolverMetadata, part: Part
    ):
        pass


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
    def test_correct_answers(self):
        # Part one has the right answer but two is too high.
        result = run_solver(
            SolverMetadata(
                klass=DecoratedTestSolution, day=5, year=2012, puzzle_name="test puzzle"
            ),
            PuzzleData(
                input="plz_work",
                part_one_answer=PartAnswerCache(correct_answer="part_one_ok"),
                part_two_answer=PartAnswerCache(correct_answer="part_two_ok"),
            ),
            MockAocClient(),
            MockSolverEventHandlers(),
        )
        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Ok(Part.One),
                part_two_result=CheckResult_Ok(Part.Two),
            ),
        )

    def test_examples_for_solver_fail(self):
        solver_info = SolverMetadata(
            klass=DecoratedTestSolution, day=5, year=2012, puzzle_name="test puzzle"
        )
        solver_info.add_example(
            Example(input="part_two_fail", output="part_two_output", part=Part.Two)
        )
        puzzle = PuzzleData(
            input="",
            part_one_answer=PartAnswerCache(),
            part_two_answer=PartAnswerCache(),
        )

        # Test that the part two example check fails
        result = run_solver(
            solver_info, puzzle, MockAocClient(), MockSolverEventHandlers()
        )
        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=None,
                part_two_result=CheckResult_ExampleFailed(
                    "part_two_bad_output", list(solver_info.examples(Part.Two))[0]
                ),
            ),
        )

        # Test part one example fails.
        solver_info.add_example(
            Example(input="part_one_fail", output="part_one_output", part=Part.One)
        )

        result = run_solver(
            solver_info, puzzle, MockAocClient(), MockSolverEventHandlers()
        )
        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_ExampleFailed(
                    "part_one_bad_output", list(solver_info.examples(Part.One))[0]
                ),
                part_two_result=None,
            ),
        )

    def test_solver_wrong_answer(self):
        solver_info = SolverMetadata(
            klass=DecoratedTestSolution, day=5, year=2012, puzzle_name="test puzzle"
        )

        # Part one has the right answer but two has the wrong answer.
        result = run_solver(
            solver_info,
            PuzzleData(
                input="part_two_fail",
                part_one_answer=PartAnswerCache(correct_answer="part_one_ok"),
                part_two_answer=PartAnswerCache(correct_answer="part_two_ok"),
            ),
            MockAocClient(),
            MockSolverEventHandlers(),
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

        # Part one and two have wrong answers. Only part one is run.
        result = run_solver(
            solver_info,
            PuzzleData(
                input="part_one_fail",
                part_one_answer=PartAnswerCache(correct_answer="part_one_ok"),
                part_two_answer=PartAnswerCache(correct_answer="part_two_ok"),
            ),
            MockAocClient(),
            MockSolverEventHandlers(),
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

    def test_wrong_answer_with_hint(self):
        solver_info = SolverMetadata(
            klass=DecoratedTestSolution, day=5, year=2012, puzzle_name="test puzzle"
        )

        # Part one has the right answer but two is too high.
        result = run_solver(
            solver_info,
            PuzzleData(
                input="part_two_high",
                part_one_answer=PartAnswerCache(correct_answer="part_one_ok"),
                part_two_answer=PartAnswerCache(high_boundary=10),
            ),
            MockAocClient(),
            MockSolverEventHandlers(),
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

        # Part one and two have wrong answers. Only part one is run.
        result = run_solver(
            solver_info,
            PuzzleData(
                input="part_one_low",
                part_one_answer=PartAnswerCache(correct_answer="hello", low_boundary=3),
                part_two_answer=PartAnswerCache(correct_answer="part_two_ok"),
            ),
            MockAocClient(),
            MockSolverEventHandlers(),
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

    def test_not_finished_answer(self):
        solver_info = SolverMetadata(
            klass=DecoratedTestSolution, day=5, year=2012, puzzle_name="test puzzle"
        )

        # Part one has the right answer but two is not complete.
        result = run_solver(
            solver_info,
            PuzzleData(
                input="part_two_not_finished",
                part_one_answer=PartAnswerCache(correct_answer="part_one_ok"),
                part_two_answer=PartAnswerCache(correct_answer="part_two_ok"),
            ),
            MockAocClient(),
            MockSolverEventHandlers(),
        )
        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_Ok(Part.One),
                part_two_result=CheckResult_NotFinished(part=Part.Two),
            ),
        )

        # Part one and two have unfinished answers. Only part one is tried.
        result = run_solver(
            solver_info,
            PuzzleData(
                input="part_one_not_finished",
                part_one_answer=PartAnswerCache(correct_answer="part_one_ok"),
                part_two_answer=PartAnswerCache(correct_answer="part_two_ok"),
            ),
            MockAocClient(),
            MockSolverEventHandlers(),
        )
        self.assertEqual(
            result,
            RunSolverResult(
                part_one_result=CheckResult_NotFinished(Part.One),
                part_two_result=None,
            ),
        )


# TODO:
# - if part is unfinished then unfinished event is raised but no other events.
# - if part example failed then on_part_wrong only for the failed part
# - update test cases above to check for appropriate events being raised
#
# - if cache is unknown, then answer is submitted to AOC client
#    - test should check if the answer was sent in the client
#
# - if cache is unknown, answer comes back as "TooSoon" then an exception is
#     raised as "TooSoon"
#
# - if cache is unknown, answer comes back as "AlreadyAnswered"
#    - test that OK answer is written to answer cache
#    - test that an event was raised to warn about this
#
# - if cache is unknown, answer comes back as OK
#    - test that OK answer written to answer cache
#    - test that answer returned OK
#
# - if cache is unknown, answer comes back as WRONG NO HINT
#    - test that WRONG answer written to answer cache
#    - test that answer returned WRONG
#
# - if cache is unknown, answer comes back as WRONG HINT LOW|HIGH
#    - test that LOW|HI answer written to answer cache
#    - test that answer returned WRONG LOW|HIGH
#
# - if answer cache has OK, or WRONG then client is not invoked
#
#
