import logging
from donner.annotations import solver, example
from donner.solution import AbstractSolver
from advent.utils import find_ints


def predict(sequence: list[int], index: int) -> int:
    prediction = 0

    while not all(x == 0 for x in sequence):
        logging.debug(f"{sequence}, element={sequence[index]} (index {index})")
        assert len(sequence) > 1

        prediction += sequence[index]

        for i in range(1, len(sequence)):
            sequence[i - 1] = sequence[i] - sequence[i - 1]

        del sequence[index]

    logging.info(f"sequence = {sequence}, index = {index}, prediction = {prediction}")
    return prediction


@solver(day=9, year=2023, name="Mirage Maintenance")
@example(
    input=[
        "0 3 6 9 12 15",
        "1 3 6 10 15 21",
        "10 13 16 21 30 45",
    ],
    part_one="114",
)
@example(
    input="10 13 16 21 30 45",
    part_two="2",
)
class Day9Solver(AbstractSolver):
    def part_one(self, input: str) -> int | str | None:
        prediction_sum = 0

        for line in input.splitlines():
            prediction_sum += predict(find_ints(line), -1)

        return prediction_sum

    def part_two(self, input: str) -> int | str | None:
        prediction_sum = 0

        for line in input.splitlines():
            prediction_sum += predict(find_ints(line), 0)

        return prediction_sum
