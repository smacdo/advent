# Scott's Advent of Code Solutions
This repository functions as a way for me to have some fun solving code puzzles
while learning more Python at the same time. Nothing in this repository should
be considered high quality reviewable code. :)

# Running
```
python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt
pip install .
pre-commit install

advent_cli
```
 - Run tests: `python3 -m unittest discover tests`

## Oatmeal tests
```
mkdir xbuild
cd xbuild
cmake ../
make && ctest
```