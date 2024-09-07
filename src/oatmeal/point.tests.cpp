#include "point.h"

#include <gtest/gtest.h>

TEST(PointTest, ConstructorSetsXY) {
  Point p{5, -2};

  EXPECT_EQ(p.x, 5);
  EXPECT_EQ(p.y, -2);
}