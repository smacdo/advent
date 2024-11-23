#pragma once

#include <cassert>
#include <concepts>
#include <format>
#include <functional>
#include <ostream>
#include <stdexcept>

//----------------------------------------------------------------------------//
// Vector2                                                                    //
//----------------------------------------------------------------------------//
template<typename T> struct TVec2 {
  static const TVec2 Zero;
  static const TVec2 One;
  static const TVec2 UnitX;
  static const TVec2 UnitY;

  T x;
  T y;

  constexpr TVec2() noexcept(std::is_nothrow_constructible_v<T>) : x(0), y(0) {}

  constexpr TVec2(const T x, const T y) noexcept(
      std::is_nothrow_constructible_v<T>)
      : x(x),
        y(y) {}

  constexpr TVec2(const TVec2&) noexcept(
      std::is_nothrow_copy_constructible_v<T>) = default;

  template<typename U = T> constexpr U length() const {
    return static_cast<U>(std::sqrt(length_squared()));
  }

  constexpr T length_squared() const { return x * x + y * y; }

  constexpr T dot(const TVec2& other) const {
    return x * other.x + y * other.y;
  }

  constexpr TVec2 normalized() const {
    const auto lsquared = length_squared();
    const auto one_over_lsquared = 1 / sqrt(lsquared);

    return TVec2(x * one_over_lsquared, y * one_over_lsquared);
  }

  friend void PrintTo(const TVec2& v, std::ostream* os) {
    *os << "(" << v.x << ", " << v.y << ")";
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

  constexpr TVec2& operator%=(const T rhs)
    requires std::integral<T>
  {
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

  constexpr auto operator<=>(const TVec2&) const = default;
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
  constexpr std::size_t operator()(const TVec2<T>& v) const noexcept {
    auto h = std::hash<T>{}(v.x);
    h ^= std::hash<T>{}(v.y) + 0x9e3779b9 + (h << 6) + (h >> 2);

    return h;
  }
};

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

//----------------------------------------------------------------------------//
// Vector3                                                                    //
//----------------------------------------------------------------------------//
template<typename T> struct TVec3 {
  static const TVec3 Zero;
  static const TVec3 One;
  static const TVec3 UnitX;
  static const TVec3 UnitY;
  static const TVec3 UnitZ;

  T x;
  T y;
  T z;

  constexpr TVec3() noexcept(std::is_nothrow_constructible_v<T>) : x(0), y(0) {}
  constexpr TVec3(const T x, const T y, const T z) noexcept(
      std::is_nothrow_constructible_v<T>)
      : x(x),
        y(y),
        z(z) {}
  constexpr TVec3(const TVec3&) noexcept(
      std::is_nothrow_copy_constructible_v<T>) = default;

  template<typename U = T> constexpr U length() const {
    return static_cast<U>(std::sqrt(length_squared()));
  }

  constexpr T length_squared() const { return x * x + y * y + z * z; }

  constexpr T dot(const TVec3& other) const {
    return x * other.x + y * other.y + z * other.z;
  }

  constexpr TVec3 normalized() const {
    const auto lsquared = length_squared();
    const auto one_over_lsquared = 1 / sqrt(lsquared);

    return TVec3(
        x * one_over_lsquared, y * one_over_lsquared, z * one_over_lsquared);
  }

  friend void PrintTo(const TVec3& v, std::ostream* os) {
    *os << "(" << v.x << ", " << v.y << ", " << v.z << ")";
  }

  constexpr bool operator==(const TVec3&) const = default;
  constexpr bool operator!=(const TVec3&) const = default;

  constexpr friend TVec3 operator-(TVec3 lhs) {
    return TVec3(-lhs.x, -lhs.y, -lhs.z);
  }

  constexpr TVec3& operator+=(const TVec3& rhs) {
    x += rhs.x;
    y += rhs.y;
    z += rhs.z;
    return *this;
  }

  constexpr friend TVec3 operator+(TVec3 lhs, const TVec3& rhs) {
    lhs += rhs;
    return lhs;
  }

  constexpr TVec3& operator-=(const TVec3& rhs) {
    x -= rhs.x;
    y -= rhs.y;
    z -= rhs.z;
    return *this;
  }

  constexpr friend TVec3 operator-(TVec3 lhs, const TVec3& rhs) {
    lhs -= rhs;
    return lhs;
  }

  constexpr TVec3& operator*=(const T rhs) {
    x *= rhs;
    y *= rhs;
    z *= rhs;
    return *this;
  }

  constexpr friend TVec3 operator*(TVec3 lhs, const T rhs) {
    lhs *= rhs;
    return lhs;
  }

  constexpr TVec3& operator/=(const T rhs) {
    x /= rhs;
    y /= rhs;
    z /= rhs;
    return *this;
  }

  constexpr friend TVec3 operator/(TVec3 lhs, const T rhs) {
    lhs /= rhs;
    return lhs;
  }

  constexpr TVec3& operator%=(const T rhs)
    requires std::integral<T>
  {
    x %= rhs;
    y %= rhs;
    z %= rhs;
    return *this;
  }

  constexpr friend TVec3 operator%(TVec3 lhs, const T rhs)
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
      case 2:
        return z;
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
      case 2:
        return z;
      default:
        throw std::out_of_range("component_index");
    }
  }

  constexpr auto operator<=>(const TVec3&) const = default;
};

template<typename T> class std::formatter<TVec3<T>> {
public:
  constexpr auto parse(format_parse_context& ctx) { return ctx.begin(); }
  template<typename Context>
  constexpr auto format(const TVec3<T>& v, Context& ctx) const {
    return format_to(ctx.out(), "{}, {}, {}", v.x, v.y, v.z);
  }
};

template<typename T> struct std::hash<TVec3<T>> {
  constexpr std::size_t operator()(const TVec3<T>& v) const noexcept {
    auto h = std::hash<T>{}(v.x);
    h ^= std::hash<T>{}(v.y) + 0x9e3779b9 + (h << 6) + (h >> 2);
    h ^= std::hash<T>{}(v.z) + 0x9e3779b9 + (h << 6) + (h >> 2);

    return h;
  }
};

template<> inline constexpr TVec3<float> TVec3<float>::Zero{0.f, 0.f, 0.f};
template<> inline constexpr TVec3<double> TVec3<double>::Zero{0., 0., 0.};
template<> inline constexpr TVec3<int> TVec3<int>::Zero{0, 0, 0};

template<> inline constexpr TVec3<float> TVec3<float>::One{1.f, 1.f, 1.f};
template<> inline constexpr TVec3<double> TVec3<double>::One{1., 1., 1.};
template<> inline constexpr TVec3<int> TVec3<int>::One{1, 1, 1};

template<> inline constexpr TVec3<float> TVec3<float>::UnitX{1.f, 0.f, 0.f};
template<> inline constexpr TVec3<double> TVec3<double>::UnitX{1., 0., 0.};
template<> inline constexpr TVec3<int> TVec3<int>::UnitX{1, 0, 0};

template<> inline constexpr TVec3<float> TVec3<float>::UnitY{0.f, 1.f, 0.f};
template<> inline constexpr TVec3<double> TVec3<double>::UnitY{0., 1., 0.};
template<> inline constexpr TVec3<int> TVec3<int>::UnitY{0, 1, 0};

template<> inline constexpr TVec3<float> TVec3<float>::UnitZ{0.f, 0.f, 1.f};
template<> inline constexpr TVec3<double> TVec3<double>::UnitZ{0., 0.f, 1.};
template<> inline constexpr TVec3<int> TVec3<int>::UnitZ{0, 0, 1};

using FVec3 = TVec3<float>;
using IVec3 = TVec3<int>;
using Vec3 = FVec3;

//----------------------------------------------------------------------------//
// Utilities                                                                  //
//----------------------------------------------------------------------------//
template<typename T> inline constexpr TVec2<T> abs(const TVec2<T>& v) {
  return TVec2(std::abs(v.x), std::abs(v.y));
}

template<typename T> inline constexpr TVec3<T> abs(const TVec3<T>& v) {
  return TVec3(std::abs(v.x), std::abs(v.y), std::abs(v.z));
}

template<typename T>
inline constexpr T distance_squared(const TVec2<T>& a, const TVec2<T>& b) {
  return (b.x - a.x) * (b.x - a.x) + (b.y - a.y) * (b.y - a.y);
}

template<typename T>
inline constexpr T distance_squared(const TVec3<T>& a, const TVec3<T>& b) {
  return (b.x - a.x) * (b.x - a.x) + (b.y - a.y) * (b.y - a.y) +
         (b.z - a.z) * (b.z - a.z);
}

template<typename T, typename U = T>
inline constexpr U distance(const TVec2<T>& a, const TVec2<T>& b) {
  return static_cast<U>(std::sqrt(distance_squared(a, b)));
}

template<typename T, typename U = T>
inline constexpr U distance(const TVec3<T>& a, const TVec3<T>& b) {
  return static_cast<U>(std::sqrt(distance_squared(a, b)));
}
