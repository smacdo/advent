#pragma once

#include <cassert>
#include <concepts>
#include <format>
#include <functional>
#include <stdexcept>

template<typename T> struct TVec2 {
  static const TVec2 Zero;
  static const TVec2 One;
  static const TVec2 UnitX;
  static const TVec2 UnitY;

  T x;
  T y;

  constexpr TVec2() : x(0), y(0) {}
  constexpr TVec2(const T x, const T y) : x(x), y(y) {}

  constexpr T length() const {
    return static_cast<T>(std::sqrt(length_squared()));
  }

  constexpr T length_squared() const { return x * x + y * y; }

  constexpr T dot(const TVec2& other) const {
    return x * other.x + y * other.y;
  }

  /*constexpr*/ TVec2 normalized() const {
    const auto lsquared = length_squared();
    const auto one_over_lsquared = 1 / sqrt(lsquared);

    return TVec2(x * one_over_lsquared, y * one_over_lsquared);
  }

  constexpr bool operator==(const TVec2&) const = default;
  constexpr bool operator!=(const TVec2&) const = default;

  constexpr friend TVec2 operator-(TVec2 lhs) { return TVec2(-lhs.x, -lhs.y); }

  constexpr TVec2& operator+=(const TVec2& rhs) {
    x += rhs.x;
    y += rhs.y;
    return *this;
  }

  constexpr friend TVec2 operator+(TVec2 lhs, const TVec2& rhs) {
    lhs += rhs;
    return lhs;
  }

  constexpr TVec2& operator-=(const TVec2& rhs) {
    x -= rhs.x;
    y -= rhs.y;
    return *this;
  }

  constexpr friend TVec2 operator-(TVec2 lhs, const TVec2& rhs) {
    lhs -= rhs;
    return lhs;
  }

  constexpr TVec2& operator*=(const T rhs) {
    x *= rhs;
    y *= rhs;
    return *this;
  }

  constexpr friend TVec2 operator*(TVec2 lhs, const T rhs) {
    lhs *= rhs;
    return lhs;
  }

  constexpr TVec2& operator/=(const T rhs) {
    x /= rhs;
    y /= rhs;
    return *this;
  }

  constexpr friend TVec2 operator/(TVec2 lhs, const T rhs) {
    lhs /= rhs;
    return lhs;
  }

  constexpr TVec2& operator%=(const T rhs) {
    x %= rhs;
    y %= rhs;
    return *this;
  }

  constexpr friend TVec2 operator%(TVec2 lhs, const T rhs)
    requires std::integral<T>
  {
    lhs %= rhs;
    return lhs;
  }

  constexpr T& operator[](std::size_t component_index) {
    switch (component_index) {
      case 0:
        return x;
      case 1:
        return y;
      default:
        throw std::out_of_range("component_index");
    }
  }

  constexpr const T& operator[](std::size_t component_index) const {
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

template<typename T> class std::formatter<TVec2<T>> {
public:
  constexpr auto parse(format_parse_context& ctx) { return ctx.begin(); }
  template<typename Context>
  constexpr auto format(const TVec2<T>& v, Context& ctx) const {
    return format_to(ctx.out(), "{}, {}", v.x, v.y);
  }
};

template<typename T> struct std::hash<TVec2<T>> {
  std::size_t operator()(const TVec2<T>& v) const noexcept {
    std::size_t h1 = std::hash<int>{}(v.x);
    std::size_t h2 = std::hash<int>{}(v.y);
    return h1 ^ (h2 << 1);
  }
};

template<typename T> inline constexpr TVec2<T> abs(const TVec2<T>& v) {
  return TVec2(std::abs(v.x), std::abs(v.y));
}

template<> inline constexpr TVec2<float> TVec2<float>::Zero{0.f, 0.f};
template<> inline constexpr TVec2<double> TVec2<double>::Zero{0., 0.};
template<> inline constexpr TVec2<int> TVec2<int>::Zero{0, 0};

template<> inline constexpr TVec2<float> TVec2<float>::One{1.f, 1.f};
template<> inline constexpr TVec2<double> TVec2<double>::One{1., 1.};
template<> inline constexpr TVec2<int> TVec2<int>::One{1, 1};

template<> inline constexpr TVec2<float> TVec2<float>::UnitX{1.f, 0.f};
template<> inline constexpr TVec2<double> TVec2<double>::UnitX{1., 0.};
template<> inline constexpr TVec2<int> TVec2<int>::UnitX{1, 0};

template<> inline constexpr TVec2<float> TVec2<float>::UnitY{0.f, 1.f};
template<> inline constexpr TVec2<double> TVec2<double>::UnitY{0., 1.};
template<> inline constexpr TVec2<int> TVec2<int>::UnitY{0, 1};

using FVec2 = TVec2<float>;
using IVec2 = TVec2<int>;
using Vec2 = FVec2;