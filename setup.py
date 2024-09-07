from skbuild import setup


setup(
    packages=["advent", "oatmeal", "donner"],
    package_dir={"": "src"},
    package_data={"oatmeal": ["py.typed"]},
)
