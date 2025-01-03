#include "vector.h"

#include <cmath>
#include <format>

#include <gtest/gtest.h>

TEST(VectorTest2, Zero) { EXPECT_EQ(Vec2(0.0f, 0.0f), Vec2::Zero); }

TEST(VectorTest2, One) { EXPECT_EQ(Vec2(1.0f, 1.0f), Vec2::One); }

TEST(VectorTest2, UnitX) { EXPECT_EQ(Vec2(1.0f, 0.0f), Vec2::UnitX); }

TEST(VectorTest2, UnitY) { EXPECT_EQ(Vec2(0.0f, 1.0f), Vec2::UnitY); }

TEST(VectorTest2, DefaultConstructorIsZero) {
  constexpr Vec2 p;

  EXPECT_EQ(p.x, 0);
  EXPECT_EQ(p.y, 0);
}

TEST(VectorTest2, ConstructorSetsXY) {
  constexpr Vec2 p{5, -2};

  EXPECT_EQ(p.x, 5);
  EXPECT_EQ(p.y, -2);
}

TEST(VectorTest2, CopyConstructor) {
  constexpr Vec2 a(8.2f, 15.1f);
  constexpr Vec2 b(a);

  EXPECT_EQ(a, b);
}

TEST(VectorTest2, VectorLength) {
  {
    // A simple vector length example.
    Vec2 simple(1, 1);

    EXPECT_FLOAT_EQ(simple.length(), std::sqrt(2.0f));
    EXPECT_FLOAT_EQ(simple.length_squared(), 2.0f);
  }

  {
    // A zero vector has length zero.
    Vec2 zero(0, 0);

    EXPECT_FLOAT_EQ(zero.length(), 0.0f);
    EXPECT_FLOAT_EQ(zero.length_squared(), 0.0f);
  }

  {
    // A unit vector has length one.
    Vec2 unit_x(1, 0);

    EXPECT_FLOAT_EQ(unit_x.length(), 1.0f);
    EXPECT_FLOAT_EQ(unit_x.length_squared(), 1.0f);
  }

  {
    // A unit vector has length one.
    Vec2 unit_y(0, 1);

    EXPECT_FLOAT_EQ(unit_y.length(), 1.0f);
    EXPECT_FLOAT_EQ(unit_y.length_squared(), 1.0f);
  }

  {
    // The length of a negative vector is positive.
    Vec2 negative(-1, -1);

    EXPECT_FLOAT_EQ(negative.length(), std::sqrt(2.0f));
    EXPECT_FLOAT_EQ(negative.length_squared(), 2.0f);
  }

  {
    // The length of a vector with perfect squares works out to a round value.
    Vec2 scalar_multiple(3, 4);

    EXPECT_FLOAT_EQ(scalar_multiple.length(), 5.0f);
    EXPECT_FLOAT_EQ(scalar_multiple.length_squared(), 25.0f);
  }

  {
    // Verify the length of a vector with very small values is correct.
    Vec2 small(1e-10, 1e-10);

    EXPECT_FLOAT_EQ(small.length(), sqrt(2e-20));
    EXPECT_FLOAT_EQ(small.length_squared(), 2e-20);
  }

  {
    // Verify the length of a vector with very large values is correct.
    Vec2 large(1e10, 1e10);

    EXPECT_FLOAT_EQ(large.length(), std::sqrt(2e20));
    EXPECT_FLOAT_EQ(large.length_squared(), 2e20);
  }

  {
    // Verify the length of a vector with one value close to but not zero is
    // correct.
    Vec2 close_zero(1e-6, 0);

    EXPECT_FLOAT_EQ(close_zero.length(), 1e-6);
    EXPECT_FLOAT_EQ(close_zero.length_squared(), 1e-12);
  }
}

TEST(VectorTest2, Dot) {
  {
    // Simple dot product demonstration.
    Vec2 vec_a(3.f, 4.f);
    Vec2 vec_b(6.f, 8.f);

    EXPECT_FLOAT_EQ(vec_a.dot(vec_b), 50.f);
    EXPECT_FLOAT_EQ(vec_b.dot(vec_a), 50.f);
  }

  {
    // Dot product of a zero vector is always zero.
    Vec2 zero_a(0.f, 0.f);
    Vec2 zero_b(3.f, 4.f);

    EXPECT_FLOAT_EQ(zero_a.dot(zero_b), 0.f);
    EXPECT_FLOAT_EQ(zero_b.dot(zero_a), 0.f);
  }

  {
    // Dot product of self is x**2 + y**2.
    Vec2 same(3.f, 4.f);
    EXPECT_FLOAT_EQ(same.dot(same), 25.f);
  }

  {
    // Dot product of perpendicular vectors is always zero.
    Vec2 perpendicular_a(1.f, 0.f);
    Vec2 perpendicular_b(0.f, 1.f);

    EXPECT_FLOAT_EQ(perpendicular_a.dot(perpendicular_b), 0.f);
    EXPECT_FLOAT_EQ(perpendicular_b.dot(perpendicular_a), 0.f);
  }

  {
    // Dot product of opposite vectors is always negative.
    Vec2 opposite_a(1.f, 0.f);
    Vec2 opposite_b(-1.f, 0.f);

    EXPECT_FLOAT_EQ(opposite_a.dot(opposite_b), -1.f);
    EXPECT_FLOAT_EQ(opposite_b.dot(opposite_a), -1.f);
  }

  {
    // Dot product of parallel vectors is the product of their magnitudes.
    Vec2 parallel_a(1.f, 2.f);
    Vec2 parallel_b(2.f, 4.f);

    EXPECT_FLOAT_EQ(parallel_a.dot(parallel_b), 10.f);
    EXPECT_FLOAT_EQ(parallel_b.dot(parallel_a), 10.f);
  }

  {
    // Dot product with negative components.
    Vec2 negative_a(-1.f, -2.f);
    Vec2 negative_b(2.f, 1.f);

    EXPECT_FLOAT_EQ(negative_a.dot(negative_b), -4.f);
    EXPECT_FLOAT_EQ(negative_b.dot(negative_a), -4.f);
  }

  {
    // Dot product with large numbers.
    Vec2 large_a(1e6, 1e6);
    Vec2 large_b(1e6, 1e6);

    EXPECT_FLOAT_EQ(large_a.dot(large_b), 2e12f);
    EXPECT_FLOAT_EQ(large_b.dot(large_a), 2e12f);
  }

  {
    // Dot product with small numbers.
    Vec2 small_a(1e-6, 1e-6);
    Vec2 small_b(1e-6, 1e-6);

    EXPECT_FLOAT_EQ(small_a.dot(small_b), 2e-12f);
    EXPECT_FLOAT_EQ(small_b.dot(small_a), 2e-12f);
  }
}

TEST(VectorTest2, Normalize) {
  {
    // Simple vector normalization example.
    const Vec2 v(3.f, 4.f);
    const Vec2 normalized_v = v.normalized();

    EXPECT_FLOAT_EQ(normalized_v.x, 0.6f);
    EXPECT_FLOAT_EQ(normalized_v.y, 0.8f);
  }

  {
    // Normalize vector with negative components.
    const Vec2 v(-3.f, -4.f);
    const Vec2 normalized_v = v.normalized();

    EXPECT_FLOAT_EQ(normalized_v.x, -0.6f);
    EXPECT_FLOAT_EQ(normalized_v.y, -0.8f);
  }

  {
    // Normalizing a zero vector results in an invalid vector.
    const Vec2 zero(0., 0.);
    const Vec2 normalized_zero = zero.normalized();

    EXPECT_TRUE(std::isnan(normalized_zero.x));
    EXPECT_TRUE(std::isnan(normalized_zero.y));
  }

  {
    // Normalizing a unit vector returns the unit vector.
    const Vec2 v(1.f, 0.f);
    const Vec2 normalized_v = v.normalized();

    EXPECT_EQ(normalized_v, Vec2(1.f, 0.f));
  }

  {
    // Normalizing a unit vector should return the same vector.
    const Vec2 unit(0.6f, 0.8f);
    const Vec2 normalized_unit = unit.normalized();

    EXPECT_FLOAT_EQ(normalized_unit.x, 0.6f);
    EXPECT_FLOAT_EQ(normalized_unit.y, 0.8f);
  }

  {
    // Normalizing a vector with small values.
    const Vec2 small(1e-10, 1e-10);
    const Vec2 normalized_small = small.normalized();

    EXPECT_FLOAT_EQ(normalized_small.x, 0.70710675797957379);
    EXPECT_FLOAT_EQ(normalized_small.y, 0.70710675797957379);
  }

  {
    // Normalizing a vector with large values.
    const Vec2 large(1e10, 1e10);
    const Vec2 normalized_large = large.normalized();

    EXPECT_FLOAT_EQ(normalized_large.x, 0.70710675797957379);
    EXPECT_FLOAT_EQ(normalized_large.y, 0.70710675797957379);
  }
}

TEST(VectorTest2, Equality) {
  {
    // A vector equals itself.
    EXPECT_TRUE(Vec2(5, -2) == Vec2(5, -2));
    EXPECT_TRUE(Vec2(5, -2) == Vec2(4 + 1, 0 - 2));

    EXPECT_FALSE(Vec2(5, -2) != Vec2(5, -2));
    EXPECT_FALSE(Vec2(5, -2) != Vec2(4 + 1, 0 - 2));
  }

  // The X and Y components of a vector must match for it to be equal.
  {
    EXPECT_FALSE(Vec2(5, -2) == Vec2(5, 0));
    EXPECT_FALSE(Vec2(5, -2) == Vec2(0, -2));
    EXPECT_FALSE(Vec2(5, -2) == Vec2(-2, 5));
    EXPECT_FALSE(Vec2(5, -2) == Vec2(5, 2));

    EXPECT_TRUE(Vec2(5, -2) != Vec2(5, 0));
    EXPECT_TRUE(Vec2(5, -2) != Vec2(0, -2));
    EXPECT_TRUE(Vec2(5, -2) != Vec2(-2, 5));
    EXPECT_TRUE(Vec2(5, -2) != Vec2(5, 2));
  }

  {
    // Equality is exact - there is no "almost equals" for the equality and
    // inequality operators.
    constexpr Vec2 small_a(1.0000001, 2.0000001);
    constexpr Vec2 small_b(1.0000002, 2.0000002);

    EXPECT_FALSE(small_a == small_b);
    EXPECT_TRUE(small_a != small_b);
  }

  {
    // constexpr vectors can be checked for equality.
    constexpr Vec2 ca(1, 3), cb(1, 2 + 1), cc(0, 0);
    EXPECT_TRUE(ca == cb);
    EXPECT_TRUE(ca != cc);
  }
}

TEST(VectorTest2, Addition) {
  constexpr Vec2 a(3, 8);
  constexpr Vec2 b(-5, 2);
  constexpr Vec2 r = a + b;

  EXPECT_EQ(r, Vec2(-2, 10));

  auto r1 = r;
  r1 += Vec2(1, -3);

  EXPECT_EQ(r1, Vec2(-1, 7));
}

TEST(VectorTest2, Subtraction) {
  constexpr Vec2 a(3, 8);
  constexpr Vec2 b(-5, 2);
  constexpr Vec2 r = a - b;

  EXPECT_EQ(r, Vec2(8, 6));

  auto r1 = r;
  r1 -= Vec2(1, -3);

  EXPECT_EQ(r1, Vec2(7, 9));
}

TEST(VectorTest2, Multiplication) {
  constexpr Vec2 a(3, -8);
  constexpr Vec2 r = a * 4;

  EXPECT_EQ(r, Vec2(12, -32));

  auto r1 = r;
  r1 *= -2;

  EXPECT_EQ(r1, Vec2(-24, 64));
}

TEST(VectorTest2, Division) {
  constexpr Vec2 a(-24, 64);
  constexpr Vec2 r = a / -2;

  EXPECT_EQ(r, Vec2(12, -32));

  auto r1 = r;
  r1 /= 4;

  EXPECT_EQ(r1, Vec2(3, -8));
}

TEST(VectorTest2, Modulo) {
  constexpr TVec2<int> a(8, 10);
  constexpr TVec2<int> r = a % 3;

  EXPECT_EQ(r, TVec2<int>(2, 1));

  auto r1 = r;
  r1 %= 2;

  EXPECT_EQ(r1, TVec2<int>(0, 1));
}

TEST(VectorTest2, GetComponent) {
  constexpr Vec2 a(8, 10);

  constexpr auto x = a[0];
  EXPECT_EQ(x, 8);

  constexpr auto y = a[1];
  EXPECT_EQ(y, 10);
}

TEST(VectorTest2, GetComponentThrowsIfIndexOutOfRange) {
  constexpr Vec2 a(8, 10);
  EXPECT_THROW({ const auto bad = a[2]; }, std::out_of_range);
}

TEST(VectorTest2, SetComponent) {
  Vec2 a(0, 0);
  a[0] = 3123;
  a[1] = -918;

  EXPECT_EQ(a[0], 3123);
  EXPECT_EQ(a[1], -918);
}

TEST(VectorTest2, SetComponentThrowsIfIndexOutOfRange) {
  Vec2 a(8, 10);
  EXPECT_THROW({ a[2] = 0; }, std::out_of_range);
}

TEST(VectorTest2, AbsoluteValue) {
  EXPECT_EQ(abs(Vec2(3, 6)), Vec2(3, 6));
  EXPECT_EQ(abs(Vec2(-4, 10)), Vec2(4, 10));
  EXPECT_EQ(abs(Vec2(12, -4)), Vec2(12, 4));
  EXPECT_EQ(abs(Vec2(-7, -123)), Vec2(7, 123));
}

TEST(VectorTest2, Format) {
  EXPECT_EQ(std::string("3, 2"), std::format("{}", Vec2(3, 2)));
}

TEST(VectorTest2, Distance) {
  {
    // Simple demonstration of the distance between two vectors.
    Vec2 simple_a(1.f, 2.f);
    Vec2 simple_b(4.f, 6.f);

    EXPECT_FLOAT_EQ(distance_squared(simple_a, simple_b), 25.f);
    EXPECT_FLOAT_EQ(distance(simple_a, simple_b), 5.f);
  }

  {
    // Distance between two vectors where one vector has negative coordinates.
    Vec2 negative_a(-1.f, -2.f);
    Vec2 negative_b(3.f, 4.f);

    EXPECT_FLOAT_EQ(distance_squared(negative_a, negative_b), 52.f);
    EXPECT_FLOAT_EQ(distance(negative_a, negative_b), sqrt(52.f));
  }

  {
    // The distance between two identical vectors is zero.
    Vec2 same_a(15.f, -5.f);
    Vec2 same_b(15.f, -5.f);

    EXPECT_FLOAT_EQ(distance_squared(same_a, same_b), 0.f);
    EXPECT_FLOAT_EQ(distance(same_a, same_b), 0.f);
  }

  {
    // The distance between two zero vectors is zero.
    Vec2 zero_a(0.f, 0.f);
    Vec2 zero_b(0.f, 0.f);

    EXPECT_FLOAT_EQ(distance_squared(zero_a, zero_b), 0.f);
    EXPECT_FLOAT_EQ(distance(zero_a, zero_b), 0.f);
  }

  {
    // Distance between two vectors on the same x axis.
    Vec2 xaxis_a(2.f, 3.f);
    Vec2 xaxis_b(2.f, 6.f);

    EXPECT_FLOAT_EQ(distance_squared(xaxis_a, xaxis_b), 9.f);
    EXPECT_FLOAT_EQ(distance(xaxis_a, xaxis_b), 3.f);
  }

  {
    // Distance between two vectors on the same y axis.
    Vec2 yaxis_a(2.f, 3.f);
    Vec2 yaxis_b(5.f, 3.f);

    EXPECT_FLOAT_EQ(distance_squared(yaxis_a, yaxis_b), 9.f);
    EXPECT_FLOAT_EQ(distance(yaxis_a, yaxis_b), 3.f);
  }

  {
    // Distance between two vectors with large coordinates.
    Vec2 large_a(100000, 200000);
    Vec2 large_b(300000, 400000);

    EXPECT_FLOAT_EQ(distance_squared(large_a, large_b), 80000000000.f);
    EXPECT_FLOAT_EQ(distance(large_a, large_b), sqrt(80000000000.f));
  }

  {
    // Distance between two vectors with small coordinates.
    Vec2 small_a(1e-6f, 1e-6f);
    Vec2 small_b(2e-6f, 2e-6f);

    EXPECT_FLOAT_EQ(distance_squared(small_a, small_b), 2e-12f);
    EXPECT_FLOAT_EQ(distance(small_a, small_b), sqrt(2e-12f));
  }
}
