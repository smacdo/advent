# Scott's Advent of Code Solutions
This repository functions as a way for me to have some fun solving code puzzles
while learning more Python at the same time. Nothing in this repository should
be considered high quality reviewable code. :)

# First build steps
```
python3 -m venv env & source ./env/bin/activate
pip install -r requirements.txt
pip install .
pre-commit install
```

# Run
```
$ advent_cli --help
usage: advent_cli [-h] [-d] [-v] {solve,visualize} ...

options:
  -h, --help         show this help message and exit
  -d, --debug        Print debug log entries
  -v, --verbose      Print verbose (info) log entries

subcommands:
  {solve,visualize}
```

# Test
```
$ python3 -m unittest discover tests
```

## Oatmeal tests
```
mkdir xbuild
cd xbuild
cmake ../
make && ctest
```