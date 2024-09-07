from skbuild import setup


setup(
    packages=["advent", "oatmeal"],
    package_dir={"": "src"},
    package_data={"oatmeal": ["py.typed"]},
)
