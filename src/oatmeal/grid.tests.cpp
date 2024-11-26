#include "grid.h"

#include <gmock/gmock.h>
#include <gtest/gtest.h>

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

TEST(GridTest, GetThrowsIfOutOfRange) {
  Grid<char> g(3, 2, ' ');

  EXPECT_THROW({ const auto bad = g[Point(-1, 0)]; }, std::out_of_range);
  EXPECT_THROW({ const auto bad = g[Point(0, -9)]; }, std::out_of_range);
  EXPECT_THROW({ const auto bad = g[Point(210, 1)]; }, std::out_of_range);
  EXPECT_THROW({ const auto bad = g[Point(2, 2)]; }, std::out_of_range);
  EXPECT_THROW({ const auto bad = g[Point(3, 2)]; }, std::out_of_range);
}

TEST(GridTest, SetThrowsIfOutOfRange) {
  Grid<char> g(3, 2, ' ');

  EXPECT_THROW({ g[Point(-1, 0)] = 'x'; }, std::out_of_range);
  EXPECT_THROW({ g[Point(0, -9)] = 'x'; }, std::out_of_range);
  EXPECT_THROW({ g[Point(210, 1)] = 'x'; }, std::out_of_range);
  EXPECT_THROW({ g[Point(2, 2)] = 'x'; }, std::out_of_range);
  EXPECT_THROW({ g[Point(3, 2)] = 'x'; }, std::out_of_range);
}

TEST(GridTest, PointInBounds) {
  Grid<char> g(3, 2, ' ');

  EXPECT_TRUE(g.contains_point(Point(0, 0)));
  EXPECT_TRUE(g.contains_point(Point(2, 0)));
  EXPECT_TRUE(g.contains_point(Point(0, 1)));
  EXPECT_TRUE(g.contains_point(Point(2, 1)));

  EXPECT_FALSE(g.contains_point(Point(-1, 0)));
  EXPECT_FALSE(g.contains_point(Point(0, -1)));
  EXPECT_FALSE(g.contains_point(Point(-1, -1)));

  EXPECT_FALSE(g.contains_point(Point(3, 1)));
  EXPECT_FALSE(g.contains_point(Point(1, 2)));
  EXPECT_FALSE(g.contains_point(Point(6, 4)));

  EXPECT_FALSE(g.contains_point(Point(-3213213, 123)));
}

TEST(GridTest, IteratePointsX) {
  GridRectPoints::Iterator itr(Point(3, 2), 1);
  EXPECT_EQ(*itr, Point(3, 2));

  itr++;
  EXPECT_EQ(*itr, Point(3, 3));
}

TEST(GridTest, IterateRows) {
  Grid<char> g(3, 4, ' ');
  auto r = g.rows();

  EXPECT_EQ(r.count(), 4);

  const auto expected = std::vector<size_t>{0, 1, 2, 3};
  EXPECT_EQ(std::vector(r.begin(), r.end()), expected);
}

TEST(GridTest, RowAccessorThrowsExceptionIfIndexOutOfRange) {
  Grid<char> g(3, 4, ' ');
  EXPECT_THROW({ const auto itr = g.row(4); }, std::out_of_range);
  EXPECT_THROW({ const auto itr = g.row(10); }, std::out_of_range);
}

TEST(GridTest, IterateCellsInRow) {
  Grid<char> g(3, 4, ' ');
  const auto points = g.row(2);

  const auto expected =
      std::vector<Point>{Point(0, 2), Point(1, 2), Point(2, 2)};
  EXPECT_EQ(std::vector(points.begin(), points.end()), expected);
}

TEST(GridTest, IterateCellsInRowWithRowIterator) {
  Grid<char> g(3, 4, ' ');
  const auto points = g.row(Grid<char>::RowIterator(0));

  const auto expected =
      std::vector<Point>{Point(0, 0), Point(1, 0), Point(2, 0)};
  EXPECT_EQ(std::vector(points.begin(), points.end()), expected);
}

TEST(GridTest, IterateRowSubset) {
  Grid<char> g(4, 10, ' ');
  const auto rows = g.rows(3, 4);
  const auto expected = std::vector<size_t>{3, 4, 5, 6};
  EXPECT_EQ(std::vector(rows.begin(), rows.end()), expected);
}

TEST(GridTest, IterateRowSubsetX) {
  Grid<char> g(4, 10, ' ');

  for (const auto row : g.rows()) {
    // for (const auto p : g.row())
  }
}

TEST(GridTest, RowsThrowsExceptionIfOutOfBounds) {
  EXPECT_THROW({ Grid<char>(3, 5, ' ').rows(5, 4); }, std::out_of_range);
  EXPECT_THROW({ Grid<char>(3, 5, ' ').rows(4, 2); }, std::out_of_range);
  EXPECT_THROW({ Grid<char>(3, 5, ' ').rows(4, 3); }, std::out_of_range);
  EXPECT_THROW({ Grid<char>(3, 5, ' ').rows(1, 9); }, std::out_of_range);
}

TEST(GridTest, RowsConstructorThrowsExceptionIfEndSmallerThanBegin) {
  EXPECT_THROW({ Grid<char>::Rows(5, 5); }, std::out_of_range);
  EXPECT_THROW({ Grid<char>::Rows(5, 4); }, std::out_of_range);
}
