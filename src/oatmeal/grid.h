#pragma once

#include "point.h"

#include <exception>
#include <functional>
#include <iterator>
#include <type_traits>
#include <vector>

// TODO: Move this into Grid as inner type.
struct GridRectPoints {
public:
  /// Iterates through all the points in a `GridRectPoints` value.
  struct Iterator {
  public:
    using difference_type = std::ptrdiff_t;
    using element_type = Point;
    using pointer = element_type*;
    using reference = element_type&;

    /// Default constructor.
    constexpr Iterator() = default;

    constexpr Iterator(Point begin, size_t x_count)
        : current_(begin),
          x_count_(x_count),
          start_x_(begin.x) {
      if (x_count == 0) {
        throw std::invalid_argument("x_count must be larger than zero");
      }
    }

    constexpr Iterator(Point begin)
        : current_(begin),
          x_count_(0),
          start_x_(begin.x) {}

    constexpr element_type operator*() const { return current_; }

    constexpr element_type const* operator->() const { return &current_; }

    constexpr Iterator& operator++() {
      if (current_.x - start_x_ + 1 >= x_count_) {
        current_.x = start_x_;
        current_.y += 1;
      } else {
        current_.x += 1;
      }

      return *this;
    }

    constexpr Iterator operator++(int) {
      const auto tmp(*this);
      ++(*this);

      return tmp;
    }

    constexpr friend bool operator==(const Iterator& a, const Iterator& b) {
      return a.current_ == b.current_;
    }

    constexpr friend bool operator!=(const Iterator& a, const Iterator& b) {
      return a.current_ != b.current_;
    }

  protected:
    Point current_;
    size_t x_count_;
    int start_x_;
  };

public:
  constexpr GridRectPoints(Point begin, size_t x_count, size_t y_count)
      : begin_(begin),
        x_count_(x_count),
        y_count_(y_count) {
    if (x_count == 0) {
      throw std::invalid_argument("x_count must be larger than zero");
    }
    if (y_count == 0) {
      throw std::invalid_argument("y_count must be larger than zero");
    }
  }

  constexpr Iterator begin() const { return Iterator(begin_, x_count_); }

  constexpr Iterator cbegin() const { return Iterator(begin_, x_count_); }

  constexpr Iterator end() const {
    return Iterator(Point(begin_.x, begin_.y + y_count_));
  }

  constexpr Iterator cend() const {
    return Iterator(Point(begin_.x, begin_.y + y_count_));
  }

protected:
  Point begin_;
  size_t x_count_;
  size_t y_count_;
};

/// A 2d array.
template<typename T> class Grid {
public:
  using value_type = T;
  using size_type = std::size_t;
  using reference = value_type&;
  using const_reference = const value_type&;
  using pointer = value_type*;

  struct RowIterator {
    using difference_type = std::ptrdiff_t;
    using element_type = size_type;
    using pointer = element_type*;
    using reference = element_type&;

    constexpr RowIterator() = default;

    constexpr RowIterator(size_type row) : row_(row) {}

    constexpr element_type operator*() const { return row_; }

    constexpr RowIterator& operator++() {
      row_++;
      return *this;
    }

    constexpr RowIterator operator++(int) {
      const auto tmp(*this);
      ++(*this);

      return tmp;
    }

    constexpr auto operator<=>(const RowIterator& other) const = default;

  protected:
    size_type row_;
  };

  struct Rows {
    constexpr Rows(size_type begin, size_type end) : begin_(begin), end_(end) {
      if (end_ <= begin_) {
        throw std::out_of_range("Row `end` must be larger than `begin`");
      }
    }

    constexpr size_type count() const { return end_ - begin_; }

    constexpr RowIterator begin() const { return RowIterator(begin_); }
    constexpr RowIterator cbegin() const { return RowIterator(begin_); }

    constexpr RowIterator end() const { return RowIterator(end_); }
    constexpr RowIterator cend() const { return RowIterator(end_); }

  protected:
    size_type begin_;
    size_type end_;
  };

  /// Initialize a grid of `x_count` columns, `y_count` rows, and set each
  /// cell's value to `defaultValue`.
  Grid(size_type x_count, size_type y_count, value_type defaultValue)
      : x_count_(x_count),
        y_count_(y_count),
        cells_(x_count * y_count, defaultValue) {}

  /// Initialize a grid of `x_count` columns, `y_count` rows, and set each cell
  /// to the value returned by invoking `init` on the cell's position.
  template<typename InitFunc = value_type(size_type, size_type)>
  Grid(size_type x_count, size_type y_count, InitFunc init)
      : x_count_(x_count),
        y_count_(y_count),
        cells_() {
    cells_.reserve(x_count_ * y_count_);
    for (size_type y = 0; y < y_count_; ++y) {
      for (size_type x = 0; x < x_count_; ++x) {
        cells_.emplace_back(init(x, y));
      }
    }
  }

  /// Default move constructor.
  Grid(Grid&& t) = default;

  /// Default assignment operator.
  Grid& operator=(Grid&& other) = default;

  /// Default destructor.
  ~Grid() = default;

  /// Returns the number of columns in the grid.
  size_type x_count() const { return x_count_; }

  /// Returns the number of columns in the grid.
  size_type col_count() const { return x_count(); }

  /// Returns the number of rows in the grid.
  size_type y_count() const { return y_count_; }

  /// Returns the number of rows in the grid.
  size_type row_count() const { return y_count(); }

  /// Returns the number of cells in the grid.
  size_type count() const { return cells_.size(); }

  /// Returns true if point `p` refers to a valid cell in this grid, otherwise
  /// returns false to indicate out of bounds.
  bool contains_point(Point p) const {
    return p.x >= 0 && p.y >= 0 && p.x < x_count_ && p.y < y_count_;
  }

  /// Returns an iterator over the rows in the grid.
  Rows rows() const { return rows(0, y_count_); }

  /// Returns an iterator over the rows in `[row, row + count)`.
  /// NOTE: `row + count` cannot be larger than `row_count()`.
  Rows rows(size_type row, size_type count) const {
    if (row >= y_count_) {
      throw std::out_of_range("row index must be less than grid y_count_");
    } else if (row + count > y_count_) {
      throw std::out_of_range(
          "row index + count must be less than grid y_count_");
    }

    return Rows(row, row + count);
  }

  /// Returns an iterator that generates all the points representing cells for
  /// the given row.
  constexpr GridRectPoints row(size_type row) const {
    if (row >= y_count_) {
      throw std::out_of_range("row index must be less than grid y_count_");
    }

    return GridRectPoints(Point(0, row), x_count_, 1);
  }

  /// Returns an iterator that generates all the points representing cells for
  /// the given row.
  constexpr GridRectPoints row(RowIterator itr) const { return row(*itr); }

  /// Returns a reference to the cell at point `p`.
  reference operator[](Point p) { return cells_[xy_index(p)]; }

  /// Returns a const reference to the cell at point `p`.
  const_reference operator[](Point p) const { return cells_[xy_index(p)]; }

  // TODO: consider taking iterator GridRectPoints iterator []

  typename std::vector<value_type>::iterator begin() { return cells_.begin(); }

  typename std::vector<value_type>::iterator end() { return cells_.end(); }

  typename std::vector<value_type>::const_iterator begin() const {
    return cells_.begin();
  }

  typename std::vector<value_type>::const_iterator end() const {
    return cells_.end();
  }

  typename std::vector<value_type>::const_iterator cbegin() const {
    return cells_.begin();
  }

  typename std::vector<value_type>::const_iterator cend() const {
    return cells_.end();
  }

private:
  /// Convert a (x,y) index to a 1d offset into the grid's array of cells.
  /// Throws an exception if the point is out of bounds.
  constexpr size_type xy_index(Point p) const { return xy_index(p.x, p.y); }

  /// Convert a (x,y) index to a 1d offset into the grid's array of cells.
  /// Throws an exception if the point is out of bounds.
  constexpr size_t xy_index(const int x, const int y) const {
    if (x < 0) {
      throw std::out_of_range("x must be a positive value");
    }
    if (y < 0) {
      throw std::out_of_range("y must be a positive value");
    }

    if (x >= x_count_) {
      throw std::out_of_range("x must be less than number of columns in grid");
    }

    if (y >= y_count_) {
      throw std::out_of_range("y must be less than number of rows in grid");
    }

    return unchecked_xy_index(x, y);
  }

  /// Convert a (x,y) index to a 1d offset into the grid's array of cells.
  constexpr size_type unchecked_xy_index(Point p) const {
    return unchecked_xy_index(p.x, p.y);
  }

  /// Convert a (x,y) index to a 1d offset into the grid's array of cells.
  constexpr size_type unchecked_xy_index(const int x, const int y) const {
    return y * x_count_ + x;
  }

private:
  /// The number of columns in this grid.
  size_type x_count_;
  /// The number of rows in this grid.
  size_type y_count_;
  /// The cells of this grid stored in row major order.
  std::vector<value_type> cells_;
};

static_assert(std::is_nothrow_move_constructible_v<Grid<int>>);
static_assert(std::is_nothrow_move_assignable_v<Grid<int>>);
