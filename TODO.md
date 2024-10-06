# Misc
- Investigate tox for test running
- Build oatmeal with optimizations when used as python module
- Build oatmeal with sanitizers when used in C++ tests
- Stand up CI testing
 - Run python unit tests
 - Run available solutions against cached answers

## Improve cli
- `advent_cli solve` with no arguments should run any solver with no cached answer
- `advent_cli solve [year] day` should solve specific puzzle (rather than all)
- `advent_cli solve --all [year]` should solve all puzzles for year or all puzzles
- Print the amount of time it took to solve each puzzle. The time should also
  break down each part, eg "solved in X seconds (part 1 took X seconds, part 2 took Y seconds)
- Solve multiple puzzles at once - use as many threads as there are CPU cores.
  - Any threaded solutions should be defered to the end and solved one at a time.
- Solutions should time out after configurable amount of time.

- If more than one solver, print a table format like so:

```
# Puzzles
Puzzle      | Examples | Part One       | Part Two        | Time
------------+----------+----------------+-----------------+--------------------------
The fir ... | OK       | OK             | OK              | 0.3 seconds (0.1 + 0.2)
Day 2       | FAIL     | SKIPPED        | SKIPPED         | 0.0 seconds
Day 3       |          | NOT IMPLMENTED | NOT IMPLEMENTED | 0.0 seconds

# Errors
## Day 2
Example 1 part 1 failed. Expected `FOO` but got `BAR` for input:
'''
YOUR_INPUT_HERE
'''

# Summary
1 OK
1 FAILED
1 SKIPPED

Total puzzle time: 0.3 seconds
Time saved with multi-threading: 0.0 seconds

Final Execution time: 0.3 seconds
```

## Implement puzzle solution scaffolding
`advent_cli scaffold [year] day`
where year is optional and defaults the most recent valid year.

write src/advent/yNNNN/dNN.py with:

```
from donner.annotations import solver
from donner.solution import AbstractSolver


@solver(day=${DAY}, year=${YEAR}, name="${PUZZLE_NAME}")
class Day${DAY}Solver(AbstractSolver):
    def part_one(self, input: str) -> int | str | None:
        return None

    def part_two(self, input: str) -> int | str | None:
        return None
```

# Missing tests
- Grid.diagonal_neighbors

# Improvements

# Utils
- Add alternate `end = ...` and `last = ...` parameters to the Range constructor.

# Bugs