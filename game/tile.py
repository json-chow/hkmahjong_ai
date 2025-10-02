class Tile:

    suits = ["dot", "bamboo", "character", "dragon", "wind", "flower"]
    values = ["1", "2", "3", "4", "5", "6", "7", "8", "9",
              "red", "white", "green",  # dragons
              "east", "south", "north", "west"]  # winds
    # Let flowers 1-4 be flowers and flowers 5-8 be seasons

    def __init__(self, suit: str, value: str) -> None:
        self.suit = suit
        self.value = value

    def __str__(self) -> str:
        return self.value + "_" + self.suit

    def __repr__(self) -> str:
        return str(self)

    def __lt__(self, other: "Tile") -> bool:
        # compare by suits
        if self.suit != other.suit:
            if Tile.suits.index(self.suit) < Tile.suits.index(other.suit):
                return True
            else:
                return False
        else:
            # compare by value
            if Tile.values.index(self.value) < Tile.values.index(other.value):
                return True
            else:
                return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tile):
            return NotImplemented
        return self.suit == other.suit and self.value == other.value

    def __hash__(self) -> int:
        return hash((self.suit, self.value))
