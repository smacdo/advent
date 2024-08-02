from advent.data import FileBackedPuzzleStore, PuzzleData
from pathlib import Path
import unittest
import tempfile


class PuzzleDataTests(unittest.TestCase):
    def test_eq(self):
        pd = PuzzleData("hello world", "part one", "part TWO")
        self.assertEqual(pd, pd)
        self.assertEqual(pd, PuzzleData("hello world", "part one", "part TWO"))
        self.assertNotEqual(pd, PuzzleData("hello world", "part one", ""))
        self.assertNotEqual(pd, PuzzleData("hello world", "", "part TWO"))
        self.assertNotEqual(pd, PuzzleData("hello world", "", ""))
        self.assertNotEqual(pd, PuzzleData("", "", ""))


class FileBackedPuzzleStoreTests(unittest.TestCase):
    def test_set_and_read_back(self):
        with tempfile.TemporaryDirectory() as tempdir:
            f = FileBackedPuzzleStore(Path(tempdir))

            # Write three days of input
            pd0 = PuzzleData("hello world", "p1a", "p2a")
            pd1 = PuzzleData("why hello there", "p2a", "p2\na")
            pd2 = PuzzleData("testing\n1\n23", "\npart\n\none", "part two")

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
            f = FileBackedPuzzleStore(Path(tempdir))

            pd0 = PuzzleData("hello world", "p1a", "p2a")
            pd1 = PuzzleData("why hello there", "p2a", "p2\na")
            pd2 = PuzzleData("testing\n1\n23", "\npart\n\none", "part two")

            f.set(0, pd0)
            f.set(1, pd1)
            f.set(5, pd2)

            # Read back the days as a list.
            self.assertSequenceEqual(f.days(), [0, 1, 5])
