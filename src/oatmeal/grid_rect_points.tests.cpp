#include "grid.h"

#include "point.h"

#include <gtest/gtest.h>

#include <vector>

TEST(GridRectPointsTest, BeginEndReturnExpectedValues) {
  constexpr GridRectPoints points(Point(4, 7), 2, 3);
  EXPECT_EQ(points.begin(), GridRectPoints::Iterator(Point(4, 7), 2));
  EXPECT_EQ(points.end(), GridRectPoints::Iterator(Point(4, 10)));
}

TEST(GridRectPointsTest, IteratePointsLeftToRightTopToBottom) {
  /**
   *    (4, 7)   (5, 7)
   *    (4, 8)   (5, 8)
   *    (4, 9)   (5, 9)
   */
  constexpr GridRectPoints points(Point(4, 7), 2, 3);
  auto itr = points.begin();

  EXPECT_EQ(*itr++, Point(4, 7));
  EXPECT_EQ(*itr++, Point(5, 7));
  EXPECT_EQ(*itr++, Point(4, 8));
  EXPECT_EQ(*itr++, Point(5, 8));
  EXPECT_EQ(*itr++, Point(4, 9));
  EXPECT_EQ(*itr++, Point(5, 9));

  // Verify the next value is the same as the sentinel.
  ASSERT_EQ(*itr, Point(4, 10));
  ASSERT_EQ(itr, points.end());
}

TEST(GridRectPointsTest, IteratorBeginEndMagic) {
  constexpr GridRectPoints points(Point(4, 7), 2, 3);
  const std::vector<Point> expected = {
      Point(4, 7),
      Point(5, 7),
      Point(4, 8),
      Point(5, 8),
      Point(4, 9),
      Point(5, 9),
  };

  std::vector<Point> vec_points;

  for (const auto p : points) {
    vec_points.push_back(p);
  }

  EXPECT_EQ(vec_points, expected);

  EXPECT_EQ(std::vector<Point>(points.begin(), points.end()), expected);
}
