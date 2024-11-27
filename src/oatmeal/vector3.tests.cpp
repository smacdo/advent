#include "vector.h"

#include <cmath>
#include <format>

#include <gtest/gtest.h>

// TODO: Finish disabled tests.

TEST(VectorTest3, Zero) { EXPECT_EQ(Vec3(0.0f, 0.0f, 0.0f), Vec3::Zero); }

TEST(VectorTest3, One) { EXPECT_EQ(Vec3(1.0f, 1.0f, 1.0f), Vec3::One); }

TEST(VectorTest3, UnitX) { EXPECT_EQ(Vec3(1.0f, 0.0f, 0.0f), Vec3::UnitX); }

TEST(VectorTest3, UnitY) { EXPECT_EQ(Vec3(0.0f, 1.0f, 0.0f), Vec3::UnitY); }

TEST(VectorTest3, UnitZ) { EXPECT_EQ(Vec3(0.0f, 0.0f, 1.0f), Vec3::UnitZ); }

TEST(VectorTest3, DefaultConstructorIsZero) {
  constexpr Vec3 p;

  EXPECT_EQ(p.x, 0);
  EXPECT_EQ(p.y, 0);
  EXPECT_EQ(p.z, 0);
}

TEST(VectorTest3, ConstructorSetsXY) {
  constexpr Vec3 p{5, -2, -14};

  EXPECT_EQ(p.x, 5);
  EXPECT_EQ(p.y, -2);
  EXPECT_EQ(p.z, -14);
}

TEST(VectorTest3, CopyConstructor) {
  constexpr Vec3 a(-8.2f, 15.1f, 0.2f);
  constexpr Vec3 b(a);

  EXPECT_EQ(a, b);
}

TEST(VectorTest3, VectorLength) {
  {
    // A simple vector length example.
    Vec3 simple(1, 2, 3);

    EXPECT_FLOAT_EQ(simple.length(), std::sqrt(14.0f));
    EXPECT_FLOAT_EQ(simple.length_squared(), 14.0f);
  }

  {
    // A zero vector has length zero.
    Vec3 zero(0, 0, 0);

    EXPECT_FLOAT_EQ(zero.length(), 0.0f);
    EXPECT_FLOAT_EQ(zero.length_squared(), 0.0f);
  }

  {
    // A unit vector has length one.
    Vec3 unit_x(1, 0, 0);

    EXPECT_FLOAT_EQ(unit_x.length(), 1.0f);
    EXPECT_FLOAT_EQ(unit_x.length_squared(), 1.0f);
  }

  {
    // A unit vector has length one.
    Vec3 unit_y(0, 1, 0);

    EXPECT_FLOAT_EQ(unit_y.length(), 1.0f);
    EXPECT_FLOAT_EQ(unit_y.length_squared(), 1.0f);
  }

  {
    // The length of a negative vector is positive.
    Vec3 negative(-1, -1, -1);

    EXPECT_FLOAT_EQ(negative.length(), std::sqrt(3.0f));
    EXPECT_FLOAT_EQ(negative.length_squared(), 3.0f);
  }

  {
    // The length of a vector with perfect squares works out to a round value.
    Vec3 scalar_multiple(1, 4, 8);

    EXPECT_FLOAT_EQ(scalar_multiple.length(), 9.0f);
    EXPECT_FLOAT_EQ(scalar_multiple.length_squared(), 81.0f);
  }

  {
    // Verify the length of a vector with very small values is correct.
    Vec3 small(1e-10, 1e-10, 1e-10);

    EXPECT_FLOAT_EQ(small.length(), sqrt(3e-20));
    EXPECT_FLOAT_EQ(small.length_squared(), 3e-20);
  }

  {
    // Verify the length of a vector with very large values is correct.
    Vec3 large(1e10, 1e10, 1e10);

    EXPECT_FLOAT_EQ(large.length(), std::sqrt(3e20));
    EXPECT_FLOAT_EQ(large.length_squared(), 3e20);
  }

  {
    // Verify the length of a vector with one value close to but not zero is
    // correct.
    Vec3 close_zero(1e-6, 0, 0);

    EXPECT_FLOAT_EQ(close_zero.length(), 1e-6);
    EXPECT_FLOAT_EQ(close_zero.length_squared(), 1e-12);
  }
}

TEST(VectorTest3, CrossProduct) {
  constexpr Vec3 a(1.f, 2.f, 3.f);
  constexpr Vec3 b(2.f, 3.f, 4.f);

  EXPECT_EQ(a.cross(b), Vec3(-1.f, 2.f, -1.f));
  EXPECT_EQ(b.cross(a), Vec3(1.f, -2.f, 1.f));
}

TEST(VectorTest3, Normalize) {
  {
    // Simple vector normalization example.
    const Vec3 v(3.f, 4.f, 5.f);
    const Vec3 normalized_v = v.normalized();

    EXPECT_FLOAT_EQ(normalized_v.x, 0.42426400f);
    EXPECT_FLOAT_EQ(normalized_v.y, 0.56568545f);
    EXPECT_FLOAT_EQ(normalized_v.z, 0.70710700f);
  }

  {
    // Normalize vector with negative components.
    const Vec3 v(-3.f, -4.f, -5.f);
    const Vec3 normalized_v = v.normalized();

    EXPECT_FLOAT_EQ(normalized_v.x, -0.42426400f);
    EXPECT_FLOAT_EQ(normalized_v.y, -0.56568545f);
    EXPECT_FLOAT_EQ(normalized_v.z, -0.70710700f);
  }

  {
    // Normalizing a zero vector results in an invalid vector.
    const Vec3 zero(0., 0., 0.);
    const Vec3 normalized_zero = zero.normalized();

    EXPECT_TRUE(std::isnan(normalized_zero.x));
    EXPECT_TRUE(std::isnan(normalized_zero.y));
    EXPECT_TRUE(std::isnan(normalized_zero.z));
  }

  {
    // Normalizing a unit vector returns the unit vector.
    const Vec3 v(0.f, 0.f, 1.f);
    const Vec3 normalized_v = v.normalized();

    EXPECT_EQ(normalized_v, Vec3(0.f, 0.f, 1.f));
  }

  {
    // Normalizing a unit vector should return the same vector.
    const Vec3 unit(0.424264f, 0.565685f, 0.707107f);
    const Vec3 normalized_unit = unit.normalized();

    EXPECT_FLOAT_EQ(normalized_unit.x, 0.424264f);
    EXPECT_FLOAT_EQ(normalized_unit.y, 0.565685f);
    EXPECT_FLOAT_EQ(normalized_unit.z, 0.707107f);
  }

  {
    // Normalizing a vector with small values.
    const Vec3 small(1e-10, 1e-10, 1e-10);
    const Vec3 normalized_small = small.normalized();

    EXPECT_FLOAT_EQ(normalized_small.x, 0.57735026f);
    EXPECT_FLOAT_EQ(normalized_small.y, 0.57735026f);
    EXPECT_FLOAT_EQ(normalized_small.z, 0.57735026f);
  }

  {
    // Normalizing a vector with large values.
    const Vec3 large(1e10, 1e10, 1e10);
    const Vec3 normalized_large = large.normalized();

    EXPECT_FLOAT_EQ(normalized_large.x, 0.57735026f);
    EXPECT_FLOAT_EQ(normalized_large.y, 0.57735026f);
    EXPECT_FLOAT_EQ(normalized_large.z, 0.57735026f);
  }
}

/*
TEST(VectorTest3, Equality) {
  {
    // A vector equals itself.
    EXPECT_TRUE(Vec3(5, -2, 11) == Vec3(5, -2, 11));
    EXPECT_TRUE(Vec3(5, -2, 11) == Vec3(4 + 1, 0 - 2, 9 + 2));

    EXPECT_FALSE(Vec3(5, -2, 11) != Vec3(5, -2, 11));
    EXPECT_FALSE(Vec3(5, -2, 11) != Vec3(4 + 1, 0 - 2, 9 + 2));
  }

  // The X, Y and Z components of a vector must match for it to be equal.
  {
    EXPECT_FALSE(Vec3(5, -2, 11) == Vec3(5, 0, 11));
    EXPECT_FALSE(Vec3(5, -2, 11) == Vec3(0, -2, 11));
    EXPECT_FALSE(Vec3(5, -2, 11) == Vec3(-2, 5, 11));
    EXPECT_FALSE(Vec3(5, -2, 11) == Vec3(5, 2));

    EXPECT_TRUE(Vec3(5, -2, 11) != Vec3(5, 0));
    EXPECT_TRUE(Vec3(5, -2, 11) != Vec3(0, -2));
    EXPECT_TRUE(Vec3(5, -2, 11) != Vec3(-2, 5));
    EXPECT_TRUE(Vec3(5, -2, 11) != Vec3(5, 2));
  }

  {
    // Equality is exact - there is no "almost equals" for the equality and
    // inequality operators.
    constexpr Vec3 small_a(1.0000001, 2.0000001);
    constexpr Vec3 small_b(1.0000002, 2.0000002);

    EXPECT_FALSE(small_a == small_b);
    EXPECT_TRUE(small_a != small_b);
  }

  {
    // constexpr vectors can be checked for equality.
    constexpr Vec3 ca(1, 3), cb(1, 2 + 1), cc(0, 0);
    EXPECT_TRUE(ca == cb);
    EXPECT_TRUE(ca != cc);
  }
}
*/

TEST(VectorTest3, Addition) {
  constexpr Vec3 a(3, 8, -6);
  constexpr Vec3 b(-5, 2, 3);
  constexpr Vec3 r = a + b;

  EXPECT_EQ(r, Vec3(-2, 10, -3));

  auto r1 = r;
  r1 += Vec3(1, -3, 2);

  EXPECT_EQ(r1, Vec3(-1, 7, -1));
}

TEST(VectorTest3, Subtraction) {
  constexpr Vec3 a(3, 8, -6);
  constexpr Vec3 b(-5, 2, 3);
  constexpr Vec3 r = a - b;

  EXPECT_EQ(r, Vec3(8, 6, -9));

  auto r1 = r;
  r1 -= Vec3(1, -3, 2);

  EXPECT_EQ(r1, Vec3(7, 9, -11));
}

TEST(VectorTest3, Multiplication) {
  constexpr Vec3 a(3, -8, 7);
  constexpr Vec3 r = a * 4;

  EXPECT_EQ(r, Vec3(12, -32, 28));

  auto r1 = r;
  r1 *= -2;

  EXPECT_EQ(r1, Vec3(-24, 64, -56));
}

TEST(VectorTest3, Division) {
  constexpr Vec3 a(-24, 64, 8);
  constexpr Vec3 r = a / -2;

  EXPECT_EQ(r, Vec3(12, -32, -4));

  auto r1 = r;
  r1 /= 4;

  EXPECT_EQ(r1, Vec3(3, -8, -1));
}

TEST(VectorTest3, Modulo) {
  constexpr TVec3<int> a(8, 10, 11);
  constexpr TVec3<int> r = a % 3;

  EXPECT_EQ(r, TVec3<int>(2, 1, 2));

  auto r1 = r;
  r1 %= 2;

  EXPECT_EQ(r1, TVec3<int>(0, 1, 0));
}

TEST(VectorTest3, GetComponent) {
  constexpr Vec3 a(8, 10, 15);

  constexpr auto x = a[0];
  EXPECT_EQ(x, 8);

  constexpr auto y = a[1];
  EXPECT_EQ(y, 10);

  constexpr auto z = a[2];
  EXPECT_EQ(z, 15);
}

TEST(VectorTest3, GetComponentThrowsIfIndexOutOfRange) {
  constexpr Vec3 a(8, 10, 15);
  EXPECT_THROW({ const auto bad = a[3]; }, std::out_of_range);
}

TEST(VectorTest3, SetComponent) {
  Vec3 a(0, 0, 0);
  a[0] = 3123;
  a[1] = -918;
  a[2] = 123;

  EXPECT_EQ(a[0], 3123);
  EXPECT_EQ(a[1], -918);
  EXPECT_EQ(a[2], 123);
}

TEST(VectorTest3, SetComponentThrowsIfIndexOutOfRange) {
  Vec3 a(8, 10, 15);
  EXPECT_THROW({ a[3] = 0; }, std::out_of_range);
}

TEST(VectorTest3, AbsoluteValue) {
  EXPECT_EQ(abs(Vec3(3, 6, 0)), Vec3(3, 6, 0));
  EXPECT_EQ(abs(Vec3(-4, 10, 2)), Vec3(4, 10, 2));
  EXPECT_EQ(abs(Vec3(12, -4, 8)), Vec3(12, 4, 8));
  EXPECT_EQ(abs(Vec3(5, 13, -17)), Vec3(5, 13, 17));
  EXPECT_EQ(abs(Vec3(-7, -123, -8)), Vec3(7, 123, 8));
}

TEST(VectorTest3, Format) {
  EXPECT_EQ(std::string("3, 2, -9"), std::format("{}", Vec3(3, 2, -9)));
}

/*
TEST(VectorTest3, Distance) {
  {
    // Simple demonstration of the distance between two vectors.
    Vec3 simple_a(1.f, 2.f);
    Vec3 simple_b(4.f, 6.f);

    EXPECT_FLOAT_EQ(distance_squared(simple_a, simple_b), 25.f);
    EXPECT_FLOAT_EQ(distance(simple_a, simple_b), 5.f);
  }

  {
    // Distance between two vectors where one vector has negative coordinates.
    Vec3 negative_a(-1.f, -2.f);
    Vec3 negative_b(3.f, 4.f);

    EXPECT_FLOAT_EQ(distance_squared(negative_a, negative_b), 52.f);
    EXPECT_FLOAT_EQ(distance(negative_a, negative_b), sqrt(52.f));
  }

  {
    // The distance between two identical vectors is zero.
    Vec3 same_a(15.f, -5.f);
    Vec3 same_b(15.f, -5.f);

    EXPECT_FLOAT_EQ(distance_squared(same_a, same_b), 0.f);
    EXPECT_FLOAT_EQ(distance(same_a, same_b), 0.f);
  }

  {
    // The distance between two zero vectors is zero.
    Vec3 zero_a(0.f, 0.f);
    Vec3 zero_b(0.f, 0.f);

    EXPECT_FLOAT_EQ(distance_squared(zero_a, zero_b), 0.f);
    EXPECT_FLOAT_EQ(distance(zero_a, zero_b), 0.f);
  }

  {
    // Distance between two vectors on the same x axis.
    Vec3 xaxis_a(2.f, 3.f);
    Vec3 xaxis_b(2.f, 6.f);

    EXPECT_FLOAT_EQ(distance_squared(xaxis_a, xaxis_b), 9.f);
    EXPECT_FLOAT_EQ(distance(xaxis_a, xaxis_b), 3.f);
  }

  {
    // Distance between two vectors on the same y axis.
    Vec3 yaxis_a(2.f, 3.f);
    Vec3 yaxis_b(5.f, 3.f);

    EXPECT_FLOAT_EQ(distance_squared(yaxis_a, yaxis_b), 9.f);
    EXPECT_FLOAT_EQ(distance(yaxis_a, yaxis_b), 3.f);
  }

  {
    // Distance between two vectors with large coordinates.
    Vec3 large_a(100000, 200000);
    Vec3 large_b(300000, 400000);

    EXPECT_FLOAT_EQ(distance_squared(large_a, large_b), 80000000000.f);
    EXPECT_FLOAT_EQ(distance(large_a, large_b), sqrt(80000000000.f));
  }

  {
    // Distance between two vectors with small coordinates.
    Vec3 small_a(1e-6f, 1e-6f);
    Vec3 small_b(2e-6f, 2e-6f);

    EXPECT_FLOAT_EQ(distance_squared(small_a, small_b), 2e-12f);
    EXPECT_FLOAT_EQ(distance(small_a, small_b), sqrt(2e-12f));
  }
}
*/