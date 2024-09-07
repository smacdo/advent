cmake_minimum_required(VERSION 3.15...3.26)

project(scotts-advent-of-code-solutions)

# Define CMAKE_INSTALL_xxx: LIBDIR, INCLUDEDIR
include(GNUInstallDirs)
include(FetchContent)

FetchContent_Declare(
  pybind11
  URL https://github.com/pybind/pybind11/archive/refs/tags/v2.13.5.tar.gz
  URL_HASH SHA256=b1e209c42b3a9ed74da3e0b25a4f4cd478d89d5efbb48f04b277df427faf6252
)
FetchContent_MakeAvailable(pybind11)

pybind11_add_module(oatmeal MODULE
  src/oatmeal/module.cpp
  src/oatmeal/oatmeal.cpp
  src/oatmeal/oatmeal.h
  src/oatmeal/point.cpp
  src/oatmeal/point.h
)

install(TARGETS ${python_module_name} DESTINATION .)