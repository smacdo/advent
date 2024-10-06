import logging
from donner.annotations import solver, example
from donner.solution import AbstractSolver
from advent.utils import find_ints


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
            sequence = find_ints(line)
            prediction = 0

            while not all(x == 0 for x in sequence):
                logging.debug(
                    f"p1: {sequence}, element={sequence[-1]}, p = {prediction}"
                )
                assert len(sequence) > 1

                prediction += sequence[-1]

                for i in range(1, len(sequence)):
                    sequence[i - 1] = sequence[i] - sequence[i - 1]

                del sequence[-1]

            logging.info(f"p1: prediction = {prediction}")
            prediction_sum += prediction

        return prediction_sum

    def part_two(self, input: str) -> int | str | None:
        prediction_sum = 0

        for line in input.splitlines():
            sequence = find_ints(line)
            prediction = 0

            while not all(x == 0 for x in sequence):
                logging.debug(
                    f"p2: {sequence}, element={sequence[0]}, p = {prediction}"
                )
                assert len(sequence) > 1

                prediction = -prediction + sequence[0]

                for i in range(1, len(sequence)):
                    sequence[i - 1] = sequence[i] - sequence[i - 1]

                del sequence[-1]

            prediction = -prediction

            logging.info(f"p2 prediction = {prediction}")
            prediction_sum += prediction

        return prediction_sum
