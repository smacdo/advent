from oatmeal import Point
import unittest
import copy
import pickle


class TestPoint(unittest.TestCase):
    def test_new_point(self):
        p = Point(-16, 2)
        self.assertEqual(p.x, -16)
        self.assertEqual(p.y, 2)

    def test_copy(self):
        p = Point(-16, 2)
        a = p
        b = copy.copy(p)

        a.x = 22
        b.x = 13

        self.assertEqual(22, p.x)
        self.assertEqual(22, a.x)
        self.assertEqual(13, b.x)

    def test_deep_copy(self):
        p = Point(-16, 2)
        a = p
        b = copy.deepcopy(p)

        a.x = 22
        b.x = 13

        self.assertEqual(22, p.x)
        self.assertEqual(22, a.x)
        self.assertEqual(13, b.x)

    def test_pickle(self):
        a = Point(317, -18)
        b = pickle.loads(pickle.dumps(a))
        self.assertEqual(a, b)

    def test_clone(self):
        p = Point(-16, 2)
        a = p
        b = p.clone()

        a.x = 22
        b.x = 13

        self.assertEqual(22, p.x)
        self.assertEqual(22, a.x)
        self.assertEqual(13, b.x)

    def test_to_string(self):
        self.assertEqual("-4, -123", f"{Point(-4, -123)}")

    def test_repr(self):
        self.assertEqual("oatmeal.Point(-4, -123)", repr(Point(-4, -123)))

    def test_get_set_by_index(self):
        p = Point(16, 8123)
        self.assertEqual(p[0], 16)
        self.assertEqual(p[1], 8123)

        p[0] = 2
        p[1] = -4

        self.assertEqual(p[0], 2)
        self.assertEqual(p[1], -4)

    def test_get_set_by_index_throw_exception_if_not_0_or_1(self):
        def try_get_invalid():
            p = Point(5, 6)
            p[2]

        def try_set_invalid():
            p = Point(5, 6)
            p[2] = 0

        self.assertRaises(Exception, try_get_invalid)
        self.assertRaises(Exception, try_set_invalid)

    def test_equal_not_equal(self):
        self.assertEqual(Point(5, 13), Point(5 + 0, 15 - 2))
        self.assertNotEqual(Point(5, 13), Point(6, 13))
        self.assertNotEqual(Point(5, 13), Point(5, 12))

    def test_math_ops(self):
        self.assertEqual(Point(18, -4), Point(20, -5) + Point(-2, 1))
        self.assertEqual(Point(17, 1), Point(20, -5) - Point(3, -6))
        self.assertEqual(Point(-24, -8), Point(6, 2) * -4)
        self.assertEqual(Point(6, 2), Point(-24, -8) / -4)
        self.assertEqual(Point(-3, 2), Point(-7, 5) // 2)
        self.assertEqual(Point(1, 2), Point(7, 5) % 3)
        self.assertEqual(Point(4, -123), -Point(-4, 123))
        self.assertEqual(Point(4, 123), abs(Point(-4, 123)))

    def test_hash(self):
        points = dict()
        points[Point(3, -15)] = "hello"

        self.assertIn(Point(3, -15), points)
        self.assertEqual(points[Point(3, -15)], "hello")
        self.assertEqual(points[Point(2, -18) + Point(1, 3)], "hello")

        self.assertIn(Point(3, -15), points)
        self.assertNotIn(Point(3, 15), points)
        self.assertNotIn(Point(16, 7), points)
