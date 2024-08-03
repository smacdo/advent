from setuptools import setup, Extension

cpp_args = ["-std=c++20", "-stdlib=libc++", "-mmacosx-version-min=10.7"]

oatmeal_module = Extension(
    "oatmeal",
    sources=["oatmeal/module.cpp", "oatmeal/oatmeal.cpp", "oatmeal/point.cpp"],
    extra_compile_args=cpp_args,
)

setup(
    name="advent",
    ext_modules=[oatmeal_module],
    packages=["advent", "oatmeal"],
    package_data={"oatmeal": ["py.typed"]},
)
