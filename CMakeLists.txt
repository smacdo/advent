cmake_minimum_required(VERSION 3.15...3.26)

project(advent VERSION "0.1")

find_package(Python COMPONENTS Interpreter REQUIRED)

#==============================================================================#
# External libraries                                                           #
#==============================================================================#
include(FetchContent)

# GTest
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/releases/download/v1.15.2/googletest-1.15.2.tar.gz
  URL_HASH SHA256=7b42b4d6ed48810c5362c265a17faebe90dc2373c885e5216439d37927f02926
  PREFIX ${CMAKE_CURRENT_BINARY_DIR}/gtest
  INSTALL_COMMAND ""
)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

# Pybind11
FetchContent_Declare(
  pybind11
  URL https://github.com/pybind/pybind11/archive/refs/tags/v2.13.5.tar.gz
  URL_HASH SHA256=b1e209c42b3a9ed74da3e0b25a4f4cd478d89d5efbb48f04b277df427faf6252
)
FetchContent_MakeAvailable(pybind11)

#==============================================================================#
# Oatmeal target independent static library                                    #
#==============================================================================#
set(oatmeal_sources
  src/oatmeal/point.cpp
  src/oatmeal/point.h
  src/oatmeal/vector.cpp
  src/oatmeal/vector.h
)

set(oatmeal_tests
  src/oatmeal/grid.tests.cpp
  src/oatmeal/grid_rect_points.tests.cpp
  src/oatmeal/point.tests.cpp
  src/oatmeal/vector.tests.cpp
)

#==============================================================================#
# _oatmeal python extension                                                    #
#==============================================================================#
set(python_module_name _oatmeal)
pybind11_add_module(${python_module_name} MODULE
  src/oatmeal/module.cpp
  ${oatmeal_sources}
)

target_compile_features(${python_module_name} PUBLIC cxx_std_20)

# XXX(scott): the scikit-build examples use `DESINTATION .` but that results in
# the .so copied to `env\` rather than the `env\pythonX.X\site-packages\oatmeal`.
# 
# This seems to work but I could easily be doing it wrong. I'm not an expert in
# CMake-foo
install(TARGETS ${python_module_name} DESTINATION "lib/python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}/site-packages/oatmeal")

#==============================================================================#
# Oatmeal unit tests                                                           #
#==============================================================================#
add_executable(oatmeal_test 
  ${oatmeal_sources}
  ${oatmeal_tests}
)
target_compile_features(oatmeal_test PUBLIC cxx_std_20)
target_link_libraries(oatmeal_test gtest_main gmock)

enable_testing()
add_test(NAME    oatmeal_test 
         COMMAND oatmeal_test)