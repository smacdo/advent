#pragma once

#include <format>
#include <functional>
#include <ostream>
#include <stdexcept>
#include <type_traits>

/// @brief A 2d point value containing X and Y components.
struct Point {
  using value_type = int;
  using size_type = std::size_t;
  using reference = value_type&;
  using const_reference = const value_type&;
  using pointer = value_type*;
  using const_pointer = const value_type*;

  /// @brief The number of components in a 2d point.
  static constexpr size_type kComponentCount = 2;

  /// @brief A point with the X and Y coordinates set to zero.
  static const Point Zero;

  /// @brief A point with the X and Y coordinates set to one.
  static const Point One;

  /// @brief A point describing the positive X axis (X = 1 and Y = 0).
  static const Point UnitX;

  /// @brief A point describing the positive Y axis (X = 0 and Y = 1).
  static const Point UnitY;

  /// @brief The X coordinate of this point.
  value_type x;

  /// @brief The Y coordinate of this point.
  value_type y;

  /// @brief Constructs a default point with X and Y set to zero.
  constexpr Point() noexcept(std::is_nothrow_constructible_v<value_type>)
      : x(0),
        y(0) {}

  /// @brief Constructs a point with X and Y from `x` and `y`.
  /// @param x The X value to set.
  /// @param y The Y value to set.
  constexpr Point(const value_type x, const value_type y) noexcept(
      std::is_nothrow_constructible_v<value_type>)
      : x(x),
        y(y) {}

  /// @brief Constructs a point with X and Y copied from `other`.
  /// @param other The point to copy from.
  constexpr Point(const Point& other) noexcept(
      std::is_nothrow_copy_constructible_v<value_type>) = default;

  friend void PrintTo(const Point& p, std::ostream* os) {
    *os << "(" << p.x << ", " << p.y << ")";
  }

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

  constexpr Point& operator*=(const value_type rhs) {
    x *= rhs;
    y *= rhs;
    return *this;
  }

  constexpr friend Point operator*(Point lhs, const value_type rhs) {
    lhs *= rhs;
    return lhs;
  }

  constexpr Point& operator/=(const value_type rhs) {
    x /= rhs;
    y /= rhs;
    return *this;
  }

  constexpr friend Point operator/(Point lhs, const value_type rhs) {
    lhs /= rhs;
    return lhs;
  }

  constexpr Point& operator%=(const value_type rhs) {
    x %= rhs;
    y %= rhs;
    return *this;
  }

  constexpr friend Point operator%(Point lhs, const value_type rhs) {
    lhs %= rhs;
    return lhs;
  }

  constexpr reference operator[](const size_type component_index) {
    switch (component_index) {
      case 0:
        return x;
      case 1:
        return y;
      default:
        throw std::out_of_range("component_index");
    }
  }

  constexpr const_reference operator[](const size_type component_index) const {
    switch (component_index) {
      case 0:
        return x;
      case 1:
        return y;
      default:
        throw std::out_of_range("component_index");
    }
  }

  constexpr auto operator<=>(const Point&) const = default;
};

template<> class std::formatter<Point> {
public:
  constexpr auto parse(format_parse_context& ctx) { return ctx.begin(); }
  template<typename Context>
  constexpr auto format(const Point& p, Context& ctx) const {
    return format_to(ctx.out(), "{}, {}", p.x, p.y);
  }
};

template<> struct std::hash<Point> {
  constexpr std::size_t operator()(const Point& p) const noexcept {
    auto h = std::hash<int>{}(p.x);
    h ^= std::hash<int>{}(p.y) + 0x9e3779b9 + (h << 6) + (h >> 2);

    return h;
  }
};

inline constexpr Point abs(const Point& p) {
  return Point(std::abs(p.x), std::abs(p.y));
}

inline constexpr Point Point::Zero{0, 0};
inline constexpr Point Point::One{1, 1};
inline constexpr Point Point::UnitX{1, 0};
inline constexpr Point Point::UnitY{0, 1};