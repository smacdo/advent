from donner.solution import (
    AbstractSolver,
    Example,
    Part,
    SolverMetadata,
    get_global_solver_registry,
)


def solver(
    day: int,
    year: int,
    name: str | None = None,
    variant: str | None = None,
):
    """
    Registers this class to solve puzzles for the given year and day.

    A class that is annotated with `@solver` will be automatically added to the
    list of solvers for a given Advent of Code year and day. The class must
    inherit from `AbstractSolver`.
    """

    def wrapper(solver_class: type[AbstractSolver]):
        if not issubclass(solver_class, AbstractSolver):
            raise ValueError("@solver class must inherit from AbstractSolver")

        get_global_solver_registry().add_metadata(
            SolverMetadata(
                klass=solver_class,
                year=year,
                day=day,
                puzzle_name=name,
                variant_name=variant,
            )
        )

        return solver_class

    return wrapper


def part_one_example(input: str | list[str], output: str):
    """Add an example input and the expected output for part one answers for this solver."""

    def wrapper(solver_class: type[AbstractSolver]):
        get_global_solver_registry().add_example(
            solver_class, Example(input=input, output=output, part=Part.One)
        )

        return solver_class

    return wrapper


def part_two_example(input: str | list[str], output: str):
    """Add an example input and the expected output for part two answers for this solver."""

    def wrapper(solver_class: type[AbstractSolver]):
        get_global_solver_registry().add_example(
            solver_class, Example(input=input, output=output, part=Part.Two)
        )

        return solver_class

    return wrapper
