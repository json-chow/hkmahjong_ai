import pytest
from game.player import HumanPlayer
from game.tile import Tile, Suit
from game.utils import GameStateDict


@pytest.fixture
def p1() -> HumanPlayer:
    return HumanPlayer(1)


@pytest.fixture
def state() -> GameStateDict:
    return {
        "wall": [],
        "round_wind": "east",
        "current_player": 1,
        "first": False,
        "discard": False,
        "kong": False,
        "double_kong": False,
        "draw": False,
        "done": False,
        "winning_hand_state": None,
        "phase": "discard",
        "players": {
            0: {
                "id": 0,
                "seat_wind": "east",
                "hand": [],
                "melds": [],
                "discards": []
            },
            1: {
                "id": 1,
                "seat_wind": "south",
                "hand": [],
                "melds": [],
                "discards": []
            },
            2: {
                "id": 2,
                "seat_wind": "west",
                "hand": [],
                "melds": [],
                "discards": []
            },
            3: {
                "id": 3,
                "seat_wind": "north",
                "hand": [],
                "melds": [],
                "discards": []
            }
        }
    }


def test_discard_tile(p1: HumanPlayer, state: GameStateDict) -> None:
    t1 = [Tile(Suit.BAMBOO, "1")]
    t2 = [Tile(Suit.BAMBOO, "2")]
    t3 = [Tile(Suit.BAMBOO, "3")]
    t4 = [Tile(Suit.DRAGON, "red")]
    t5 = [Tile(Suit.WIND, "west")]
    state["players"][p1.id]["hand"] = t2 * 3 + t1 * 3 + t3 * 3 + t4 * 3 + t5 * 2
    assert p1.query_discard(state, sorted_hand=True, idx=4) == 0
