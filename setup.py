from skbuild import setup


setup(
    packages=["advent", "advent.y2023", "oatmeal", "donner"],
    package_dir={"": "src"},
    package_data={"oatmeal": ["py.typed"]},
)
