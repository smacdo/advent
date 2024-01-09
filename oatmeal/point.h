#include "oatmeal.h"

/** 2d cartesian point with x and y components. */
typedef struct {
  PyObject_HEAD double x;
  double y;
} Point;

/** Python type definition for `Point`. */
extern PyTypeObject PointType;

/** __init__(self, x: num, y: num) */
int Point_init(Point* self, PyObject* args, PyObject* kwds);

/** clone(self) -> Point */
PyObject* Point_clone(Point* self, PyObject*);

/** repr(self) -> str */
PyObject* Point_repr(PyObject* self);

/** str(self) -> str */
PyObject* Point_str(PyObject* self);

/** len(self) -> int */
Py_ssize_t Point_len(PyObject* self);

/** __get__(self, index: int) -> num */
PyObject* Point_get(PyObject* self, PyObject* index);

/** __set__(self, index: int, value: num) */
int Point_set(PyObject* self, PyObject* index, PyObject* value);

/** __add__(self, left: Point, right: Point) -> Point */
PyObject* Point_add(PyObject* left, PyObject* right);

/** __sub__(left: Point, right: Point) -> Point */
PyObject* Point_sub(PyObject* left, PyObject* right);

/** __mul__(left: Point, right: num) -> Point */
PyObject* Point_mul(PyObject* left, PyObject* right);

/** __true_div__(left: Point, right: num) -> Point */
PyObject* Point_true_div(PyObject* left, PyObject* right);

/** __floor_div__(left: Point, right: num) -> Point */
PyObject* Point_floor_div(PyObject* left, PyObject* right);

/** __neg__(left: Point) -> Point */
PyObject* Point_negate(PyObject* left);

/** __abs__(left: Point) -> Point */
PyObject* Point_abs(PyObject* left);

PyObject* Point_compare(PyObject* self, PyObject* other, int op);
Py_hash_t Point_hash(PyObject* self);