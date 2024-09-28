#include "grid.h"

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <vector>

using namespace ::testing;

TEST(GridTest, ConstructorCreatesGridOfSizeXY) {
  Grid<int> g{3, 2, int()};
  EXPECT_EQ(g.x_count(), 3);
  EXPECT_EQ(g.y_count(), 2);
}

TEST(GridTest, ConstructorInitsToDefaultValue) {
  Grid<int> g{3, 2, 22};

  for (size_t y = 0; y < 2; ++y) {
    for (size_t x = 0; x < 3; ++x) {
      EXPECT_EQ(g[Point(x, y)], 22)
          << "grid cell " << x << ", " << y << " must be 22";
    }
  }
}

TEST(GridTest, ConstructorInitWithFunc) {
  Grid<int> g{3, 2, [](size_t x, size_t y) { return y * 100 + x; }};

  g[Point(0, 0)] = 0;
  g[Point(1, 0)] = 1;
  g[Point(2, 0)] = 2;

  g[Point(0, 0)] = 100;
  g[Point(1, 0)] = 101;
  g[Point(2, 0)] = 102;
}

TEST(GridTest, GetAndSetCells) {
  Grid<char> g(3, 2, ' ');

  EXPECT_EQ(g[Point(1, 0)], ' ');

  g[Point(0, 0)] = 'h';
  g[Point(2, 0)] = 'i';
  g[Point(2, 1)] = '!';

  EXPECT_EQ(g[Point(1, 0)], ' ');
  EXPECT_EQ(g[Point(0, 0)], 'h');
  EXPECT_EQ(g[Point(2, 0)], 'i');
  EXPECT_EQ(g[Point(2, 1)], '!');
}

// TODO: Test that get [] raises invalid_argument if x or y out of bounds.
// TODO: Test that set [] raises invalid_argument if x or y out of bounds.

TEST(GridTest, IterateCellsConst) {
  const Grid<int> g{3, 2, [](size_t x, size_t y) { return y * 100 + x; }};
  const auto vec = std::vector<int>(g.begin(), g.end());

  ASSERT_THAT(vec, ElementsAre(0, 1, 2, 100, 101, 102));
}