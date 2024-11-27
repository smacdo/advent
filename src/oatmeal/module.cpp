#include "grid.h"
#include "point.h"
#include "vector.h"

#include <pybind11/operators.h>
#include <pybind11/pybind11.h>

#include <format>
#include <functional>

namespace py = pybind11;

PYBIND11_MODULE(_oatmeal, m) {
  m.doc() =
      "An assortment of boring but essential tools written in C++ for speed";

  py::class_<Grid<py::object>>(m, "Grid")
      .def(py::init([](size_t x_count, size_t y_count, py::function init) {
        return Grid<py::object>(
            x_count, y_count, [&init](auto x, auto y) { return init(x, y); });
      }))
      .def(py::init([](size_t x_count, size_t y_count, py::list initial) {
        // TODO: test!
        if (initial.size() != y_count) {
          throw py::value_error(
              "list row count must match grid y_count when constructing");
        }

        return Grid<py::object>(
            x_count, y_count, [initial, x_count](size_t x, size_t y) {
              const auto& row = py::cast<py::list>(initial[y]);

              if (row.size() != x_count) {
                throw py::value_error(
                    "list col count must match grid x_count when constructing");
              }

              const auto index = y * x_count + x;
              return row[x];
            });
      }))
      .def(py::init<size_t, size_t, py::object>())
      .def_property_readonly("x_count", &Grid<py::object>::x_count)
      .def_property_readonly("y_count", &Grid<py::object>::y_count)
      .def_property_readonly("col_count", &Grid<py::object>::col_count)
      .def_property_readonly("row_count", &Grid<py::object>::row_count)
      .def(
          "__getitem__",
          [](const Grid<py::object>& self, Point p) { return self[p]; })
      .def(
          "__setitem__",
          [](Grid<py::object>& self, Point p, py::object v) { self[p] = v; })
      .def(
          "__iter__",
          [](const Grid<py::object>& self) {
            return py::make_iterator(self.begin(), self.end());
          },
          py::keep_alive<0, 1>())
      .def("__len__", [](Grid<py::object>& self) { return self.count(); });

  py::class_<Point>(m, "Point")
      .def(py::init<int, int>())
      .def_property(
          "x",
          [](const Point& p) { return p.x; },
          [](Point& p, int newX) { p.x = newX; })
      .def_property(
          "y",
          [](const Point& p) { return p.y; },
          [](Point& p, int newY) { p.y = newY; })
      .def(py::pickle(
          [](const Point& p) { // __getstate__
            return py::make_tuple(p.x, p.y);
          },
          [](py::tuple t) { // __setstate__
            if (t.size() != 2) {
              throw std::runtime_error("invalid state");
            }

            return Point(t[0].cast<int>(), t[1].cast<int>());
          }))
      .def("clone", [](const Point& self) { return Point(self); })
      .def("__copy__", [](const Point& p) { return Point(p); })
      .def("__deepcopy__", [](const Point& p, py::dict) { return Point(p); })
      .def(
          "__repr__",
          [](const Point& p) {
            return std::format("oatmeal.Point({}, {})", p.x, p.y);
          })
      .def(
          "__str__",
          [](const Point& p) { return std::format("{}, {}", p.x, p.y); })
      .def("__hash__", [](const Point& p) { return std::hash<Point>{}(p); })
      .def("__getitem__", [](const Point& p, int i) { return p[i]; })
      .def("__setitem__", [](Point& p, int i, int v) { p[i] = v; })
      .def("__abs__", [](const Point& self) { return abs(self); })
      .def("__floordiv__", [](const Point& lhs, int rhs) { return lhs / rhs; })
      .def(py::self == py::self)
      .def(py::self != py::self)
      .def(py::self += py::self)
      .def(py::self + py::self)
      .def(py::self -= py::self)
      .def(py::self - py::self)
      .def(py::self * int())
      .def(py::self / int())
      .def(py::self % int())
      .def(-py::self);

  py::class_<Vec2>(m, "Vec2")
      .def(py::init<float, float>())
      .def_property(
          "x",
          [](const Vec2& v) { return v.x; },
          [](Vec2& v, int newX) { v.x = newX; })
      .def_property(
          "y",
          [](const Vec2& v) { return v.y; },
          [](Vec2& v, int newY) { v.y = newY; })
      .def(py::pickle(
          [](const Vec2& v) { // __getstate__
            return py::make_tuple(v.x, v.y);
          },
          [](py::tuple t) { // __setstate__
            if (t.size() != 2) {
              throw std::runtime_error("invalid state");
            }

            return Vec2(t[0].cast<float>(), t[1].cast<float>());
          }))
      .def(
          "dot",
          [](const Vec2& self, const Vec2& other) { return self.dot(other); })
      .def("length", [](const Vec2& self) { return self.length(); })
      .def("length_squared", [](const Vec2& self) { return self.length(); })
      .def("normalized", [](const Vec2& self) { return self.normalized(); })
      .def("clone", [](const Vec2& self) { return Vec2(self); })
      .def("__copy__", [](const Vec2& v) { return Vec2(v); })
      .def("__deepcopy__", [](const Vec2& v, py::dict) { return Vec2(v); })
      .def(
          "__repr__",
          [](const Vec2& v) {
            return std::format("oatmeal.Vec2({}, {})", v.x, v.y);
          })
      .def(
          "__str__",
          [](const Vec2& v) { return std::format("{}, {}", v.x, v.y); })
      .def("__hash__", [](const Vec2& v) { return std::hash<Vec2>{}(v); })
      .def("__getitem__", [](const Vec2& v, int i) { return v[i]; })
      .def("__setitem__", [](Vec2& v, int i, int val) { v[i] = val; })
      .def("__abs__", [](const Vec2& self) { return abs(self); })
      .def("__floordiv__", [](const Vec2& lhs, int rhs) { return lhs / rhs; })
      .def(py::self == py::self)
      .def(py::self != py::self)
      .def(py::self += py::self)
      .def(py::self + py::self)
      .def(py::self -= py::self)
      .def(py::self - py::self)
      .def(py::self * float())
      .def(py::self / float())
      .def(-py::self);

  py::class_<Vec3>(m, "Vec3")
      .def(py::init<float, float, float>())
      .def_property(
          "x",
          [](const Vec3& v) { return v.x; },
          [](Vec3& v, int newX) { v.x = newX; })
      .def_property(
          "y",
          [](const Vec3& v) { return v.y; },
          [](Vec3& v, int newY) { v.y = newY; })
      .def_property(
          "z",
          [](const Vec3& v) { return v.z; },
          [](Vec3& v, int newZ) { v.z = newZ; })
      .def(py::pickle(
          [](const Vec3& v) { // __getstate__
            return py::make_tuple(v.x, v.y, v.z);
          },
          [](py::tuple t) { // __setstate__
            if (t.size() != 3) {
              throw std::runtime_error("invalid state");
            }

            return Vec3(
                t[0].cast<float>(), t[1].cast<float>(), t[2].cast<float>());
          }))
      .def(
          "dot",
          [](const Vec3& self, const Vec3& other) { return self.dot(other); })
      .def(
          "cross",
          [](const Vec3& self, const Vec3& other) { return self.cross(other); })
      .def("length", [](const Vec3& self) { return self.length(); })
      .def("length_squared", [](const Vec3& self) { return self.length(); })
      .def("normalized", [](const Vec3& self) { return self.normalized(); })
      .def("clone", [](const Vec3& self) { return Vec3(self); })
      .def("__copy__", [](const Vec3& v) { return Vec3(v); })
      .def("__deepcopy__", [](const Vec3& v, py::dict) { return Vec3(v); })
      .def(
          "__repr__",
          [](const Vec3& v) {
            return std::format("oatmeal.Vec3({}, {}. {})", v.x, v.y, v.z);
          })
      .def(
          "__str__",
          [](const Vec3& v) {
            return std::format("{}, {}, {}", v.x, v.y, v.z);
          })
      .def("__hash__", [](const Vec3& v) { return std::hash<Vec3>{}(v); })
      .def("__getitem__", [](const Vec3& v, int i) { return v[i]; })
      .def("__setitem__", [](Vec3& v, int i, int val) { v[i] = val; })
      .def("__abs__", [](const Vec3& self) { return abs(self); })
      .def("__floordiv__", [](const Vec3& lhs, int rhs) { return lhs / rhs; })
      .def(py::self == py::self)
      .def(py::self != py::self)
      .def(py::self += py::self)
      .def(py::self + py::self)
      .def(py::self -= py::self)
      .def(py::self - py::self)
      .def(py::self * float())
      .def(py::self / float())
      .def(-py::self);

  m.def("distance_squared", [](const TVec2<float>& a, const TVec2<float>& b) {
    return distance_squared(a, b);
  });
  m.def("distance", [](const TVec2<float>& a, const TVec2<float>& b) {
    return distance(a, b);
  });
}