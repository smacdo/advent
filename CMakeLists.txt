cmake_minimum_required(VERSION 3.15...3.26)

project(advent VERSION "0.1")

# Define CMAKE_INSTALL_xxx: LIBDIR, INCLUDEDIR
include(GNUInstallDirs)
include(FetchContent)

find_package(Python COMPONENTS Interpreter REQUIRED)

FetchContent_Declare(
  pybind11
  URL https://github.com/pybind/pybind11/archive/refs/tags/v2.13.5.tar.gz
  URL_HASH SHA256=b1e209c42b3a9ed74da3e0b25a4f4cd478d89d5efbb48f04b277df427faf6252
)
FetchContent_MakeAvailable(pybind11)

set(python_module_name _oatmeal)
pybind11_add_module(${python_module_name} MODULE
  src/oatmeal/module.cpp
  src/oatmeal/oatmeal.cpp
  src/oatmeal/oatmeal.h
  src/oatmeal/point.cpp
  src/oatmeal/point.h
)

target_compile_features(${python_module_name} PUBLIC cxx_std_20)

# XXX(scott): the scikit-build examples use `DESINTATION .` but that results in
# the .so copied to `env\` rather than the `env\pythonX.X\site-packages\oatmeal`.
# 
# This seems to work but I could easily be doing it wrong. I'm not an expert in
# CMake-foo
install(TARGETS ${python_module_name} DESTINATION "lib/python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}/site-packages/oatmeal")