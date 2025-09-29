from __future__ import annotations
import typing


if typing.TYPE_CHECKING:
    from game.tile import Tile


class Player:

    def __init__(self, id: int, wind: str) -> None:
        self.id = id
        self.hand = []
        self.melds = []
        self.discards = []
        self.seat_wind = wind

    def print_hand(self, sort_hand: bool = False) -> None:
        if sort_hand:
            print(", ".join(str(tile) for tile in sorted(self.hand)))
        else:
            print(", ".join(str(tile) for tile in self.hand))

    def print_melds(self) -> None:
        print(self.melds)

    def discard_tile(self, idx: int, sorted_hand: bool = False) -> Tile:
        if sorted_hand:
            idx = self.hand.index(sorted(self.hand)[idx])
        discarded_tile = self.hand.pop(idx)
        self.discards.append(discarded_tile)
        return discarded_tile

    def query_meld(self, type: str, options: list[list[Tile]]) -> str:
        '''Manual melding performed by human player'''
        print(f"Player {self.id}, you have a potential {type}")
        print("0: Skip")
        for i in range(1, len(options)+1):
            print(f"{i}: {options[i-1]}")
        return input("Choice: ")

    def perform_meld(self, to_meld: list[list[Tile]]) -> None:
        # Perform each meld
        for tile in to_meld:
            self.hand.remove(tile)
        self.melds.append(to_meld)
        # TODO: exposed pung --> kong

    def __str__(self) -> str:
        return str(self.id)
