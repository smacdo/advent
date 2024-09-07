#include <pybind11/pybind11.h>

#include "point.h"

namespace py = pybind11;

PYBIND11_MODULE(_oatmeal, m) {
  m.doc() =
      "An assortment of boring but essential tools written in C++ for speed";
  py::class_<Point>(m, "Point")
      .def(py::init<int, int>())
      .def("__repr__", [](const Point& p) { return "oatmeal.Point(...)"; });
}