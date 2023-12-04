import logging
import unittest


class Point:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"

    def __str__(self):
        return f"{self.x}, {self.y}"

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise Exception(f"cannot get subscript [{key}] for Point object")

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise Exception(f"cannot set subscript [{key}] for Point object")

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Point(self.x * other, self.y * other)

    def __truediv__(self, other):
        return Point(self.x / other, self.y / other)

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __abs__(self):
        return Point(abs(self.x), abs(self.y))

    def __hash__(self):
        return hash((self.x, self.y))


class TestPoint(unittest.TestCase):
    def test_new_points(self):
        p = Point(-16, 2)
        self.assertEqual(p.x, -16)
        self.assertEqual(p.y, 2)

    def test_point_to_string(self):
        self.assertEqual("-4, -123", f"{Point(-4, -123)}")

    def test_point_repr(self):
        self.assertEqual("Point(x=-4, y=-123)", repr(Point(-4, -123)))

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


def init_logging(default_level=logging.INFO):
    add_logging_level("TRACE", logging.DEBUG - 5)
    logging.basicConfig(level=default_level)


def add_logging_level(level_name, level_num):
    # Simplified version of https://stackoverflow.com/a/35804945
    method_name = level_name.lower()

    # Generate a function that implements logging at the requested logging level
    # by checking if it is enabled first.
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    def log_to_root(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    # Register the new log level with the Python logging system.
    logging.addLevelName(level_num, level_name)

    setattr(logging, level_name, level_num)  # Add `logging.$level_name = $level_num`
    setattr(logging.getLoggerClass(), method_name, logForLevel)
    setattr(logging, method_name, log_to_root)


class TestUtilsModule(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
