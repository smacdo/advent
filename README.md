# Scott's Advent of Code Solutions
This repository functions as a way for me to have some fun solving code puzzles
while learning more Python at the same time. Nothing in this repository should
be considered high quality reviewable code. :)

# Running
```
python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt
python3 setup.py install

python3 -m advent.cli
```
 - Run tests: `python3 -m unittest discover tests`

(outdated)
 - Solve a specific day: `python3 main.py solve 0 2023`
 - Run the tests for specific day: `python3 -m advent.days.day0`
 - Run tests: `python3 -m unittest discover tests`

# Tasks
- Switch to encryption rather than obscuration. Use a ENV VAR to allow testing
  in CI.
- Ensure strictest typing checks
