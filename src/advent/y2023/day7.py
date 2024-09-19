from collections import Counter
from dataclasses import dataclass
from enum import IntEnum
from functools import total_ordering
from advent.utils import split
from donner.annotations import example, solver
from donner.solution import AbstractSolver
import logging


class Type(IntEnum):
    HighCard = 1
    OnePair = 2
    TwoPair = 3
    ThreeOfAKind = 4
    FullHouse = 5
    FourOfAKind = 6
    FiveOfAKind = 7


CARD_POWER = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
    "X": 1,  # 'J' joker card for part 2.
}


@dataclass
@total_ordering
class Hand:
    cards: list[str]
    bid: int

    def type(self) -> Type:
        card_counts = Counter(c for c in self.cards)
        mc = card_counts.most_common()

        # Convert jokers to the most common card if they are present.
        if "X" in self.cards:
            # Edge case - convert only when there are non-joker cards present.
            if len(mc) != 1 or mc[0][0] != "X":
                # Find most common card that is not a joker.
                most_common_card = next(filter(lambda x: x[0] != "X", mc))[0]
                card_counts[most_common_card] += card_counts["X"]

                del card_counts["X"]

                mc = card_counts.most_common()

        assert len(mc) > 0
        assert mc[0][1] <= 5

        logging.debug(f"cards={self.cards}, counts={card_counts}")

        if mc[0][1] == 5:
            return Type.FiveOfAKind
        elif mc[0][1] == 4:
            return Type.FourOfAKind
        elif mc[0][1] == 3 and mc[1][1] == 2:
            return Type.FullHouse
        elif mc[0][1] == 3 and mc[1][1] == 1:  # and mc[2][1] == 1
            return Type.ThreeOfAKind
        elif mc[0][1] == 2 and mc[1][1] == 2:  # and mc[2][1] == 1
            return Type.TwoPair
        elif mc[0][1] == 2 and mc[1][1] == 1:
            return Type.OnePair
        elif mc[0][1] == 1:
            return Type.HighCard
        else:
            raise Exception(
                f"could not type hand cards={self.cards}, counts={card_counts}"
            )

    def __str__(self) -> str:
        return f"cards=[{"".join(self.cards)}], type={self.type()}, bid={self.bid}"

    def __le__(self, other: "Hand") -> bool:
        my_rank = int(self.type())
        other_rank = int(other.type())

        if my_rank != other_rank:
            return my_rank < other_rank
        else:
            for i in range(0, len(self.cards)):
                my_card = self.cards[i]
                other_card = other.cards[i]

                if my_card != other_card:
                    return CARD_POWER[my_card] < CARD_POWER[other_card]

            raise Exception(f"cards are equal, self = {self.cards}, other = {other}")


def parse_input(input: str) -> list[Hand]:
    hands: list[Hand] = []

    for line in input.splitlines():
        cards_str, bid_str = split(line, " ")
        hands.append(Hand([c for c in cards_str], int(bid_str)))

    return hands


@solver(day=7, year=2023, name="Camel Cards")
@example(
    input=[
        "32T3K 765",
        "T55J5 684",
        "KK677 28",
        "KTJJT 220",
        "QQQJA 483",
    ],
    part_one="6440",
    part_two="5905",
)
class Day7Solver(AbstractSolver):
    def part_one(self, input: str) -> int | str | None:
        hands = parse_input(input)
        hands.sort()

        total_winnings = 0

        for i, h in enumerate(hands):
            rank = i + 1
            win = rank * h.bid
            total_winnings += win

            logging.debug(f"hand={h}, rank={rank}, bid={h.bid} -> {win}")

        return total_winnings

    def part_two(self, input: str) -> int | str | None:
        # swap out jokers J -> X to keep the same scoring code in part 1 and 2.
        input = input.replace("J", "X")

        hands = parse_input(input)
        hands.sort()

        total_winnings = 0

        for i, h in enumerate(hands):
            rank = i + 1
            win = rank * h.bid
            total_winnings += win

            logging.debug(f"hand={h}, rank={rank}, bid={h.bid} -> {win}")

        return total_winnings
