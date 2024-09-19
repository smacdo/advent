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


JOKERS_WILD_POWER = 1
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
}


@dataclass
@total_ordering
class Hand:
    cards: list[str]
    bid: int
    jokers_are_wild: bool

    def type(self) -> Type:
        # Count the cards and then get a list of the most common cards sorted in
        # ascending order.
        card_counts = Counter(c for c in self.cards)
        mc = card_counts.most_common()

        # When jokers are wild, treat all of the joker cards as the most common
        # card except when there are no other cards except for jokers.
        if self.jokers_are_wild and "J" in self.cards and len(mc) > 1:
            # Find the most common non-joker card.
            # NOTE: This will throw an exception if there are no non-joker cards.
            most_common_card = next(filter(lambda x: x[0] != "J", mc))[0]

            # Make jokers count to the most common non-joker card.
            card_counts[most_common_card] += card_counts["J"]

            # Remove the joker cards from the count.
            del card_counts["J"]

            # Recount the cards now that the jokers have been transformed.
            mc = card_counts.most_common()

        # Find the highest scoring category for this hand.
        if mc[0][1] == 5:
            return Type.FiveOfAKind
        elif mc[0][1] == 4:
            return Type.FourOfAKind
        elif mc[0][1] == 3 and mc[1][1] == 2:
            return Type.FullHouse
        elif mc[0][1] == 3 and mc[1][1] == 1:
            return Type.ThreeOfAKind
        elif mc[0][1] == 2 and mc[1][1] == 2:
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
        def card_power(c: str) -> int:
            if self.jokers_are_wild and c == "J":
                return JOKERS_WILD_POWER
            else:
                return CARD_POWER[c]

        my_rank = int(self.type())
        other_rank = int(other.type())

        if my_rank != other_rank:
            return my_rank < other_rank
        else:
            for i in range(0, len(self.cards)):
                my_card = self.cards[i]
                other_card = other.cards[i]

                if my_card != other_card:
                    return card_power(my_card) < card_power(other_card)

            raise Exception(f"cards are equal, self = {self.cards}, other = {other}")


def parse_input(input: str, jokers_are_wild: bool = False) -> list[Hand]:
    hands: list[Hand] = []

    for line in input.splitlines():
        cards_str, bid_str = split(line, " ")
        hands.append(
            Hand([c for c in cards_str], int(bid_str), jokers_are_wild=jokers_are_wild)
        )

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
        hands = parse_input(input, jokers_are_wild=True)
        hands.sort()

        total_winnings = 0

        for i, h in enumerate(hands):
            rank = i + 1
            win = rank * h.bid
            total_winnings += win

            logging.debug(f"hand={h}, rank={rank}, bid={h.bid} -> {win}")

        return total_winnings
