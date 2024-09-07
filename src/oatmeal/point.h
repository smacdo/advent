#include "oatmeal.h"

#include <functional>
#include <stdexcept>

struct Point {
  int x;
  int y;

  constexpr Point(const int x, const int y) : x(x), y(y) {}

  constexpr bool operator==(const Point&) const = default;
  constexpr bool operator!=(const Point&) const = default;

  constexpr friend Point operator-(Point lhs) { return Point(-lhs.x, -lhs.y); }

  constexpr Point& operator+=(const Point& rhs) {
    x += rhs.x;
    y += rhs.y;
    return *this;
  }

  constexpr friend Point operator+(Point lhs, const Point& rhs) {
    lhs += rhs;
    return lhs;
  }

  constexpr Point& operator-=(const Point& rhs) {
    x -= rhs.x;
    y -= rhs.y;
    return *this;
  }

  constexpr friend Point operator-(Point lhs, const Point& rhs) {
    lhs -= rhs;
    return lhs;
  }

  constexpr Point& operator*=(const int rhs) {
    x *= rhs;
    y *= rhs;
    return *this;
  }

  constexpr friend Point operator*(Point lhs, const int rhs) {
    lhs *= rhs;
    return lhs;
  }

  constexpr Point& operator/=(const int rhs) {
    x /= rhs;
    y /= rhs;
    return *this;
  }

  constexpr friend Point operator/(Point lhs, const int rhs) {
    lhs /= rhs;
    return lhs;
  }

  constexpr Point& operator%=(const int rhs) {
    x %= rhs;
    y %= rhs;
    return *this;
  }

  constexpr friend Point operator%(Point lhs, const int rhs) {
    lhs %= rhs;
    return lhs;
  }

  constexpr int& operator[](std::size_t component_index) {
    switch (component_index) {
      case 0:
        return x;
      case 1:
        return y;
      default:
        throw std::out_of_range("component_index");
    }
  }

  constexpr const int& operator[](std::size_t component_index) const {
    switch (component_index) {
      case 0:
        return x;
      case 1:
        return y;
      default:
        throw std::out_of_range("component_index");
    }
  }
};

template<> struct std::hash<Point> {
  std::size_t operator()(const Point& p) const noexcept {
    std::size_t h1 = std::hash<int>{}(p.x);
    std::size_t h2 = std::hash<int>{}(p.y);
    return h1 ^ (h2 << 1);
  }
};

inline constexpr Point abs(const Point& p) {
  return Point(std::abs(p.x), std::abs(p.y));
}