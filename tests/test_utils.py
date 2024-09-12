from advent.utils import (
    first_and_last,
    split,
    unzip,
    count_if,
    all_pairs,
    combinations,
    expect_re_match,
)
import re
import unittest


class TestExpectReMatch(unittest.TestCase):
    def test_with_pattern(self):
        pattern = re.compile("(\\d+):(\\d+)")
        m = expect_re_match(pattern, "13:2")

        self.assertIsNotNone(m)
        self.assertEqual("13", m.group(1))
        self.assertEqual("2", m.group(2))

    def test_with_str_pattern(self):
        m = expect_re_match("(\\d+):(\\d+)", "13:2")

        self.assertIsNotNone(m)
        self.assertEqual("13", m.group(1))
        self.assertEqual("2", m.group(2))

    def test_no_match_throws_exception(self):
        pattern = re.compile("(\\d+):(\\d+)")
        self.assertRaises(Exception, lambda: expect_re_match(pattern, "13:-8"))


class TestSplit(unittest.TestCase):
    def test_ignore_empty(self):
        self.assertSequenceEqual(
            ["12", "x", "4123"],
            split(text=" 12 x   4123 ", sep=" ", ignore_empty=True),
        )

    def test_do_not_ignore_empty(self):
        self.assertSequenceEqual(
            ["", "12", "x", "", "", "4123", "", ""],
            split(text=" 12 x   4123  ", sep=" ", ignore_empty=False),
        )

    # TODO: test trim_whitespace


class TestCountIf(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(0, count_if([], lambda x: False))
        self.assertEqual(0, count_if(iter([]), lambda x: False))

    def test_count(self):
        self.assertEqual(2, count_if([1, 2, 3, 4], lambda x: x % 2 == 0))

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            count_if(1)  # type: ignore


class TestFirstAndLast(unittest.TestCase):
    def test_one_item_list(self):
        self.assertEqual((10, 10), first_and_last([10]))

    def test_multi_item_list(self):
        self.assertEqual((13, 3), first_and_last([13, 3]))
        self.assertEqual((81, "a"), first_and_last([81, "a"]))

    def test_empty_list_throws_exception(self):
        self.assertRaises(StopIteration, lambda: first_and_last([]))

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            first_and_last(2)  # type: ignore


class TestUnzip(unittest.TestCase):
    def test_unzip_2(self):
        A = [5, 8, 10]
        B = [-2, 12, "b"]
        self.assertEqual((A, B), unzip([(5, -2), (8, 12), (10, "b")]))

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            unzip(1)  # type: ignore


class TestAllPairs(unittest.TestCase):
    def test_empty_list(self):
        self.assertSequenceEqual([], list(all_pairs([])))

    def test_single_element_list(self):
        self.assertSequenceEqual([], list(all_pairs([1])))

    def test_double_element_list(self):
        self.assertSequenceEqual([(1, 2)], list(all_pairs([1, 2])))

    def test_multi_element_list(self):
        self.assertSequenceEqual(
            [("a", "b"), ("a", "c"), ("a", "d"), ("b", "c"), ("b", "d"), ("c", "d")],
            list(all_pairs(["a", "b", "c", "d"])),
        )

    def test_not_list(self):
        with self.assertRaises(TypeError):
            list(all_pairs(5))  # type: ignore


class TestCombinations(unittest.TestCase):
    def test_k(self):
        self.assertSequenceEqual(
            [[1], [2], [3], [4]], list(combinations(1, [1, 2, 3, 4]))
        )
        self.assertSequenceEqual(
            [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]],
            list(combinations(2, [1, 2, 3, 4])),
        )
        self.assertSequenceEqual(
            [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]],
            list(combinations(3, [1, 2, 3, 4])),
        )
        self.assertSequenceEqual(
            [[1, 2, 3, 4]],
            list(combinations(4, [1, 2, 3, 4])),
        )

    def test_bad_k(self):
        with self.assertRaises(ValueError):
            list(combinations(0, [1, 2, 3, 4]))
        with self.assertRaises(ValueError):
            list(combinations(5, [1, 2, 3, 4]))

    def test_bad_types(self):
        with self.assertRaises(TypeError):
            list(combinations("2", [1, 2, 3, 4]))  # type: ignore
        with self.assertRaises(TypeError):
            list(combinations(5, "abc"))  # type: ignore


if __name__ == "__main__":
    unittest.main()
