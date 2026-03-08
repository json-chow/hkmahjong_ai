from enum import Enum


Suit = Enum("Suit", ["DOT", "BAMBOO", "CHARACTER", "DRAGON", "WIND", "FLOWER"])


class Tile:
    values = ["1", "2", "3", "4", "5", "6", "7", "8", "9",
              "red", "white", "green",  # dragons
              "east", "south", "north", "west"]  # winds
    # Let flowers 1-4 be flowers and flowers 5-8 be seasons

    def __init__(self, suit: Suit, value: str) -> None:
        self.suit = suit
        self.value = value

    def __str__(self) -> str:
        if self.suit == Suit.FLOWER:
            return f"{(int(self.value) - 1) % 4 + 1}_FLOWER"
        return self.value + "_" + self.suit.name

    def __repr__(self) -> str:
        return str(self)

    def __lt__(self, other: "Tile") -> bool:
        # compare by suits
        if self.suit != other.suit:
            return self.suit.value < other.suit.value
        # otherwise, compare by value
        return Tile.values.index(self.value) < Tile.values.index(other.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tile):
            return NotImplemented
        return self.suit == other.suit and self.value == other.value

    def __hash__(self) -> int:
        return hash((self.suit, self.value))
