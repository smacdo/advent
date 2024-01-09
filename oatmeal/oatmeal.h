#pragma once

#define PY_SSIZE_T_CLEAN

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
PyObject* inc(PyObject*, PyObject* value);