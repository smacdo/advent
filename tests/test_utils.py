from advent.utils import (
    Range,
    ValueCanNotBeNoneError,
    find_digits,
    find_ints,
    first_and_last,
    last,
    merge_ranges,
    not_none,
    split,
    first,
    unzip,
    count_if,
    all_pairs,
    combinations,
    expect_re_match,
)
import re
import unittest


class TestNotNone(unittest.TestCase):
    def test_with_values(self):
        self.assertEqual(5, not_none(5))
        self.assertEqual(5, not_none(4 + 1))
        self.assertEqual("hello", not_none("hello"))

    def test_with_none(self):
        self.assertRaises(ValueCanNotBeNoneError, lambda: not_none(None))


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


class TestStringParsing(unittest.TestCase):
    def test_split_ignore_empty(self):
        self.assertSequenceEqual(
            ["12", "x", "4123"],
            split(text=" 12 x   4123 ", sep=" ", ignore_empty=True),
        )

    def test_splt_do_not_ignore_empty(self):
        self.assertSequenceEqual(
            ["", "12", "x", "", "", "4123", "", ""],
            split(text=" 12 x   4123  ", sep=" ", ignore_empty=False),
        )

    # TODO: test split trim_whitespace parameter

    def test_find_ints(self):
        self.assertSequenceEqual([], find_ints(""))
        self.assertSequenceEqual([34, -231, 0, 8], find_ints("he34  -231  0 - - 8"))

    def test_find_digits(self):
        self.assertSequenceEqual([], find_digits(""))
        self.assertSequenceEqual(
            [5, 3, 2, 1, 8, 3, 2, 1], find_digits("5x-321  8\n\t3 2.1")
        )


class TestCountIf(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(0, count_if([], lambda x: False))
        self.assertEqual(0, count_if(iter([]), lambda x: False))

    def test_count(self):
        self.assertEqual(2, count_if([1, 2, 3, 4], lambda x: x % 2 == 0))

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            count_if(1)  # type: ignore


class TestFirst(unittest.TestCase):
    def test_try_first_list(self):
        self.assertEqual(10, first([10]))
        self.assertEqual(5, first([5, 10]))
        self.assertEqual(-8, first([-8, 38, 100]))

    def test_try_first_empty_uses_default(self):
        self.assertIsNone(first([]))
        self.assertEqual("hello", first([], default="hello"))


class TestLast(unittest.TestCase):
    def test_try_first_list(self):
        self.assertEqual(10, last([10]))
        self.assertEqual(15, last([10, 15]))
        self.assertEqual(100, last([-8, -200, 100]))

    def test_try_first_empty_uses_default(self):
        self.assertIsNone(last([]))
        self.assertEqual(321, last([], default=321))


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


class TestRange(unittest.TestCase):
    def test_init_with_zero_or_negative_length_raises_exception(self):
        self.assertRaises(ValueError, lambda: Range(3, 0))
        self.assertRaises(ValueError, lambda: Range(3, -1))

    def test_str(self):
        self.assertEqual("[4, 6]", str(Range(4, 3)))

    def test_contains(self):
        r = Range(4, 3)

        self.assertFalse(-3 in r)
        self.assertFalse(3 in r)
        self.assertTrue(4 in r)
        self.assertTrue(5 in r)
        self.assertTrue(6 in r)
        self.assertFalse(7 in r)
        self.assertFalse(8 in r)

    def test_overlaps(self):
        r = Range(4, 3)  # [ 4, 5, 6 ]

        self.assertTrue(r.overlaps(Range(4, 3)))
        self.assertTrue(r.overlaps(Range(6, 1)))
        self.assertTrue(r.overlaps(Range(5, 2)))
        self.assertTrue(r.overlaps(Range(4, 10)))
        self.assertTrue(r.overlaps(Range(-1, 6)))
        self.assertTrue(r.overlaps(Range(-2, 8)))

        self.assertFalse(r.overlaps(Range(1, 1)))
        self.assertFalse(r.overlaps(Range(1, 3)))
        self.assertFalse(r.overlaps(Range(3, 1)))
        self.assertFalse(r.overlaps(Range(7, 1)))
        self.assertFalse(r.overlaps(Range(7, 2)))
        self.assertFalse(r.overlaps(Range(10, 5)))

    def test_iter(self):
        r = Range(4, 3)
        self.assertEqual([4, 5, 6], list(r))

    def test_iter_reverse(self):
        r = Range(4, 3)
        self.assertEqual([6, 5, 4], list(reversed(r)))

    def test_length(self):
        self.assertEqual(3, len(Range(4, 3)))

    def test_get(self):
        r = Range(4, 3)
        self.assertEqual(4, r[0])
        self.assertEqual(5, r[1])
        self.assertEqual(6, r[2])

    def test_get_negative(self):
        r = Range(4, 3)
        self.assertEqual(6, r[-1])
        self.assertEqual(5, r[-2])
        self.assertEqual(4, r[-3])

    def test_get_raises_exception_if_past_bounds(self):
        r = Range(4, 3)
        self.assertRaises(IndexError, lambda: r[3])
        self.assertRaises(IndexError, lambda: r[-4])

    def test_set_is_not_supported(self):
        def f():
            r = Range(4, 3)
            r[0] = 0

        self.assertRaises(NotImplementedError, lambda: f())

    def test_del_is_not_supported(self):
        def f():
            r = Range(4, 3)
            del r[0]

        self.assertRaises(NotImplementedError, lambda: f())

    def test_split(self):
        #                10 | 11 | 12 | 13 | 14 | 15
        # 7  | 8  | 9  | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17

        #                10 | 11           | 14 | 15
        #                        | 12 | 13
        self.assertEqual(
            (Range(10, 2), Range(12, 2), Range(14, 2)), Range(10, 6).split(Range(12, 2))
        )

        #                -
        #                10 | 11 | 12 | 13 | 14 | 15
        self.assertEqual((None, Range(10, 6), None), Range(10, 6).split(Range(10, 6)))
        self.assertEqual((None, Range(10, 6), None), Range(10, 6).split(Range(9, 8)))

        #                10 | 11 | 12 | 13
        #                                  | 14 | 15
        self.assertEqual(
            (Range(10, 4), Range(14, 2), None), Range(10, 6).split(Range(14, 2))
        )
        self.assertEqual(
            (Range(10, 4), Range(14, 2), None), Range(10, 6).split(Range(14, 3))
        )

        #                               13 | 14 | 15
        #                10 | 11 | 12 |
        self.assertEqual(
            (None, Range(10, 3), Range(13, 3)), Range(10, 6).split(Range(10, 3))
        )
        self.assertEqual(
            (None, Range(10, 3), Range(13, 3)), Range(10, 6).split(Range(9, 4))
        )

    def test_split_none(self):
        self.assertIsNone(Range(10, 6).split(Range(7, 2)))
        self.assertIsNone(Range(10, 6).split(Range(7, 3)))
        self.assertIsNone(Range(10, 6).split(Range(16, 10)))
        self.assertIsNone(Range(10, 6).split(Range(17, 10)))

    def test_sort(self):
        self.assertSequenceEqual(
            [Range(-1, 10), Range(4, 2), Range(10, 22)],
            sorted(
                [
                    Range(4, 2),
                    Range(10, 22),
                    Range(-1, 10),
                ]
            ),
        )

    def test_merge(self):
        self.assertSequenceEqual([], merge_ranges([]))
        self.assertSequenceEqual([Range(4, 3)], merge_ranges([Range(4, 3)]))

        self.assertSequenceEqual(
            [Range(3, 11)], merge_ranges([Range(3, 3), Range(4, 10)])
        )
        self.assertSequenceEqual(
            [Range(3, 11)], merge_ranges([Range(6, 8), Range(3, 8)])
        )
        self.assertSequenceEqual(
            [Range(4, 5)], merge_ranges([Range(4, 2), Range(6, 3)])
        )
        self.assertSequenceEqual(
            [Range(0, 2), Range(3, 7)], merge_ranges([Range(3, 7), Range(0, 2)])
        )

        self.assertSequenceEqual(
            [Range(1, 8), Range(10, 5)],
            merge_ranges([Range(1, 3), Range(4, 2), Range(6, 3), Range(10, 5)]),
        )
