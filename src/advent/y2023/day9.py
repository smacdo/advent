import logging
from donner.annotations import solver, example
from donner.solution import AbstractSolver
from advent.utils import find_ints


def predict(sequence: list[int], pos: int, modifier: int) -> int:
    prediction = 0

    while not all(x == 0 for x in sequence):
        logging.debug(
            f"predict itr: seq = {sequence}, x = {sequence[pos]}, p = {prediction}, pos = {pos}, mod = {modifier}"
        )
        assert len(sequence) > 1

        prediction = modifier * prediction + sequence[pos]

        for i in range(1, len(sequence)):
            sequence[i - 1] = sequence[i] - sequence[i - 1]

        del sequence[-1]

    logging.info(f"prediction is {prediction}")
    return modifier * prediction


@solver(day=9, year=2023, name="Mirage Maintenance")
@example(
    input=[
        "0 3 6 9 12 15",
        "1 3 6 10 15 21",
        "10 13 16 21 30 45",
    ],
    part_one="114",
    part_two="2",
)
class Day9Solver(AbstractSolver):
    def part_one(self, input: str) -> int | str | None:
        prediction_sum = 0

        for line in input.splitlines():
            prediction_sum += predict(find_ints(line), -1, 1)

        return prediction_sum

    def part_two(self, input: str) -> int | str | None:
        prediction_sum = 0

        for line in input.splitlines():
            prediction_sum += predict(find_ints(line), 0, -1)

        return prediction_sum
