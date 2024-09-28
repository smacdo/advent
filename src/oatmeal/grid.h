#pragma once

#include "point.h"

#include <cassert>
#include <functional>
#include <vector>

// TODO: move constructor and move assignment.

template<typename T> class Grid {
public:
  Grid(size_t x_count, size_t y_count, T defaultValue)
      : x_count_(x_count),
        y_count_(y_count),
        cells_(x_count * y_count, defaultValue) {}

  template<typename InitFunc = T(size_t, size_t)>
  Grid(size_t x_count, size_t y_count, InitFunc init)
      : x_count_(x_count),
        y_count_(y_count),
        cells_() {
    cells_.reserve(x_count_ * y_count_);
    for (size_t y = 0; y < y_count_; ++y) {
      for (size_t x = 0; x < x_count_; ++x) {
        cells_[xy_index(Point(x, y))] = init(x, y);
      }
    }
  }

  ~Grid() = default;

  size_t x_count() const { return x_count_; }
  size_t col_count() const { return x_count(); }

  size_t y_count() const { return y_count_; }
  size_t row_count() const { return y_count(); }

  size_t count() const { return cells_.size(); }

  T& operator[](Point index) { return cells_[xy_index(index)]; }

  const T& operator[](Point index) const { return cells_[xy_index(index)]; }

  T* begin() { return cells_.begin(); }
  T* end() { return cells_.end(); }

  typename std::vector<T>::const_iterator begin() const {
    return cells_.begin();
  }
  typename std::vector<T>::const_iterator end() const { return cells_.end(); }

private:
  constexpr size_t xy_index(Point p) const {
    if (p.x >= x_count_) {
      throw std::invalid_argument("x offset out of bounds");
    }

    if (p.y >= y_count_) {
      throw std::invalid_argument("y offset out of bounds");
    }

    return p.y * x_count_ + p.x;
  }

private:
  size_t x_count_;
  size_t y_count_;
  std::vector<T> cells_;
};