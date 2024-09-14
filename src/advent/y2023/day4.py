from dataclasses import dataclass
from advent.utils import find_ints, split
from donner.annotations import example, solver
from donner.solution import AbstractSolver
import logging


@dataclass
class Card:
    winning_numbers: list[int]
    my_numbers: list[int]


def parse_card(text: str) -> Card:
    _, numbers_text = split(text, ":")
    winning_numbers_text, my_numbers_text = split(numbers_text, "|")

    winning_numbers = list(find_ints(winning_numbers_text))
    my_numbers = list(find_ints(my_numbers_text))

    return Card(winning_numbers, my_numbers)


@solver(day=4, year=2023, name="Scratchcards")
@example(
    input=[
        "Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53",
        "Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19",
        "Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1",
        "Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83",
        "Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36",
        "Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11",
    ],
    part_one="13",
    part_two="30",
)
class Day4Solver(AbstractSolver):
    def part_one(self, input: str) -> int | str | None:
        # Tally the cards.
        sum = 0

        for card_line_text in input.splitlines():
            # Count the number of matches for this card.
            card = parse_card(card_line_text)
            num_matches = 0

            for x in card.my_numbers:
                if x in card.winning_numbers:
                    num_matches += 1

            # Sum the match score of each card.
            if num_matches > 0:
                sum += 2 ** (num_matches - 1)

        return sum

    def part_two(self, input: str) -> int | str | None:
        # Tally the cards.
        cards: list[Card] = [parse_card(line) for line in input.splitlines()]
        count: list[int] = [1 for _ in cards]

        for index, card in enumerate(cards):
            # Count the number of matches for this card.
            num_matches = 0

            for x in card.my_numbers:
                if x in card.winning_numbers:
                    num_matches += 1

            # Generate new card copies based on the number of matches.
            logging.debug(
                f"card {index + 1} with {count[index]} copies had {num_matches} matches and will award {count[index]} copies"
            )

            for x in range(index + 1, min(index + num_matches + 1, len(count))):
                count[x] += count[index]
                logging.debug(
                    f" -> card {x + 1} will receive {count[index]} for new total of {count[x]}"
                )

        # Show the final card counts.
        for index, c in enumerate(count):
            logging.info(f"game {index + 1} had {c} copies")

        return sum(count)
