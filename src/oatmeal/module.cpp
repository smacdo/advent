#include "point.h"

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
}