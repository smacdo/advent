#include "point.h"

#include <cmath>
#include <functional>

#include <structmember.h>

// TODO: Rewrite other methods to follow compare example.

namespace {
  /** Create a new Point PyObject and initialize to the given x and y. */
  PyObject* create_point(double x, double y) {
    PyObject* init_args = Py_BuildValue("dd", x, y);
    PyObject* point_obj = PyObject_CallObject((PyObject*)&PointType, init_args);
    Py_DECREF(init_args);

    return point_obj;
  }
} // namespace

//--------------------------------------------------------------------------------------------------
// Point python type definition.
//--------------------------------------------------------------------------------------------------
PyMemberDef Point_Members[] = {
    {"x", T_DOUBLE, offsetof(Point, x), 0, "x component"},
    {"y", T_DOUBLE, offsetof(Point, y), 0, "y component"},
    {nullptr}};

PyMappingMethods Point_MappingMethods = {
    .mp_length = Point_len,
    .mp_subscript = Point_get,
    .mp_ass_subscript = Point_set,
};

PyNumberMethods Point_NumberMethods = {
    .nb_add = Point_add,
    .nb_subtract = Point_sub,
    .nb_multiply = Point_mul,
    .nb_true_divide = Point_true_div,
    .nb_floor_divide = Point_floor_div,
    .nb_negative = Point_negate,
    .nb_absolute = Point_abs,
};

PyMethodDef Point_Methods[] = {
    {"clone",
     (PyCFunction)Point_clone,
     METH_NOARGS,
     "Return a copy of the point"},
    {nullptr}};

PyTypeObject PointType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = "oatmeal.Point",
    .tp_doc = PyDoc_STR("2d point"),
    .tp_basicsize = sizeof(Point),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)Point_init,
    .tp_members = Point_Members,
    .tp_methods = Point_Methods,
    .tp_repr = Point_repr,
    .tp_str = Point_str,
    .tp_as_mapping = &Point_MappingMethods,
    .tp_as_number = &Point_NumberMethods,
    .tp_richcompare = &Point_compare,
    .tp_hash = &Point_hash,
};

//--------------------------------------------------------------------------------------------------
// Point method definitions.
//--------------------------------------------------------------------------------------------------
int Point_init(Point* self, PyObject* args, PyObject* kwds) {
  self->x = 0.0;
  self->y = 0.0;

  static char* kwlist[] = {"x", "y", nullptr};

  if (!PyArg_ParseTupleAndKeywords(
          args, kwds, "|dd", kwlist, &self->x, &self->y)) {
    return -1;
  }
  return 0;
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_clone(Point* self, PyObject*) {
  return create_point(self->x, self->y);
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_repr(PyObject* obj_self) {
  const auto* self = reinterpret_cast<Point*>(obj_self);

  char* x_str = PyOS_double_to_string(self->x, 'r', 0, 0, nullptr);
  char* y_str = PyOS_double_to_string(self->y, 'r', 0, 0, nullptr);

  auto repr_str_obj = PyUnicode_FromFormat("Point(x=%s, y=%s)", x_str, y_str);

  PyMem_Free(x_str);
  PyMem_Free(y_str);

  return repr_str_obj;
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_str(PyObject* obj_self) {
  const auto* self = reinterpret_cast<Point*>(obj_self);

  char* x_str = PyOS_double_to_string(self->x, 'r', 0, 0, nullptr);
  char* y_str = PyOS_double_to_string(self->y, 'r', 0, 0, nullptr);

  auto str_obj = PyUnicode_FromFormat("%s, %s", x_str, y_str);

  PyMem_Free(x_str);
  PyMem_Free(y_str);

  return str_obj;
}

//--------------------------------------------------------------------------------------------------
Py_ssize_t Point_len(PyObject* self) { return 2; }

//--------------------------------------------------------------------------------------------------
PyObject* Point_get(PyObject* obj_self, PyObject* obj_index) {
  const auto* self = reinterpret_cast<Point*>(obj_self);
  const auto index = PyLong_AsLong(obj_index);

  switch (index) {
    case 0:
      return PyFloat_FromDouble(self->x);
    case 1:
      return PyFloat_FromDouble(self->y);
    default:
      PyErr_Format(PyExc_RuntimeError, "bad point index: %d", index);
      return nullptr;
  }
}

//--------------------------------------------------------------------------------------------------
int Point_set(PyObject* obj_self, PyObject* obj_index, PyObject* obj_value) {
  auto* self = reinterpret_cast<Point*>(obj_self);
  const auto index = PyLong_AsLong(obj_index);
  const auto value = PyFloat_AsDouble(obj_value);

  if (value == -1.0 && PyErr_Occurred() != nullptr) {
    return -1;
  }

  switch (index) {
    case 0:
      self->x = value;
      return 0;
    case 1:
      self->y = value;
      return 0;
    default:
      PyErr_Format(PyExc_RuntimeError, "bad point index: %d", index);
      return -1;
  }
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_add(PyObject* obj_left, PyObject* obj_right) {
  if (PyObject_TypeCheck(obj_left, &PointType) == 0 ||
      PyObject_TypeCheck(obj_right, &PointType) == 0) {
    return Py_NotImplemented;
  }

  const auto* left = reinterpret_cast<Point*>(obj_left);
  const auto* right = reinterpret_cast<Point*>(obj_right);

  return create_point(left->x + right->x, left->y + right->y);
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_sub(PyObject* obj_left, PyObject* obj_right) {
  if (PyObject_TypeCheck(obj_left, &PointType) == 0 ||
      PyObject_TypeCheck(obj_right, &PointType) == 0) {
    return Py_NotImplemented;
  }

  const auto* left = reinterpret_cast<Point*>(obj_left);
  const auto* right = reinterpret_cast<Point*>(obj_right);

  return create_point(left->x - right->x, left->y - right->y);
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_mul(PyObject* obj_left, PyObject* obj_right) {
  if (PyObject_TypeCheck(obj_left, &PointType) == 0 ||
      PyFloat_Check(obj_right)) {
    return Py_NotImplemented;
  }

  const auto* left = reinterpret_cast<Point*>(obj_left);
  const auto right = PyFloat_AsDouble(obj_right);

  return create_point(left->x * right, left->y * right);
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_true_div(PyObject* obj_left, PyObject* obj_right) {
  if (PyObject_TypeCheck(obj_left, &PointType) == 0 ||
      PyFloat_Check(obj_right)) {
    return Py_NotImplemented;
  }

  const auto* left = reinterpret_cast<Point*>(obj_left);
  const auto right = PyFloat_AsDouble(obj_right);

  return create_point(left->x / right, left->y / right);
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_floor_div(PyObject* obj_left, PyObject* obj_right) {
  if (PyObject_TypeCheck(obj_left, &PointType) == 0 ||
      PyFloat_Check(obj_right)) {
    return Py_NotImplemented;
  }

  const auto* left = reinterpret_cast<Point*>(obj_left);
  const auto right = PyFloat_AsDouble(obj_right);

  return create_point(
      static_cast<double>(std::floor(left->x / right)),
      static_cast<double>(std::floor(left->y / right)));
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_negate(PyObject* obj_left) {
  if (PyObject_TypeCheck(obj_left, &PointType) == 0) {
    return Py_NotImplemented;
  }

  const auto* left = reinterpret_cast<Point*>(obj_left);

  return create_point(-left->x, -left->y);
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_abs(PyObject* obj_left) {
  if (PyObject_TypeCheck(obj_left, &PointType) == 0) {
    return Py_NotImplemented;
  }

  const auto* left = reinterpret_cast<Point*>(obj_left);

  return create_point(std::abs(left->x), std::abs(left->y));
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_compare(PyObject* obj_self, PyObject* obj_other, int op) {
  auto result = Py_NotImplemented;

  if (PyObject_TypeCheck(obj_self, &PointType) != 0 &&
      PyObject_TypeCheck(obj_other, &PointType) != 0) {
    const auto* self = reinterpret_cast<Point*>(obj_self);
    const auto* other = reinterpret_cast<Point*>(obj_other);

    switch (op) {
      case Py_EQ:
        result =
            (self->x == other->x && self->y == other->y ? Py_True : Py_False);
        break;
      case Py_NE:
        result =
            (self->x != other->x || self->y != other->y ? Py_True : Py_False);
        break;
      default:
        break;
    }
  }

  Py_INCREF(result);
  return result;
}

//--------------------------------------------------------------------------------------------------
Py_hash_t Point_hash(PyObject* obj_self) {
  const auto* self = reinterpret_cast<Point*>(obj_self);
  const auto h1 = std::hash<double>{}(self->x);
  const auto h2 = std::hash<double>{}(self->y);
  return h1 ^ (h2 << 1);
}
