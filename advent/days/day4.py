#!/usr/bin/env python3
import re
import unittest

from advent.solver import AdventDaySolver, AdventDayTestCase, solver_main


# TODO: rename read_space_delim_input ?
def split_space_delim_input(input):
    return [x for x in input.split(" ") if x != ""]


class Card:
    def __init__(self, id, winning_numbers, my_numbers):
        self.id = id
        self.winning_numbers = [int(x) for x in winning_numbers]
        self.my_numbers = [int(x) for x in my_numbers]
        self.copies = 0

    def points(self):
        m = self.matches()
        return pow(2, len(m) - 1) if len(m) > 0 else 0

    def matches(self):
        return [x for x in self.my_numbers if x in self.winning_numbers]

    def num_matches(self):
        return len(self.matches())


def parse_card_input(input):
    card_matcher = re.search("Card\\s+(\\d+): ([0-9 ]+) \\| ([0-9 ]+)", input)

    if not card_matcher:
        raise Exception(f"failed to regex parse card input `{input}`")

    game_id = int(card_matcher.group(1))
    winning_numbers = split_space_delim_input(card_matcher.group(2))
    my_numbers = split_space_delim_input(card_matcher.group(3))

    return Card(game_id, winning_numbers, my_numbers)


def parse_card_inputs(lines):
    return [parse_card_input(line) for line in lines]


def scoring_with_copy(cards_in):
    cards = cards_in.copy()

    for i, card in enumerate(cards):
        for j in range(card.num_matches()):
            card_index = i + 1 + j

            if card_index >= len(cards):
                continue

            cards[card_index].copies += card.copies + 1

    return cards


class Solver(
    AdventDaySolver, day=4, year=2023, name="Scratchcards", solution=(17803, 5554894)
):
    def __init__(self, input):
        super().__init__(input)

    def solve(self):
        self.cards = parse_card_inputs(self.input)

        # Part one scoring
        self.scores = [s.points() for s in self.cards]
        score_sum = sum(self.scores)

        # Part two scoring
        p2_cards = scoring_with_copy(self.cards)
        card_count_sum = sum([s.copies + 1 for s in p2_cards])

        return (score_sum, card_count_sum)


class Tests(AdventDayTestCase):
    def setUp(self):
        super().setUp(Solver)

    def test_sample(self):
        d = self._create_sample_solver(
            """Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11"""
        )
        s = d.solve()

        self.assertEqual([8, 2, 2, 1, 0, 0], d.scores)
        self.assertEqual(13, sum(d.scores))

        self.assertEqual(13, s[0])
        self.assertEqual(30, s[1])

    def test_parse_card_input(self):
        card = parse_card_input("Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1")
        self.assertEqual(card.id, 3)
        self.assertEqual(card.winning_numbers, [1, 21, 53, 59, 44])
        self.assertEqual(card.my_numbers, [69, 82, 63, 72, 16, 21, 14, 1])

    def test_card_score(self):
        card = parse_card_input("Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1")
        self.assertEqual(card.points(), 2)

    def test_split_space_delim_input(self):
        self.assertEqual(["a", "b", "c"], split_space_delim_input("   a    b c   "))


if __name__ == "__main__":
    solver_main(unittest.TestProgram(exit=False), Solver)
