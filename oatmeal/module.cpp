#include "oatmeal.h"
#include "point.h"

//--------------------------------------------------------------------------------------------------
// Oatmeal module definition.
//--------------------------------------------------------------------------------------------------
static PyMethodDef oatmeal_methods[] = {{nullptr, nullptr, 0, nullptr}};

static PyModuleDef oatmeal_module = {
    PyModuleDef_HEAD_INIT,
    "oatmeal",
    "An assortment of boring but essential tools written in C++ for speed",
    0,
    oatmeal_methods};

//--------------------------------------------------------------------------------------------------
// Oatmeal module entry point.
//--------------------------------------------------------------------------------------------------
PyMODINIT_FUNC PyInit_oatmeal() {
  PyObject* mod = PyModule_Create(&oatmeal_module);

  if (mod == nullptr) {
    return nullptr;
  }

  if (PyType_Ready(&PointType) < 0) {
    return nullptr;
  }

  Py_INCREF(&PointType);

  if (PyModule_AddObject(mod, "Point", (PyObject*)&PointType) < 0) {
    Py_DECREF(&PointType);
    Py_DECREF(mod);
    return nullptr;
  }

  return mod;
}