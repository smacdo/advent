#include "oatmeal.h"

//--------------------------------------------------------------------------------------------------
PyObject* inc(PyObject*, PyObject* value) {
  const double v = PyFloat_AsDouble(value);
  return PyFloat_FromDouble(v + 1.0);
}