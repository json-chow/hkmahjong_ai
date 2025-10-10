from __future__ import annotations
import typing
from abc import ABC, abstractmethod
import random
from game.utils import GameStateDict


if typing.TYPE_CHECKING:
    from game.tile import Tile


class Player(ABC):
    id: int

    def __init__(self, id: int) -> None:
        self.id = id

    @abstractmethod
    def query_meld(self, state: GameStateDict, type: str, options: list[list[Tile]]) -> int:
        pass

    @abstractmethod
    def query_discard(self, state: GameStateDict, sorted_hand: bool) -> int:
        pass

    def __str__(self) -> str:
        return str(self.id)


class HumanPlayer(Player):

    def query_meld(self, state: GameStateDict, type: str, options: list[list[Tile]]) -> int:
        '''Manual melding performed by human player'''
        print(f"Player {self.id}, you have a potential {type}")
        print("0: Skip")
        for i in range(1, len(options)+1):
            print(f"{i}: {options[i-1]}")
        return int(input("Choice: "))

    def query_discard(self, state: GameStateDict, sorted_hand: bool = False, idx: typing.Optional[int] = None) -> int:
        curr_hand = state["players"][self.id]["hand"]
        if not idx:  # used for testing
            idx = int(input(f"Choose a discard (0...{len(curr_hand)-1}): "))
        if sorted_hand:
            idx = curr_hand.index(sorted(curr_hand)[idx])
        return idx


class RandomAIPlayer(Player):

    def query_meld(self, state: GameStateDict, type: str, options: list[list[Tile]]) -> int:
        if type == "win":
            return 1  # always win
        return random.randint(0, len(options))

    def query_discard(self, state: GameStateDict, sorted_hand: bool = False) -> int:
        curr_hand = state["players"][self.id]["hand"]
        idx = random.randint(0, len(curr_hand)-1)
        if sorted_hand:
            idx = curr_hand.index(sorted(curr_hand)[idx])
        return idx
