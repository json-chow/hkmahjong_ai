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
    def query_meld(self, state: GameStateDict, options: dict) -> tuple[str, list[Tile] | list[list[Tile]]]:
        pass

    @abstractmethod
    def query_discard(self, state: GameStateDict, sorted_hand: bool) -> int:
        pass

    def __str__(self) -> str:
        return str(self.id)


class HumanPlayer(Player):

    # def query_meld(self, state: GameStateDict, type: str, options: list[list[Tile]]) -> int:
    #     '''Manual melding performed by human player'''
    #     print(f"Player {self.id}, you have a potential {type}")
    #     print("0: Skip")
    #     for i in range(1, len(options)+1):
    #         print(f"{i}: {options[i-1]}")
    #     return int(input("Choice: "))

    def query_meld(self, state: GameStateDict, options: dict) -> tuple[str, list[Tile] | list[list[Tile]]]:
        print(f"Player {self.id}, you have a potential meld")
        # Choose type of meld
        print("0: Skip")
        idx = 1
        win_idx = -1
        possible_choices = {}
        for meld_type in options:
            if options[meld_type]:
                print(f"{idx}: {meld_type}")
                possible_choices[idx] = meld_type
                if meld_type == "win":
                    win_idx = idx
                idx += 1
        choice = int(input("Choice: "))

        # Choose specific meld
        if choice == 0:
            return "", []
        if choice == win_idx:
            return "win", options["win"]

        melds = options[possible_choices[choice]]
        for i in range(len(melds)):
            print(f"{i}: {melds[i]}")
        meld_choice = int(input("Choice: "))
        return possible_choices[choice], melds[meld_choice]

    def query_discard(self, state: GameStateDict, sorted_hand: bool = False, idx: typing.Optional[int] = None) -> int:
        curr_hand = state["players"][self.id]["hand"]
        if idx is None:  # used for testing
            idx = int(input(f"Choose a discard (0...{len(curr_hand)-1}): "))
        if sorted_hand:
            idx = curr_hand.index(sorted(curr_hand)[idx])
        return idx


class RandomAIPlayer(Player):

    def __init__(self, id: int, seed: int | None = None) -> None:
        super().__init__(id)
        self.rng = random.Random(seed)

    def query_meld(self, state: GameStateDict, options: dict) -> tuple[str, list[Tile] | list[list[Tile]]]:
        # TODO: fixed action space for the melds
        # Choose type of meld
        idx = 1
        win_idx = -1
        possible_choices = {}
        for meld_type in options:
            if options[meld_type]:
                possible_choices[idx] = meld_type
                if meld_type == "win":
                    win_idx = idx
                idx += 1
        choice = self.rng.randint(0, len(possible_choices)) if win_idx == -1 else win_idx

        # Choose specific meld
        if choice == 0:
            return "", []
        if choice == win_idx:
            return "win", options["win"]

        melds = options[possible_choices[choice]]
        meld_choice = self.rng.randint(0, len(melds)-1)
        return possible_choices[choice], melds[meld_choice]

    def query_discard(self, state: GameStateDict, sorted_hand: bool = False) -> int:
        curr_hand = state["players"][self.id]["hand"]
        idx = self.rng.randint(0, len(curr_hand)-1)
        if sorted_hand:
            idx = curr_hand.index(sorted(curr_hand)[idx])
        return idx
