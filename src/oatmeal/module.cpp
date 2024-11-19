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
      .def(
          "__repr__",
          [](const Point& p) {
            return std::format("oatmeal.Point({}, {})", p.x, p.y);
          })
      .def(
          "__str__",
          [](const Point& p) { return std::format("{}, {}", p.x, p.y); })
      .def("__copy__", [](const Point& p) { return Point(p); })
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
      .def(
          "__repr__",
          [](const Vec2& v) {
            return std::format("oatmeal.Vec2({}, {})", v.x, v.y);
          })
      .def(
          "__str__",
          [](const Vec2& v) { return std::format("{}, {}", v.x, v.y); })
      .def("__copy__", [](const Vec2& v) { return Vec2(v); })
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

  py::class_<Grid<py::object>>(m, "Grid")
      .def(py::init<size_t, size_t, py::object>())
      .def(py::init<size_t, size_t, py::function>())
      .def(py::init([](size_t x_count, size_t y_count, py::list initial) {
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
      .def_property_readonly("x_count", &Grid<py::object>::x_count)
      .def_property_readonly("y_count", &Grid<py::object>::y_count)
      .def("col_count", &Grid<py::object>::col_count)
      .def("row_count", &Grid<py::object>::row_count)
      .def(
          "__getitem__",
          [](const Grid<py::object>& self, Point p) { return self[p]; })
      .def(
          "__setitem__",
          [](Grid<py::object>& self, Point p, py::object v) { self[p] = v; })
      .def("__len__", [](Grid<py::object>& self) { return self.count(); });
}