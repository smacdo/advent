from setuptools import setup, Extension

cpp_args = ['-std=c+20', '-stdlib=libc++', '-mmacosx-version-min=10.7']

oatmeal_module = Extension("oatmeal", sources = ["oatmeal/module.cpp", "oatmeal/oatmeal.cpp"], extra_compile_args=cpp_args)

setup(
    name='oatmeal',
    version='0.1',
    description='Boring but healthy tools written in C++ for speed',
    ext_modules=[oatmeal_module]
)