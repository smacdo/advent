# Misc
- Investigate tox for test running
- Build oatmeal with optimizations when used as python module
- Build oatmeal with sanitizers when used in C++ tests

## Improve cli
- `advent_cli solve [year] day` should solve specific puzzle (rather than all)
- `advent_cli solve --all [year]` should solve all puzzles for year or all puzzles

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

# Bugs
- Status message "Tested the examples for ..." should not be printed if solver
  does not have any examples.