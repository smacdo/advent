#include "oatmeal.h"

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