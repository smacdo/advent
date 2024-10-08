#include "point.h"

/*
#include <cmath>
#include <functional>

#include <structmember.h>

namespace {
  /// Create a new Point PyObject and initialize to the given x and y.
  PyObject* create_point(long x, long y) {
    PyObject* init_args = Py_BuildValue("ll", x, y);
    PyObject* point_obj = PyObject_CallObject((PyObject*)&PointType, init_args);
    Py_DECREF(init_args);

    return point_obj;
  }

  /// Cast a Python object to a long, and return true if the cast succeeded.
  bool from_pyobj(PyObject* long_obj, long* out) {
    if (!PyLong_Check(long_obj)) {
      return false;
    } else {
      if (out != nullptr) {
        *out = PyLong_AsLong(long_obj);
      }

      return true;
    }
  }
} // namespace

//--------------------------------------------------------------------------------------------------
// Point python type definition.
//--------------------------------------------------------------------------------------------------
PyMemberDef Point_Members[] = {
    {"x", T_LONG, offsetof(Point, x), 0, "x component"},
    {"y", T_LONG, offsetof(Point, y), 0, "y component"},
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
    .nb_remainder = Point_mod,
    .nb_negative = Point_negate,
    .nb_absolute = Point_abs,
};

PyMethodDef Point_Methods[] = {
    {"clone",
     (PyCFunction)Point_clone,
     METH_NOARGS,
     "Return a copy of the point"},
    {"__getstate__",
     (PyCFunction)Point_getstate,
     METH_NOARGS,
     "pickle the point object"},
    {"__setstate__",
     (PyCFunction)Point_setstate,
     METH_O,
     "un-pickle the point object"},
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

  char* kwlist[] = {"x", "y", nullptr};

  if (!PyArg_ParseTupleAndKeywords(
          args, kwds, "|ll", kwlist, &self->x, &self->y)) {
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
  return PyUnicode_FromFormat("Point(x=%d, y=%d)", self->x, self->y);
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_str(PyObject* obj_self) {
  const auto* self = reinterpret_cast<Point*>(obj_self);
  return PyUnicode_FromFormat("%d, %d", self->x, self->y);
}

//--------------------------------------------------------------------------------------------------
Py_ssize_t Point_len(PyObject* self) { return 2; }

//--------------------------------------------------------------------------------------------------
PyObject* Point_get(PyObject* obj_self, PyObject* obj_index) {
  const auto* self = reinterpret_cast<Point*>(obj_self);
  auto index = PyLong_AsLong(obj_index);

  if (!from_pyobj(obj_index, &index)) {
    PyErr_Format(
        PyExc_ValueError, "point component index must be an int", index);
    return nullptr;
  }

  switch (index) {
    case 0:
      return PyLong_FromLong(self->x);
    case 1:
      return PyLong_FromLong(self->y);
    default:
      PyErr_Format(PyExc_ValueError, "point index out of range: %d", index);
      return nullptr;
  }
}

//--------------------------------------------------------------------------------------------------
int Point_set(PyObject* obj_self, PyObject* obj_index, PyObject* obj_value) {
  auto* self = reinterpret_cast<Point*>(obj_self);
  auto index = 0L;

  if (!from_pyobj(obj_index, &index)) {
    PyErr_Format(
        PyExc_ValueError, "point component index must be an int", index);
    return -1;
  }

  auto new_value = 0L;

  if (!from_pyobj(obj_value, &new_value)) {
    PyErr_Format(
        PyExc_ValueError, "point component value must be an int", index);
    return -1;
  }

  switch (index) {
    case 0:
      self->x = new_value;
      return 0;
    case 1:
      self->y = new_value;
      return 0;
    default:
      PyErr_Format(PyExc_ValueError, "point index out of range: %d", index);
      return -1;
  }
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_add(PyObject* obj_left, PyObject* obj_right) {
  if (PyObject_TypeCheck(obj_left, &PointType) != 0 &&
      PyObject_TypeCheck(obj_right, &PointType) != 0) {
    const auto* left = reinterpret_cast<Point*>(obj_left);
    const auto* right = reinterpret_cast<Point*>(obj_right);

    return create_point(left->x + right->x, left->y + right->y);
  } else {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_sub(PyObject* obj_left, PyObject* obj_right) {
  if (PyObject_TypeCheck(obj_left, &PointType) != 0 &&
      PyObject_TypeCheck(obj_right, &PointType) != 0) {
    const auto* left = reinterpret_cast<Point*>(obj_left);
    const auto* right = reinterpret_cast<Point*>(obj_right);

    return create_point(left->x - right->x, left->y - right->y);
  } else {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_mul(PyObject* obj_left, PyObject* obj_right) {
  if (PyObject_TypeCheck(obj_left, &PointType) != 0 &&
      PyLong_Check(obj_right)) {
    const auto* left = reinterpret_cast<Point*>(obj_left);
    const auto right = PyLong_AsLong(obj_right);

    return create_point(left->x * right, left->y * right);
  } else {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_true_div(PyObject* obj_left, PyObject* obj_right) {
  if (PyObject_TypeCheck(obj_left, &PointType) != 0 &&
      PyLong_Check(obj_right)) {
    const auto* left = reinterpret_cast<Point*>(obj_left);
    const auto right = PyLong_AsLong(obj_right);

    return create_point(left->x / right, left->y / right);
  } else {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_floor_div(PyObject* obj_left, PyObject* obj_right) {
  if (PyObject_TypeCheck(obj_left, &PointType) != 0 &&
      PyLong_Check(obj_right)) {
    const auto* left = reinterpret_cast<Point*>(obj_left);
    const auto right = PyLong_AsLong(obj_right);

    return create_point(
        static_cast<long>(std::floor(left->x / right)),
        static_cast<long>(std::floor(left->y / right)));
  } else {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_mod(PyObject* obj_left, PyObject* obj_right) {
  if (PyObject_TypeCheck(obj_left, &PointType) != 0 &&
      PyLong_Check(obj_right)) {
    const auto* left = reinterpret_cast<Point*>(obj_left);
    const auto right = PyLong_AsLong(obj_right);

    return create_point(
        static_cast<long>(left->x % right), static_cast<long>(left->y % right));
  } else {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_negate(PyObject* obj_left) {
  if (PyObject_TypeCheck(obj_left, &PointType) != 0) {
    const auto* left = reinterpret_cast<Point*>(obj_left);
    return create_point(-left->x, -left->y);
  } else {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_abs(PyObject* obj_left) {
  if (PyObject_TypeCheck(obj_left, &PointType) != 0) {
    const auto* left = reinterpret_cast<Point*>(obj_left);
    return create_point(std::abs(left->x), std::abs(left->y));
  } else {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }
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
        // Other comparisons are not supported.
        break;
    }
  } else {
    // Comparing == or != to wrong type is legal and should be returned as a
    // false result.
    switch (op) {
      case Py_EQ:
        result = Py_False;
        break;
      case Py_NE:
        result = Py_True;
        break;
      default:
        // Other comparisons are not supported.
        break;
    }
  }

  Py_INCREF(result);
  return result;
}

//--------------------------------------------------------------------------------------------------
Py_hash_t Point_hash(PyObject* obj_self) {
  const auto* self = reinterpret_cast<Point*>(obj_self);
  const auto h1 = std::hash<long>{}(self->x);
  const auto h2 = std::hash<long>{}(self->y);
  return h1 ^ (h2 << 1);
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_getstate(Point* self, PyObject*) {
  return Py_BuildValue("{slsl}", "x", self->x, "y", self->y);
}

//--------------------------------------------------------------------------------------------------
PyObject* Point_setstate(Point* self, PyObject* state) {
  // https://pythonextensionpatterns.readthedocs.io/en/latest/pickle.html
  // State object must be a dictionary.
  if (!PyDict_CheckExact(state)) {
    PyErr_SetString(PyExc_ValueError, "pickled object must be a dict");
    return nullptr;
  }

  // Load the x and y fields from the pickle state.
  if (!from_pyobj(PyDict_GetItemString(state, "x"), &self->x)) {
    PyErr_SetString(
        PyExc_ValueError, "pickled field `x` must exist and be an int");
    return nullptr;
  }

  if (!from_pyobj(PyDict_GetItemString(state, "y"), &self->y)) {
    PyErr_SetString(
        PyExc_ValueError, "pickled field `y` must exist and be an int");
    return nullptr;
  }

  Py_RETURN_NONE;
}
*/