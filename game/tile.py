from enum import Enum, StrEnum


Suit = Enum("Suit", ["DOT", "BAMBOO", "CHARACTER", "DRAGON", "WIND", "FLOWER"])
Value = StrEnum("Value", [
    # Numbers (let flowers 1-4 be flowers, 5-8 be seasons)
    ("ONE", "1"),
    ("TWO", "2"),
    ("THREE", "3"),
    ("FOUR", "4"),
    ("FIVE", "5"),
    ("SIX", "6"),
    ("SEVEN", "7"),
    ("EIGHT", "8"),
    ("NINE", "9"),
    # Dragons
    ("RED", "red"),
    ("WHITE", "white"),
    ("GREEN", "green"),
    # Winds
    ("EAST", "east"),
    ("SOUTH", "south"),
    ("NORTH", "north"),
    ("WEST", "west")
])


class Tile:
    def __init__(self, suit: Suit, value: Value) -> None:
        self.suit = suit
        self.value = value

    def __str__(self) -> str:
        if self.suit == Suit.FLOWER:
            return f"{(int(self.value.value) - 1) % 4 + 1}_FLOWER"
        return self.value.value + "_" + self.suit.name

    def __repr__(self) -> str:
        return str(self)

    def __lt__(self, other: "Tile") -> bool:
        # compare by suits
        if self.suit != other.suit:
            return self.suit.value < other.suit.value
        # otherwise, compare by value using enum def order
        enum_list = list(Value)
        return enum_list.index(self.value) < enum_list.index(other.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tile):
            return NotImplemented
        return self.suit == other.suit and self.value == other.value

    def __hash__(self) -> int:
        return hash((self.suit, self.value))
