import pytest
from game.utils import check_win, check_kong, check_pung, check_chow, score_hand, get_action_mask
from game.utils import HandStateDict, GameStateDict, PlayerStateDict
from game.tile import Tile, Suit
from game.constants import NUM_ACTIONS


@pytest.fixture
def p1() -> PlayerStateDict:
    # State of player 1
    p1_state: PlayerStateDict = {
        "id": 0,
        "seat_wind": "east",
        "hand": [],
        "melds": [],
        "discards": []
    }
    return p1_state


def test_check_kong_exposed(p1: PlayerStateDict) -> None:
    t1 = Tile(Suit.BAMBOO, "2")
    p1["melds"].append([t1] * 3)
    assert check_kong(p1, t1, True) == [[t1]*4]


def test_check_not_kong_exposed(p1: PlayerStateDict) -> None:
    t1 = Tile(Suit.BAMBOO, "2")
    t2 = Tile(Suit.BAMBOO, "3")
    p1["melds"].append([t1] * 2 + [t2])
    assert not check_kong(p1, t1, True)


def test_check_win_selfdraw(p1: PlayerStateDict) -> None:
    t1 = [Tile(Suit.BAMBOO, "1")]
    t2 = [Tile(Suit.BAMBOO, "2")]
    t3 = [Tile(Suit.BAMBOO, "3")]
    t4 = [Tile(Suit.DRAGON, "red")]
    t5 = [Tile(Suit.WIND, "west")]
    hand = t1 * 3 + t2 * 3 + t3 * 3 + t4 * 3 + t5 * 2
    p1["hand"] = hand
    w, s = check_win(p1, None, True)
    ref = [t1*3] + [t2*3] + [t3*3] + [t4*3] + [t5*2]
    assert set(tuple(i) for i in w) == set(tuple(i) for i in ref)


def test_check_win_selfdraw2(p1: PlayerStateDict) -> None:
    t1 = [Tile(Suit.DOT, "1")]
    t2 = [Tile(Suit.DOT, "2")]
    t3 = [Tile(Suit.DOT, "3")]
    t4 = [Tile(Suit.DRAGON, "red")]
    t5 = [Tile(Suit.WIND, "west")]
    t6 = [Tile(Suit.BAMBOO, "1")]
    hand = t1 * 2 + t2 * 2 + t3 * 2 + t4 * 3 + t5 * 3 + t6 * 2
    p1["hand"] = hand
    w, s = check_win(p1, None, True)
    ref = [t1 + t2 + t3]*2 + [t4*3] + [t5*3] + [t6*2]
    assert set(tuple(i) for i in w) == set(tuple(i) for i in ref)


def test_check_win_discard(p1: PlayerStateDict) -> None:
    t1 = [Tile(Suit.DOT, "1")]
    t2 = [Tile(Suit.DOT, "2")]
    t3 = [Tile(Suit.DOT, "3")]
    t4 = [Tile(Suit.DRAGON, "red")]
    t5 = [Tile(Suit.WIND, "west")]
    t6 = [Tile(Suit.BAMBOO, "1")]
    hand = t1 * 2 + t2 + t3 * 2 + t4 * 3 + t5 * 3 + t6 * 2
    p1["hand"] = hand
    w, s = check_win(p1, t2[0], False)
    ref = [t1 + t2 + t3]*2 + [t4*3] + [t5*3] + [t6*2]
    assert set(tuple(i) for i in w) == set(tuple(i) for i in ref)


def test_check_win_discard2(p1: PlayerStateDict) -> None:
    t1 = [Tile(Suit.DOT, "1")]
    t2 = [Tile(Suit.DOT, "2")]
    t3 = [Tile(Suit.DOT, "3")]
    t4 = [Tile(Suit.DRAGON, "red")]
    t5 = [Tile(Suit.WIND, "west")]
    t6 = [Tile(Suit.BAMBOO, "1")]
    hand = t1 * 2 + t2 * 1 + t3 * 2 + t4 * 4 + t5 * 4 + t6 * 2
    p1["hand"] = hand
    w, s = check_win(p1, t2[0], False)
    ref = [t1 + t2 + t3]*2 + [t4*4] + [t5*4] + [t6*2]
    assert set(tuple(i) for i in w) == set(tuple(i) for i in ref)


def test_check_pung_cp(p1: PlayerStateDict) -> None:
    t1 = Tile(Suit.DOT, "1")
    p1["hand"] = [t1] * 3
    assert check_pung(p1, t1, True) == [[t1]*3]


def test_check_not_pung_(p1: PlayerStateDict) -> None:
    t1 = Tile(Suit.DOT, "1")
    t2 = Tile(Suit.DOT, "2")
    p1["hand"] = [t1] * 3
    assert not check_pung(p1, t2, True)


def test_check_chow_cp(p1: PlayerStateDict) -> None:
    t1 = Tile(Suit.DOT, "1")
    t2 = Tile(Suit.DOT, "2")
    t3 = Tile(Suit.DOT, "3")
    p1["hand"] = [t1, t3, t2]
    assert check_chow(p1, t2, True) == [[t1, t2, t3]]


def test_check_chow_notcp(p1: PlayerStateDict) -> None:
    t1 = Tile(Suit.DOT, "3")
    t2 = Tile(Suit.DOT, "4")
    t3 = Tile(Suit.DOT, "5")
    p1["hand"] = [t3, t2]
    assert check_chow(p1, t1, False) == [[t1, t2, t3]]


def test_check_not_chow(p1: PlayerStateDict) -> None:
    t1 = Tile(Suit.DOT, "1")
    t2 = Tile(Suit.DOT, "2")
    t3 = Tile(Suit.DOT, "4")
    p1["hand"] = [t1, t2, t3]
    assert not check_chow(p1, t2, True)


def test_score_hand1() -> None:
    t1 = [Tile(Suit.BAMBOO, "1")]
    t2 = [Tile(Suit.BAMBOO, "2")]
    t3 = [Tile(Suit.BAMBOO, "3")]
    t4 = [Tile(Suit.DRAGON, "red")]
    t5 = [Tile(Suit.WIND, "west")]
    t6 = [Tile(Suit.FLOWER, "5")]
    melds = [t1 + t2 + t3] * 3 + [t4 * 3] + [t5 * 2] + [t6]
    state: HandStateDict = {
        "round_wind": "east",
        "seat_wind": "east",
        "win_condition": ["self_pick"],
        "thirteen_orphans": False,
        "nine_gates": False
    }
    assert score_hand(melds, state) == 3+1+1+1  # half flush, self pick, red dragon, own flower


def test_score_hand2() -> None:
    t1 = [Tile(Suit.BAMBOO, "1")]
    t2 = [Tile(Suit.BAMBOO, "2")]
    t3 = [Tile(Suit.BAMBOO, "3")]
    t4 = [Tile(Suit.BAMBOO, "4")]
    t5 = [Tile(Suit.BAMBOO, "5")]
    melds = [t1*3] + [t2*3] + [t3*4] + [t4*4] + [t5 * 2]
    state: HandStateDict = {
        "round_wind": "east",
        "seat_wind": "east",
        "win_condition": ["self_pick", "last_draw"],
        "thirteen_orphans": False,
        "nine_gates": False
    }
    assert score_hand(melds, state) == 7+1+1+3+1  # full flush, self pick, last draw, all pungs, no flowers


def test_score_hand3() -> None:
    t1 = [Tile(Suit.DOT, "1")]
    t2 = [Tile(Suit.BAMBOO, "2")]
    t3 = [Tile(Suit.BAMBOO, "3")]
    t4 = [Tile(Suit.BAMBOO, "4")]
    t5 = [Tile(Suit.WIND, "east")]
    t6 = [Tile(Suit.FLOWER, "6")]
    melds = [t1 * 3] + [t2 + t3 + t4] * 2 + [t5 * 3] + [t4 * 2] + [t6]
    state: HandStateDict = {
        "round_wind": "east",
        "seat_wind": "east",
        "win_condition": [],
        "thirteen_orphans": False,
        "nine_gates": False
    }
    assert score_hand(melds, state) == 2  # round wind, seat wind


def test_score_thirteen_orphans() -> None:
    melds = [
        [Tile(Suit.BAMBOO, "1")],
        [Tile(Suit.BAMBOO, "9")],
        [Tile(Suit.DOT, "1")],
        [Tile(Suit.DOT, "9")],
        [Tile(Suit.CHARACTER, "1")],
        [Tile(Suit.CHARACTER, "9")],
        [Tile(Suit.DRAGON, "red")],
        [Tile(Suit.DRAGON, "green")],
        [Tile(Suit.DRAGON, "white")],
        [Tile(Suit.WIND, "east")],
        [Tile(Suit.WIND, "west")],
        [Tile(Suit.WIND, "south")],
        [Tile(Suit.WIND, "north")],
        [Tile(Suit.WIND, "north")]
    ]
    state: HandStateDict = {
        "round_wind": "east",
        "seat_wind": "east",
        "win_condition": ["concealed_hand"],
        "thirteen_orphans": True,
        "nine_gates": False
    }
    assert score_hand(melds, state) == 13  # thirteen orphans


def test_score_mixed_orphans() -> None:
    t1 = [Tile(Suit.BAMBOO, "1")]
    t2 = [Tile(Suit.BAMBOO, "9")]
    t3 = [Tile(Suit.DOT, "1")]
    t4 = [Tile(Suit.DRAGON, "red")]
    t5 = [Tile(Suit.WIND, "west")]
    melds = [t1 * 3] + [t2 * 3] + [t3 * 3] + [t4 * 3] + [t5 * 2]
    state: HandStateDict = {
        "round_wind": "east",
        "seat_wind": "east",
        "win_condition": [],
        "thirteen_orphans": False,
        "nine_gates": False
    }
    assert score_hand(melds, state) == 1+1+3+1  # mixed orphans, red dragon, all pungs, no flowers


def test_score_orphans() -> None:
    t1 = [Tile(Suit.BAMBOO, "1")]
    t2 = [Tile(Suit.BAMBOO, "9")]
    t3 = [Tile(Suit.DOT, "1")]
    t4 = [Tile(Suit.BAMBOO, "9")]
    t5 = [Tile(Suit.CHARACTER, "1")]
    melds = [t1 * 3] + [t2 * 3] + [t3 * 3] + [t4 * 3] + [t5 * 2]
    state: HandStateDict = {
        "round_wind": "east",
        "seat_wind": "east",
        "win_condition": [],
        "thirteen_orphans": False,
        "nine_gates": False
    }
    assert score_hand(melds, state) == 13  # orphans (10), all pungs (3), no flowers (1)


def test_action_mask_meld() -> None:
    t1 = Tile(Suit.BAMBOO, "2")
    t2 = Tile(Suit.BAMBOO, "3")
    t3 = Tile(Suit.BAMBOO, "4")
    t4 = Tile(Suit.BAMBOO, "5")
    t5 = Tile(Suit.WIND, "west")
    p0_state: PlayerStateDict = {
        "id": 0,
        "seat_wind": "east",
        "hand": [t1, t1, t1, t2, t2, t3, t3, t4, t4, t5, t5, t5, t5],
        "melds": [],
        "discards": []
    }
    game_state: GameStateDict = {
        "players": {
            0: p0_state
        },
        "wall": [],
        "round_wind": "east",
        "current_player": 0,  # idx into self.players
        "first": False,  # flag the very first turn
        "discard": False,  # skip drawing a tile
        "kong": False,  # for tracking win by kong, indicates if a replacement tile is to be drawn due to a kong
        "double_kong": False,  # for tracking win by double kong
        "draw": False,  # indicates if the game ends in a draw
        "done": False,
        "winning_hand_state": None,
        "phase": "meld",  # game phase -- "meld", "discard", informs action mask generation
    }
    mask = get_action_mask(game_state, 0, t4)
    exp_res = [0] * NUM_ACTIONS
    exp_res[-1] = 1  # pass
    exp_res[68] = 1  # 5 bamboo pung
    exp_res[43] = 1  # 3-4-5 bamboo chow
    assert mask == exp_res


def test_action_mask_discard() -> None:
    t1 = Tile(Suit.BAMBOO, "2")
    t2 = Tile(Suit.BAMBOO, "3")
    t3 = Tile(Suit.BAMBOO, "4")
    t4 = Tile(Suit.BAMBOO, "5")
    t5 = Tile(Suit.WIND, "west")
    p0_state: PlayerStateDict = {
        "id": 0,
        "seat_wind": "east",
        "hand": [t1, t1, t1, t2, t2, t3, t3, t4, t4, t5, t5, t5, t5],
        "melds": [],
        "discards": []
    }
    game_state: GameStateDict = {
        "players": {
            0: p0_state
        },
        "wall": [],
        "round_wind": "east",
        "current_player": 0,  # idx into self.players
        "first": False,  # flag the very first turn
        "discard": False,  # skip drawing a tile
        "kong": False,  # for tracking win by kong, indicates if a replacement tile is to be drawn due to a kong
        "double_kong": False,  # for tracking win by double kong
        "draw": False,  # indicates if the game ends in a draw
        "done": False,
        "winning_hand_state": None,
        "phase": "discard",  # game phase -- "meld", "discard", informs action mask generation
    }
    mask = get_action_mask(game_state, 0, None)
    exp_res = [0] * NUM_ACTIONS
    exp_res[10:14] = [1, 1, 1, 1]  # discard bamboos
    exp_res[33] = 1  # discard west wind
    assert mask == exp_res
