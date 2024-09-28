#include "point.h"

#include <gtest/gtest.h>

TEST(PointTest, ConstructorSetsXY) {
  constexpr Point p{5, -2};

  EXPECT_EQ(p.x, 5);
  EXPECT_EQ(p.y, -2);
}

TEST(PointTest, Equals) {
  constexpr Point p{5, -2};

  EXPECT_TRUE(Point(5, -2) == Point(5, -2));
  EXPECT_TRUE(Point(5, -2) == Point(4 + 1, 0 - 2));

  EXPECT_FALSE(Point(5, -2) == Point(5, 0));
  EXPECT_FALSE(Point(5, -2) == Point(0, -2));
  EXPECT_FALSE(Point(5, -2) == Point(-2, 5));
  EXPECT_FALSE(Point(5, -2) == Point(5, 2));
}

TEST(PointTest, NotEquals) {
  constexpr Point p{5, -2};

  EXPECT_FALSE(Point(5, -2) != Point(5, -2));
  EXPECT_FALSE(Point(5, -2) != Point(4 + 1, 0 - 2));

  EXPECT_TRUE(Point(5, -2) != Point(5, 0));
  EXPECT_TRUE(Point(5, -2) != Point(0, -2));
  EXPECT_TRUE(Point(5, -2) != Point(-2, 5));
  EXPECT_TRUE(Point(5, -2) != Point(5, 2));
}

TEST(PointTest, Addition) {
  constexpr Point a(3, 8);
  constexpr Point b(-5, 2);
  constexpr Point r = a + b;

  EXPECT_EQ(r, Point(-2, 10));

  auto r1 = r;
  r1 += Point(1, -3);

  EXPECT_EQ(r1, Point(-1, 7));
}

TEST(PointTest, Subtraction) {
  constexpr Point a(3, 8);
  constexpr Point b(-5, 2);
  constexpr Point r = a - b;

  EXPECT_EQ(r, Point(8, 6));

  auto r1 = r;
  r1 -= Point(1, -3);

  EXPECT_EQ(r1, Point(7, 9));
}

TEST(PointTest, Multiplication) {
  constexpr Point a(3, -8);
  constexpr Point r = a * 4;

  EXPECT_EQ(r, Point(12, -32));

  auto r1 = r;
  r1 *= -2;

  EXPECT_EQ(r1, Point(-24, 64));
}

TEST(PointTest, Division) {
  constexpr Point a(-24, 64);
  constexpr Point r = a / -2;

  EXPECT_EQ(r, Point(12, -32));

  auto r1 = r;
  r1 /= 4;

  EXPECT_EQ(r1, Point(3, -8));
}

TEST(PointTest, Modulo) {
  constexpr Point a(8, 10);
  constexpr Point r = a % 3;

  EXPECT_EQ(r, Point(2, 1));

  auto r1 = r;
  r1 %= 2;

  EXPECT_EQ(r1, Point(0, 1));
}

TEST(PointTest, GetComponent) {
  constexpr Point a(8, 10);

  constexpr auto x = a[0];
  EXPECT_EQ(x, 8);

  constexpr auto y = a[1];
  EXPECT_EQ(y, 10);
}

TEST(PointTest, GetComponentThrowsIfIndexOutOfRange) {
  constexpr Point a(8, 10);
  EXPECT_THROW({ const auto bad = a[2]; }, std::out_of_range);
}

TEST(PointTest, SetComponent) {
  Point a(0, 0);
  a[0] = 3123;
  a[1] = -918;

  EXPECT_EQ(a[0], 3123);
  EXPECT_EQ(a[1], -918);
}

TEST(PointTest, SetComponentThrowsIfIndexOutOfRange) {
  Point a(8, 10);
  EXPECT_THROW({ a[2] = 0; }, std::out_of_range);
}

TEST(PointTest, AbsoluteValue) {
  EXPECT_EQ(abs(Point(3, 6)), Point(3, 6));
  EXPECT_EQ(abs(Point(-4, 10)), Point(4, 10));
  EXPECT_EQ(abs(Point(12, -4)), Point(12, 4));
  EXPECT_EQ(abs(Point(-7, -123)), Point(7, 123));
}