// TODO: Add C++ linting and formatting.
// TODO: Test Mac, Linux if this works.

// Visual Studio does not provide the ability to run against `python_d` forcing
// us to remove the _DEBUG macro define. Failure to do this results in a
// "Exception - GIL not held" error when the oatmeal module is imported.
#if defined(_MSC_VER) && defined(_DEBUG)
#undef _DEBUG
#include <Python.h>
#define _DEBUG 1
#else
#include <Python.h>
#endif

/// A simple test function to explore exporting a C++ function to Python.
PyObject* inc(PyObject*, PyObject* value) {
  const double v = PyFloat_AsDouble(value);
  return PyFloat_FromDouble(v + 1.0);
}

static PyMethodDef oatmeal_methods[] = {
    {"inc", (PyCFunction)inc, METH_O, nullptr},
    {nullptr, nullptr, 0, nullptr}};

static PyModuleDef oatmeal_module = {
    PyModuleDef_HEAD_INIT,
    "oatmeal",
    "An assortment of boring but essential tools written in C++ for speed",
    0,
    oatmeal_methods};

PyMODINIT_FUNC PyInit_oatmeal() { return PyModule_Create(&oatmeal_module); }