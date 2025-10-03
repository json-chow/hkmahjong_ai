from __future__ import annotations
import typing
from abc import ABC, abstractmethod
import random


if typing.TYPE_CHECKING:
    from game.tile import Tile


class Player(ABC):
    id: int
    hand: list[Tile]
    melds: list[list[Tile]]
    discards: list[Tile]
    seat_wind: str

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

    @abstractmethod
    def query_meld(self, type: str, options: list[list[Tile]]) -> int:
        pass

    @abstractmethod
    def query_discard(self, sorted_hand: bool = False) -> Tile:
        pass

    def perform_meld(self, to_meld: list[Tile]) -> None:
        # Perform each meld
        for tile in to_meld:
            self.hand.remove(tile)
        self.melds.append(to_meld)
        # TODO: exposed pung --> kong

    def __str__(self) -> str:
        return (
            f"Player {self.id} ({self.seat_wind})\n"
            f"Hand: {self.hand}\n"
            f"Melds: {self.melds}"
        )


class HumanPlayer(Player):

    def query_meld(self, type: str, options: list[list[Tile]]) -> int:
        '''Manual melding performed by human player'''
        print(f"Player {self.id}, you have a potential {type}")
        print("0: Skip")
        for i in range(1, len(options)+1):
            print(f"{i}: {options[i-1]}")
        return int(input("Choice: "))

    def query_discard(self, sorted_hand: bool = False, idx: typing.Optional[int] = None) -> Tile:
        if not idx:  # used for testing
            idx = int(input(f"Choose a discard (0...{len(self.hand)-1}): "))
        if sorted_hand:
            idx = self.hand.index(sorted(self.hand)[idx])
        discarded_tile = self.hand.pop(idx)
        self.discards.append(discarded_tile)
        return discarded_tile


class RandomAIPlayer(Player):

    def query_meld(self, type: str, options: list[list[Tile]]) -> int:
        return random.randint(0, len(options))

    def query_discard(self, sorted_hand: bool = False) -> Tile:
        idx = random.randint(0, len(self.hand)-1)
        if sorted_hand:
            idx = self.hand.index(sorted(self.hand)[idx])
        discarded_tile = self.hand.pop(idx)
        self.discards.append(discarded_tile)
        return discarded_tile
