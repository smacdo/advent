#pragma once

#include <concepts>
#include <format>
#include <functional>
#include <ostream>
#include <stdexcept>

//----------------------------------------------------------------------------//
// Vector2                                                                    //
//----------------------------------------------------------------------------//
/// @brief A 2d vector value containing X and Y components.
template<typename T> struct TVec2 {
  using value_type = T;
  using size_type = std::size_t;
  using reference = value_type&;
  using const_reference = const value_type&;
  using pointer = value_type*;
  using const_pointer = const value_type*;

  /// @brief The number of components in a 2d vector.
  static constexpr size_type kComponentCount = 2;

  /// @brief A vector with the X and Y coordinates set to zero.
  static const TVec2 Zero;

  /// @brief A vector with the X and Y coordinates set to one.
  static const TVec2 One;

  /// @brief A vector describing the positive X axis (X = 1 and Y = 0).
  static const TVec2 UnitX;

  /// @brief A vector describing the positive Y axis (X = 0 and Y = 1).
  static const TVec2 UnitY;

  /// @brief The X coordinate of this vector.
  value_type x;

  /// @brief The Y coordinate of this vector.
  value_type y;

  /// @brief Constructs a default vector with X and Y set to zero.
  constexpr TVec2() noexcept(std::is_nothrow_constructible_v<value_type>)
      : x(0),
        y(0) {}

  /// @brief Constructs a vector with X and Y from `x` and `y`.
  /// @param x The X value to set.
  /// @param y The Y value to set.
  constexpr TVec2(const value_type x, const value_type y) noexcept(
      std::is_nothrow_constructible_v<value_type>)
      : x(x),
        y(y) {}

  /// @brief Constructs a vector with X and Y copied from `other`.
  /// @param other The vector to copy from.
  constexpr TVec2(const TVec2& other) noexcept(
      std::is_nothrow_copy_constructible_v<value_type>) = default;

  /// @brief Returns the length of this vector.
  ///
  /// Callers of this method can change the precision of the length calculation
  /// by defining the template parameter `U` (e.g.
  /// `Vector2<int>::length<float>`).
  template<typename U = value_type> constexpr U length() const {
    return static_cast<U>(std::sqrt(length_squared()));
  }

  /// @brief Returns the squared length of this vector.
  ///
  /// Using the squared length is faster than `length` because this method
  /// avoids a square root call. This method can be used when callers need to
  /// compare magnitudes, but do not need to know direction or exact lengths.
  constexpr value_type length_squared() const { return x * x + y * y; }

  /// @brief Returns a dot product of this vector and `other`.
  constexpr value_type dot(const TVec2& other) const {
    return x * other.x + y * other.y;
  }

  /// @brief Returns a vector with values normalized from this vector.
  ///
  /// Normalizing a vector is to divide each component by the length of the
  /// vector. A zero vector will result in each component being set to `NaN`.
  ///
  /// See this Stack Overflow answer [1] on the uses of vector normalization.
  constexpr TVec2 normalized() const {
    const auto lsquared = length_squared();
    const auto one_over_lsquared = 1 / sqrt(lsquared);

    return TVec2(x * one_over_lsquared, y * one_over_lsquared);
  }

  /// @brief Print a human readable form of the vector to `os` for Google Tests.
  friend void PrintTo(const TVec2& v, std::ostream* os) {
    *os << "(" << v.x << ", " << v.y << ")";
  }

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

  constexpr TVec2& operator*=(const value_type rhs) {
    x *= rhs;
    y *= rhs;
    return *this;
  }

  constexpr friend TVec2 operator*(TVec2 lhs, const value_type rhs) {
    lhs *= rhs;
    return lhs;
  }

  constexpr TVec2& operator/=(const value_type rhs) {
    x /= rhs;
    y /= rhs;
    return *this;
  }

  constexpr friend TVec2 operator/(TVec2 lhs, const value_type rhs) {
    lhs /= rhs;
    return lhs;
  }

  constexpr TVec2& operator%=(const value_type rhs)
    requires std::integral<value_type>
  {
    x %= rhs;
    y %= rhs;
    return *this;
  }

  constexpr friend TVec2 operator%(TVec2 lhs, const value_type rhs)
    requires std::integral<value_type>
  {
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
/// @brief A 3d vector value containing X, Y and Z components.
template<typename T> struct TVec3 {
  using value_type = T;
  using size_type = std::size_t;
  using reference = value_type&;
  using const_reference = const value_type&;
  using pointer = value_type*;
  using const_pointer = const value_type*;

  /// @brief The number of components in a 3d point.
  static constexpr size_type kComponentCount = 3;

  /// @brief A vector with the X, Y and Z coordinates set to zero.
  static const TVec3 Zero;

  /// @brief A vector with the X and Y coordinates set to one.
  static const TVec3 One;

  /// @brief A vector describing the positive X axis (X = 1, Y = 0, and Z = 0).
  static const TVec3 UnitX;

  /// @brief A vector describing the positive X axis (X = 0, Y = 1, and Z = 0).
  static const TVec3 UnitY;

  /// @brief A vector describing the positive Z axis (X = 1, Y = 0, and Z = 1).
  static const TVec3 UnitZ;

  /// @brief The X coordinate of this vector.
  value_type x;

  /// @brief The Y coordinate of this vector.
  value_type y;

  /// @brief The Z coordinate of this vector.
  value_type z;

  /// @brief Constructs a default vector with X, Y and Z set to zero.
  constexpr TVec3() noexcept(std::is_nothrow_constructible_v<value_type>)
      : x(0),
        y(0),
        z(0) {}

  /// @brief Constructs a vector with X, Y and Z from `x`, `y` and `z`.
  /// @param x The X value to set.
  /// @param y The Y value to set.
  /// @param z The Z value to set.
  constexpr TVec3(
      const value_type x,
      const value_type y,
      const value_type z) noexcept(std::is_nothrow_constructible_v<value_type>)
      : x(x),
        y(y),
        z(z) {}

  /// @brief Constructs a vector with X, Y and Z copied from `other`.
  /// @param other The vector to copy from.
  constexpr TVec3(const TVec3& other) noexcept(
      std::is_nothrow_copy_constructible_v<value_type>) = default;

  /// @brief Returns the length of this vector.
  ///
  /// Callers of this method can change the precision of the length calculation
  /// by defining the template parameter `U` (e.g.
  /// `Vector3<int>::length<float>`).
  template<typename U = value_type> constexpr U length() const {
    return static_cast<U>(std::sqrt(length_squared()));
  }

  /// @brief Returns the squared length of this vector.
  ///
  /// Using the squared length is faster than `length` because this method
  /// avoids a square root call. This method can be used when callers need to
  /// compare magnitudes, but do not need to know direction or exact lengths.
  constexpr value_type length_squared() const { return x * x + y * y + z * z; }

  /// @brief Returns a dot product of this vector and `other`.
  constexpr value_type dot(const TVec3& other) const {
    return x * other.x + y * other.y + z * other.z;
  }

  /// @brief Returns the cross product of this vector and `other`.
  ///
  /// The cross product result is a vector that is perpendicular to the two
  /// vectors used in the cross product calculation.
  constexpr TVec3 cross(const TVec3& other) const {
    return TVec3(
        y * other.z - z * other.y,
        z * other.x - x * other.z,
        x * other.y - y * other.x);
  }

  /// @brief Returns a vector with values normalized from this vector.
  ///
  /// Normalizing a vector is to divide each component by the length of the
  /// vector. A zero vector will result in each component being set to `NaN`.
  ///
  /// See this Stack Overflow answer [1] on the uses of vector normalization.
  constexpr TVec3 normalized() const {
    const auto lsquared = length_squared();
    const auto one_over_lsquared = 1 / sqrt(lsquared);

    return TVec3(
        x * one_over_lsquared, y * one_over_lsquared, z * one_over_lsquared);
  }

  /// @brief Print a human readable form of the vector to `os` for Google Tests.
  friend void PrintTo(const TVec3& v, std::ostream* os) {
    *os << "(" << v.x << ", " << v.y << ", " << v.z << ")";
  }

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

  constexpr TVec3& operator*=(const value_type rhs) {
    x *= rhs;
    y *= rhs;
    z *= rhs;
    return *this;
  }

  constexpr friend TVec3 operator*(TVec3 lhs, const value_type rhs) {
    lhs *= rhs;
    return lhs;
  }

  constexpr TVec3& operator/=(const value_type rhs) {
    x /= rhs;
    y /= rhs;
    z /= rhs;
    return *this;
  }

  constexpr friend TVec3 operator/(TVec3 lhs, const value_type rhs) {
    lhs /= rhs;
    return lhs;
  }

  constexpr TVec3& operator%=(const value_type rhs)
    requires std::integral<value_type>
  {
    x %= rhs;
    y %= rhs;
    z %= rhs;
    return *this;
  }

  constexpr friend TVec3 operator%(TVec3 lhs, const value_type rhs)
    requires std::integral<value_type>
  {
    lhs %= rhs;
    return lhs;
  }

  constexpr reference operator[](const size_type component_index) {
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

  constexpr const_reference operator[](const size_type component_index) const {
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
/// @brief Returns a vector with each component set to the absolute value of the
/// matching component in `v`.
template<typename T> inline constexpr TVec2<T> abs(const TVec2<T>& v) {
  return TVec2(std::abs(v.x), std::abs(v.y));
}

/// @brief Returns a vector with each component set to the absolute value of the
/// matching component in `v`.
template<typename T> inline constexpr TVec3<T> abs(const TVec3<T>& v) {
  return TVec3(std::abs(v.x), std::abs(v.y), std::abs(v.z));
}

/// @brief Returns the squared euclidean distance between `a` and `b`.
template<typename T>
inline constexpr T distance_squared(const TVec2<T>& a, const TVec2<T>& b) {
  return (b.x - a.x) * (b.x - a.x) + (b.y - a.y) * (b.y - a.y);
}

/// @brief Returns the squared euclidean distance between `a` and `b`.
template<typename T>
inline constexpr T distance_squared(const TVec3<T>& a, const TVec3<T>& b) {
  return (b.x - a.x) * (b.x - a.x) + (b.y - a.y) * (b.y - a.y) +
         (b.z - a.z) * (b.z - a.z);
}

/// @brief Returns the euclidean distance between `a` and `b`.
template<typename T, typename U = T>
inline constexpr U distance(const TVec2<T>& a, const TVec2<T>& b) {
  return static_cast<U>(std::sqrt(distance_squared(a, b)));
}

/// @brief Returns the euclidean distance between `a` and `b`.
template<typename T, typename U = T>
inline constexpr U distance(const TVec3<T>& a, const TVec3<T>& b) {
  return static_cast<U>(std::sqrt(distance_squared(a, b)));
}
