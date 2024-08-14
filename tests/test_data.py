from advent.data import (
    AnswerResponse,
    FileBackedPuzzleStore,
    PartAnswerCache,
    PuzzleData,
)
from pathlib import Path
import unittest
import tempfile


class FileBackedPuzzleStoreTests(unittest.TestCase):
    def test_set_and_read_back(self):
        with tempfile.TemporaryDirectory() as tempdir:
            f = FileBackedPuzzleStore(Path(tempdir), year=1969)

            # Write three days of input
            pd0 = PuzzleData(
                "hello world", PartAnswerCache("p1a"), PartAnswerCache("p2a")
            )
            pd1 = PuzzleData(
                "why hello there", PartAnswerCache("foo"), PartAnswerCache("blah")
            )
            pd2 = PuzzleData(
                "testing\n1\n23", PartAnswerCache("part1"), PartAnswerCache("part two")
            )

            f.set(0, pd0)
            f.set(1, pd1)
            f.set(5, pd2)

            # Read back the three days of input
            self.assertEqual(f.get(0), pd0)
            self.assertEqual(f.get(1), pd1)
            self.assertEqual(f.get(5), pd2)

    def test_set_and_read_back_with_missing_fields(self):
        with tempfile.TemporaryDirectory() as tempdir:
            f = FileBackedPuzzleStore(Path(tempdir), year=1969)

            # Write three days of input
            pd0 = PuzzleData("hello world", PartAnswerCache(), PartAnswerCache("p2a"))
            pd1 = PuzzleData(
                "why hello there", PartAnswerCache("p2a"), PartAnswerCache()
            )
            pd2 = PuzzleData("testing\n1\n23", PartAnswerCache(), PartAnswerCache())

            f.set(0, pd0)
            f.set(1, pd1)
            f.set(5, pd2)

            # Read back the three days of input
            self.assertEqual(f.get(0), pd0)
            self.assertEqual(f.get(1), pd1)
            self.assertEqual(f.get(5), pd2)

    def test_get_days(self):
        with tempfile.TemporaryDirectory() as tempdir:
            # Create a useless directory that shouldn't be included in the day
            # list.
            (Path(tempdir) / "NOT_A_DAY").mkdir()

            # Set three days of input.
            f = FileBackedPuzzleStore(Path(tempdir), year=1969)

            pd0 = PuzzleData(
                "hello world", PartAnswerCache("p1a"), PartAnswerCache("p2a")
            )
            pd1 = PuzzleData(
                "why hello there", PartAnswerCache("foo"), PartAnswerCache("blah")
            )
            pd2 = PuzzleData(
                "testing\n1\n23", PartAnswerCache("part1"), PartAnswerCache("part two")
            )

            f.set(0, pd0)
            f.set(1, pd1)
            f.set(5, pd2)

            # Read back the days as a list.
            self.assertSequenceEqual(f.days(), [0, 1, 5])

    def test_has_days(self):
        with tempfile.TemporaryDirectory() as tempdir:
            # Create a useless directory that shouldn't be included in the day
            # list.
            (Path(tempdir) / "NOT_A_DAY").mkdir()

            # Set three days of input.
            f = FileBackedPuzzleStore(Path(tempdir), year=1969)

            pd0 = PuzzleData(
                "hello world", PartAnswerCache("p1a"), PartAnswerCache("p2a")
            )
            pd1 = PuzzleData(
                "why hello there", PartAnswerCache("foo"), PartAnswerCache("blah")
            )
            pd2 = PuzzleData(
                "testing\n1\n23", PartAnswerCache("part1"), PartAnswerCache("part two")
            )

            f.set(0, pd0)
            f.set(1, pd1)
            f.set(5, pd2)

            # Check if only days 0, 1 and 5 exist.
            self.assertTrue(f.has_day(0))
            self.assertTrue(f.has_day(1))
            self.assertTrue(f.has_day(5))

            self.assertFalse(f.has_day(2))
            self.assertFalse(f.has_day(3))
            self.assertFalse(f.has_day(4))
            self.assertFalse(f.has_day(6))

    def test_add_day(self):
        with tempfile.TemporaryDirectory() as tempdir:
            f = FileBackedPuzzleStore(Path(tempdir), year=1969)

            # Write three days of input
            f.add_day(0, "hello world")
            f.add_day(1, "why hello there")
            f.add_day(5, "testing\n1\n23")

            # Read back the three days of input
            self.assertEqual(
                f.get(0),
                PuzzleData("hello world", PartAnswerCache(), PartAnswerCache()),
            )
            self.assertEqual(
                f.get(1),
                PuzzleData("why hello there", PartAnswerCache(), PartAnswerCache()),
            )
            self.assertEqual(
                f.get(5),
                PuzzleData("testing\n1\n23", PartAnswerCache(), PartAnswerCache()),
            )


class PartAnswerCacheTests(unittest.TestCase):
    def test_right_answer_when_checking(self):
        pac = PartAnswerCache(
            correct_answer="hello", wrong_answers=set(["abc", "stop"])
        )
        self.assertEqual(pac.check_answer("hello"), AnswerResponse.Ok)

    def test_wrong_answer_cache(self):
        pac = PartAnswerCache(
            correct_answer="hello", wrong_answers=set(["abc", "stop"])
        )

        self.assertEqual(pac.check_answer("abc"), AnswerResponse.Wrong)
        self.assertEqual(pac.check_answer("stop"), AnswerResponse.Wrong)
        self.assertEqual(pac.check_answer("hello"), AnswerResponse.Ok)

    def test_add_wrong_answers(self):
        pac = PartAnswerCache()
        pac.add_wrong_answer("incorrect")
        pac.add_wrong_answer("5")

        self.assertIn("incorrect", pac.wrong_answers)
        self.assertIn("5", pac.wrong_answers)

    def test_set_lower_high_boundary_replaces_prev(self):
        pac = PartAnswerCache()

        self.assertEqual(pac.set_high_boundary(30), 30)
        self.assertEqual(pac.high_boundary, 30)

        self.assertEqual(pac.set_high_boundary(31), 30)
        self.assertEqual(pac.high_boundary, 30)

        self.assertEqual(pac.set_high_boundary(12), 12)
        self.assertEqual(pac.high_boundary, 12)

    def test_set_higher_low_boundary_replaces_prev(self):
        pac = PartAnswerCache()

        self.assertEqual(pac.set_low_boundary(4), 4)
        self.assertEqual(pac.low_boundary, 4)

        self.assertEqual(pac.set_low_boundary(-2), 4)
        self.assertEqual(pac.low_boundary, 4)

        self.assertEqual(pac.set_low_boundary(187), 187)
        self.assertEqual(pac.low_boundary, 187)

    def test_check_answer_checks_low_if_set(self):
        pac = PartAnswerCache()
        self.assertEqual(pac.check_answer(100), AnswerResponse.Unknown)

        pac.set_low_boundary(90)

        self.assertEqual(pac.check_answer(100), AnswerResponse.Unknown)
        self.assertEqual(pac.check_answer(85), AnswerResponse.TooLow)
        self.assertEqual(pac.check_answer(90), AnswerResponse.TooLow)

    def test_check_answer_checks_high_if_set(self):
        pac = PartAnswerCache()
        self.assertEqual(pac.check_answer(100), AnswerResponse.Unknown)

        pac.set_high_boundary(90)

        self.assertEqual(pac.check_answer(100), AnswerResponse.TooHigh)
        self.assertEqual(pac.check_answer(85), AnswerResponse.Unknown)
        self.assertEqual(pac.check_answer(90), AnswerResponse.TooHigh)

    def test_check_answer_checks_low_high_if_set(self):
        pac = PartAnswerCache()
        self.assertEqual(pac.check_answer(107), AnswerResponse.Unknown)

        pac.set_low_boundary(96)
        pac.set_high_boundary(103)

        self.assertEqual(pac.check_answer(107), AnswerResponse.TooHigh)
        self.assertEqual(pac.check_answer(103), AnswerResponse.TooHigh)
        self.assertEqual(pac.check_answer(100), AnswerResponse.Unknown)
        self.assertEqual(pac.check_answer(98), AnswerResponse.Unknown)
        self.assertEqual(pac.check_answer(96), AnswerResponse.TooLow)
        self.assertEqual(pac.check_answer(-5), AnswerResponse.TooLow)

    def test_check_answer_bounds_checked_if_int_or_int_str(self):
        pac = PartAnswerCache(
            low_boundary=-50, high_boundary=25, wrong_answers={"-9", "1", "xyz"}
        )

        self.assertEqual(pac.check_answer("55"), AnswerResponse.TooHigh)
        self.assertEqual(pac.check_answer(55), AnswerResponse.TooHigh)

        self.assertEqual(pac.check_answer(10), AnswerResponse.Unknown)
        self.assertEqual(pac.check_answer("10"), AnswerResponse.Unknown)

        self.assertEqual(pac.check_answer("-74"), AnswerResponse.TooLow)
        self.assertEqual(pac.check_answer(-74), AnswerResponse.TooLow)

    def test_check_answer_bounds_skipped_if_not_int_str(self):
        pac = PartAnswerCache(
            low_boundary=-50, high_boundary=25, wrong_answers={"-9", "1", "xyz"}
        )

        self.assertEqual(pac.check_answer("55.0"), AnswerResponse.Unknown)
        self.assertEqual(pac.check_answer("abc"), AnswerResponse.Unknown)
        self.assertEqual(pac.check_answer("32x"), AnswerResponse.Unknown)

    def test_wrong_answers_if_in_bounds(self):
        pac = PartAnswerCache(
            low_boundary=-50,
            high_boundary=25,
            wrong_answers={"-9", "1", "100", "-100", "xyz"},
        )

        self.assertEqual(pac.check_answer("-9"), AnswerResponse.Wrong)
        self.assertEqual(pac.check_answer(-9), AnswerResponse.Wrong)
        self.assertEqual(pac.check_answer("1"), AnswerResponse.Wrong)
        self.assertEqual(pac.check_answer(1), AnswerResponse.Wrong)
        self.assertEqual(pac.check_answer("xyz"), AnswerResponse.Wrong)
        self.assertEqual(pac.check_answer("100"), AnswerResponse.TooHigh)
        self.assertEqual(pac.check_answer(100), AnswerResponse.TooHigh)
        self.assertEqual(pac.check_answer("-100"), AnswerResponse.TooLow)
        self.assertEqual(pac.check_answer(-100), AnswerResponse.TooLow)

    def test_answers_are_wrong_when_there_is_correct_answer_that_does_not_match(self):
        pac = PartAnswerCache(correct_answer="yes")

        self.assertEqual(pac.check_answer("yes"), AnswerResponse.Ok)
        self.assertEqual(pac.check_answer("no"), AnswerResponse.Wrong)
        self.assertEqual(pac.check_answer("maybe"), AnswerResponse.Wrong)

    def test_serialize_answer_cache(self):
        pac = PartAnswerCache(
            correct_answer="12",
            low_boundary=-50,
            high_boundary=25,
            wrong_answers={"-9", "1", "100", "xyz"},
        )

        self.assertEqual(pac.serialize(), "= 12\n[ -50\n] 25\nX -9\nX 1\nX 100\nX xyz")

        pac = PartAnswerCache(
            low_boundary=-50,
            high_boundary=25,
            wrong_answers={"-9", "1", "100", "xyz"},
        )

        self.assertEqual(pac.serialize(), "[ -50\n] 25\nX -9\nX 1\nX 100\nX xyz")

        pac = PartAnswerCache(
            high_boundary=25,
            wrong_answers={"-9", "1", "100", "xyz"},
        )

        self.assertEqual(pac.serialize(), "] 25\nX -9\nX 1\nX 100\nX xyz")

        pac = PartAnswerCache()

        self.assertEqual(pac.serialize(), "")

    def test_serialize_answers_with_newlines(self):
        pac = PartAnswerCache(
            wrong_answers={"-9", "new\nline", "blah"},
        )
        self.assertRaises(ValueError, lambda: pac.serialize())

        pac = PartAnswerCache(correct_answer="hello\nworld")
        self.assertRaises(ValueError, lambda: pac.serialize())

    def test_deserialize_answer_cache(self):
        pac = PartAnswerCache.deserialize("= 12\n[ -50\n] 25\nX -9\nX 1\nX 100\nX xyz")
        self.assertEqual(pac.correct_answer, "12")
        self.assertEqual(pac.low_boundary, -50)
        self.assertEqual(pac.high_boundary, 25)
        self.assertIn("-9", pac.wrong_answers)
        self.assertIn("1", pac.wrong_answers)
        self.assertIn("100", pac.wrong_answers)
        self.assertIn("xyz", pac.wrong_answers)

    def test_deserialize_answers_with_spaces(self):
        pac = PartAnswerCache.deserialize("= hello world\nX foobar\nX one two three")
        self.assertEqual(pac.correct_answer, "hello world")
        self.assertIn("foobar", pac.wrong_answers)
        self.assertIn("one two three", pac.wrong_answers)
