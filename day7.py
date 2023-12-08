#!/usr/bin/env python3
import enum
import logging
import unittest

from utils import AdventDaySolver, AdventDayTestCase, init_logging

CARD_SCORE = {
    "2": (1, 2),
    "3": (2, 3),
    "4": (3, 4),
    "5": (4, 5),
    "6": (5, 6),
    "7": (6, 7),
    "8": (7, 8),
    "9": (8, 9),
    "T": (9, 10),
    "J": (10, 1),
    "Q": (11, 11),
    "K": (12, 12),
    "A": (13, 13),
}


def all_same(container):
    if len(container) == 0:
        # An empty container cannot be all the same because it contains nothing.
        return False
    return all(x == container[0] for x in container)


def parse_input(lines):
    entries = []
    for line in lines:
        hand, bid = line.split()
        entries.append(InputEntry(hand, int(bid)))
    return entries


class HandType(enum.IntEnum):
    HighCard = 1
    OnePair = 2
    TwoPair = 3
    ThreeKind = 4
    FullHouse = 5
    FourKind = 6
    FiveKind = 7


class InputEntry:
    def __init__(self, hand, bid):
        self.hand = Hand(hand, with_jokers=False)
        self.hand_p2 = Hand(hand, with_jokers=True)
        self.bid = bid


class Hand:
    def __init__(self, cards, with_jokers):
        self.cards = cards
        self.with_jokers = with_jokers
        self.type = Hand.classify(self.cards, self.with_jokers)

    def __str__(self):
        return self.cards

    def __repr__(self):
        return f"Hand({self.cards}, {self.type})"

    def score(self):
        # cards are ranked by position left to right, so
        #  ABCDE, A = card_score * 10000
        #                          1000
        #                          100
        #                          10
        #         E =            * 1
        score = 0
        tuple_i = 1 if self.with_jokers else 0

        for c in self.cards:
            score = score * 100 + CARD_SCORE[c][tuple_i]

        return score + (100000000000 * int(self.type))

    @staticmethod
    def classify(cards, with_jokers):
        assert len(cards) == 5
        lut = dict()

        for c in cards:
            if c in lut:
                lut[c] += 1
            else:
                lut[c] = 1

        # Remove jokers from the card list (if present) and re-add them to
        # the best scoring card.
        joker_count = 0

        if with_jokers and "J" in cards:
            joker_count = lut["J"]
            del lut["J"]

        # Sort keys by occurence of cards in descending order.
        keys = [k for k in lut.keys()]
        keys.sort(key=lambda x: lut[x], reverse=True)

        # Replace keys with their occurence count
        counts = [lut[k] for k in keys]
        logging.debug(f"{cards} => {counts} (LUT: {lut})")

        if with_jokers:
            if len(counts) == 0:
                counts = [joker_count]
            else:
                counts[0] += joker_count

        if counts[0] == 5:
            return HandType.FiveKind
        if counts[0] == 4:
            return HandType.FourKind
        if counts[0] == 3 and counts[1] == 2:
            return HandType.FullHouse
        if counts[0] == 3 and counts[1] == 1 and counts[2] == 1:
            return HandType.ThreeKind
        if counts[0] == 2 and counts[1] == 2 and counts[2] == 1:
            return HandType.TwoPair
        if 2 in counts:
            return HandType.OnePair
        else:
            return HandType.HighCard


class Solver(
    AdventDaySolver,
    day=7,
    year=2023,
    name="Camel Cards",
    solution=(250957639, 251515496),
):
    def __init__(self, input):
        super().__init__(input)
        self.entries = parse_input(input)

        # sort entries by rank
        entries = [e for e in self.entries]
        entries.sort(key=lambda x: x.hand.score() + 1)

        # assign rank to cards
        for i, e in enumerate(entries):
            e.hand.rank = i + 1

        # part2: resort entries by rank again using p2 score rules
        entries = [e for e in self.entries]
        entries.sort(key=lambda x: x.hand_p2.score() + 1)

        for i, e in enumerate(entries):
            e.hand_p2.rank = i + 1

    def solve(self):
        part_1 = sum(e.bid * e.hand.rank for e in self.entries)
        part_2 = sum(e.bid * e.hand_p2.rank for e in self.entries)

        return (part_1, part_2)


class Tests(AdventDayTestCase):
    def setUp(self):
        init_logging(logging.DEBUG)
        super().setUp(Solver)

    def test_sample(self):
        d = self._create_sample_solver(
            """32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483"""
        )

        self.assertEqual(5, len(d.entries))
        self.assertEqual("32T3K", d.entries[0].hand.cards)
        self.assertEqual(765, d.entries[0].bid)
        self.assertEqual("QQQJA", d.entries[4].hand.cards)
        self.assertEqual(483, d.entries[4].bid)

        self.assertEqual(HandType.OnePair, d.entries[0].hand.type)
        self.assertEqual(HandType.ThreeKind, d.entries[1].hand.type)
        self.assertEqual(HandType.TwoPair, d.entries[2].hand.type)
        self.assertEqual(HandType.TwoPair, d.entries[3].hand.type)
        self.assertEqual(HandType.ThreeKind, d.entries[4].hand.type)

        self.assertEqual(1, d.entries[0].hand.rank)
        self.assertEqual(4, d.entries[1].hand.rank)
        self.assertEqual(3, d.entries[2].hand.rank)
        self.assertEqual(2, d.entries[3].hand.rank)
        self.assertEqual(5, d.entries[4].hand.rank)

        # Part two
        self.assertEqual(HandType.OnePair, d.entries[0].hand_p2.type)
        self.assertEqual(HandType.FourKind, d.entries[1].hand_p2.type)
        self.assertEqual(HandType.TwoPair, d.entries[2].hand_p2.type)
        self.assertEqual(HandType.FourKind, d.entries[3].hand_p2.type)
        self.assertEqual(HandType.FourKind, d.entries[4].hand_p2.type)

        self.assertEqual(1, d.entries[0].hand_p2.rank)
        self.assertEqual(3, d.entries[1].hand_p2.rank)
        self.assertEqual(2, d.entries[2].hand_p2.rank)
        self.assertEqual(5, d.entries[3].hand_p2.rank)
        self.assertEqual(4, d.entries[4].hand_p2.rank)

        # Actual solver
        s = d.solve()

        self.assertEqual(6440, s[0])
        self.assertEqual(5905, s[1])

    def test_real_input(self):
        s = self._create_real_solver().solve()
        self.assertEqual(250957639, s[0])
        self.assertEqual(251515496, s[1])
        pass


if __name__ == "__main__":
    unittest.main()
