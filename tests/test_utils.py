import pytest
from game.utils import check_win, check_kong, check_pung, check_chow, score_hand
from game.tile import Tile
from game.player import Player


@pytest.fixture
def p1():
    return Player(1, "east")


def test_check_kong_exposed(p1):
    t1 = Tile("bamboo", "2")
    p1.melds.append([t1] * 3)
    assert check_kong(p1, t1, True) == [[t1]*4]


def test_check_not_kong_exposed(p1):
    t1 = Tile("bamboo", "2")
    t2 = Tile("bamboo", "3")
    p1.melds.append([t1] * 2 + [t2])
    assert not check_kong(p1, t1, True)


def test_check_win_selfdraw(p1):
    t1 = [Tile("bamboo", "1")]
    t2 = [Tile("bamboo", "2")]
    t3 = [Tile("bamboo", "3")]
    t4 = [Tile("dragon", "red")]
    t5 = [Tile("wind", "west")]
    hand = t1 * 3 + t2 * 3 + t3 * 3 + t4 * 3 + t5 * 2
    p1.hand = hand
    w, s = check_win(p1, None, True)
    ref = [t1*3] + [t2*3] + [t3*3] + [t4*3] + [t5*2]
    assert set(tuple(i) for i in w) == set(tuple(i) for i in ref)


def test_check_win_selfdraw2(p1):
    t1 = [Tile("dot", "1")]
    t2 = [Tile("dot", "2")]
    t3 = [Tile("dot", "3")]
    t4 = [Tile("dragon", "red")]
    t5 = [Tile("wind", "west")]
    t6 = [Tile("bamboo", "1")]
    hand = t1 * 2 + t2 * 2 + t3 * 2 + t4 * 3 + t5 * 3 + t6 * 2
    p1.hand = hand
    w, s = check_win(p1, None, True)
    ref = [t1 + t2 + t3]*2 + [t4*3] + [t5*3] + [t6*2]
    assert set(tuple(i) for i in w) == set(tuple(i) for i in ref)


def test_check_win_discard(p1):
    t1 = [Tile("dot", "1")]
    t2 = [Tile("dot", "2")]
    t3 = [Tile("dot", "3")]
    t4 = [Tile("dragon", "red")]
    t5 = [Tile("wind", "west")]
    t6 = [Tile("bamboo", "1")]
    hand = t1 * 2 + t2 + t3 * 2 + t4 * 3 + t5 * 3 + t6 * 2
    p1.hand = hand
    w, s = check_win(p1, t2[0], False)
    ref = [t1 + t2 + t3]*2 + [t4*3] + [t5*3] + [t6*2]
    assert set(tuple(i) for i in w) == set(tuple(i) for i in ref)


def test_check_win_discard2(p1):
    t1 = [Tile("dot", "1")]
    t2 = [Tile("dot", "2")]
    t3 = [Tile("dot", "3")]
    t4 = [Tile("dragon", "red")]
    t5 = [Tile("wind", "west")]
    t6 = [Tile("bamboo", "1")]
    hand = t1 * 2 + t2 * 1 + t3 * 2 + t4 * 4 + t5 * 4 + t6 * 2
    p1.hand = hand
    w, s = check_win(p1, t2[0], False)
    ref = [t1 + t2 + t3]*2 + [t4*4] + [t5*4] + [t6*2]
    assert set(tuple(i) for i in w) == set(tuple(i) for i in ref)


def test_check_pung_cp(p1):
    t1 = Tile("dot", "1")
    p1.hand = [t1] * 3
    assert check_pung(p1, t1, True) == [[t1]*3]


def test_check_not_pung_(p1):
    t1 = Tile("dot", "1")
    t2 = Tile("dot", "2")
    p1.hand = [t1] * 3
    assert not check_pung(p1, t2, True)


def test_check_chow_cp(p1):
    t1 = Tile("dot", "1")
    t2 = Tile("dot", "2")
    t3 = Tile("dot", "3")
    p1.hand = [t1, t3, t2]
    assert check_chow(p1, t2, True) == [[t1, t2, t3]]


def test_check_chow_notcp(p1):
    t1 = Tile("dot", "3")
    t2 = Tile("dot", "4")
    t3 = Tile("dot", "5")
    p1.hand = [t3, t2]
    assert check_chow(p1, t1, False) == [[t1, t2, t3]]


def test_check_not_chow(p1):
    t1 = Tile("dot", "1")
    t2 = Tile("dot", "2")
    t3 = Tile("dot", "4")
    p1.hand = [t1, t2, t3]
    assert not check_chow(p1, t2, True)


def test_score_hand1():
    t1 = [Tile("bamboo", "1")]
    t2 = [Tile("bamboo", "2")]
    t3 = [Tile("bamboo", "3")]
    t4 = [Tile("dragon", "red")]
    t5 = [Tile("wind", "west")]
    t6 = [Tile("flower", "5")]
    melds = [t1 + t2 + t3] * 3 + [t4 * 3] + [t5 * 2] + [t6]
    state = {
        "round_wind": "east",
        "seat_wind": "east",
        "win_condition": ["self_pick"],
        "thirteen_orphans": False,
        "nine_gates": False
    }
    assert score_hand(melds, state) == 3+1+1+1  # half flush, self pick, red dragon, own flower


def test_score_hand2():
    t1 = [Tile("bamboo", "1")]
    t2 = [Tile("bamboo", "2")]
    t3 = [Tile("bamboo", "3")]
    t4 = [Tile("bamboo", "4")]
    t5 = [Tile("bamboo", "5")]
    melds = [t1*3] + [t2*3] + [t3*4] + [t4*4] + [t5 * 2]
    state = {
        "round_wind": "east",
        "seat_wind": "east",
        "win_condition": ["self_pick", "last_draw"],
        "thirteen_orphans": False,
        "nine_gates": False
    }
    assert score_hand(melds, state) == 7+1+1+3+1  # full flush, self pick, last draw, all pungs, no flowers


def test_score_hand3():
    t1 = [Tile("dot", "1")]
    t2 = [Tile("bamboo", "2")]
    t3 = [Tile("bamboo", "3")]
    t4 = [Tile("bamboo", "4")]
    t5 = [Tile("wind", "east")]
    t6 = [Tile("flower", "6")]
    melds = [t1 * 3] + [t2 + t3 + t4] * 2 + [t5 * 3] + [t4 * 2] + [t6]
    state = {
        "round_wind": "east",
        "seat_wind": "east",
        "win_condition": [],
        "thirteen_orphans": False,
        "nine_gates": False
    }
    assert score_hand(melds, state) == 2  # round wind, seat wind


def test_score_thirteen_orphans():
    melds = [
        [Tile("bamboo", "1")],
        [Tile("bamboo", "9")],
        [Tile("dot", "1")],
        [Tile("dot", "9")],
        [Tile("character", "1")],
        [Tile("character", "9")],
        [Tile("dragon", "red")],
        [Tile("dragon", "green")],
        [Tile("dragon", "white")],
        [Tile("wind", "east")],
        [Tile("wind", "west")],
        [Tile("wind", "south")],
        [Tile("wind", "north")],
        [Tile("wind", "north")]
    ]
    state = {
        "round_wind": "east",
        "seat_wind": "east",
        "win_condition": ["concealed_hand"],
        "thirteen_orphans": True,
        "nine_gates": False
    }
    assert score_hand(melds, state) == 13  # thirteen orphans


def test_score_mixed_orphans():
    t1 = [Tile("bamboo", "1")]
    t2 = [Tile("bamboo", "9")]
    t3 = [Tile("dots", "1")]
    t4 = [Tile("dragon", "red")]
    t5 = [Tile("wind", "west")]
    melds = [t1 * 3] + [t2 * 3] + [t3 * 3] + [t4 * 3] + [t5 * 2]
    state = {
        "round_wind": "east",
        "seat_wind": "east",
        "win_condition": [],
        "thirteen_orphans": False,
        "nine_gates": False
    }
    assert score_hand(melds, state) == 1+1+3+1  # mixed orphans, red dragon, all pungs, no flowers


def test_score_orphans():
    t1 = [Tile("bamboo", "1")]
    t2 = [Tile("bamboo", "9")]
    t3 = [Tile("dot", "1")]
    t4 = [Tile("bamboo", "9")]
    t5 = [Tile("character", "1")]
    melds = [t1 * 3] + [t2 * 3] + [t3 * 3] + [t4 * 3] + [t5 * 2]
    state = {
        "round_wind": "east",
        "seat_wind": "east",
        "win_condition": [],
        "thirteen_orphans": False,
        "nine_gates": False
    }
    assert score_hand(melds, state) == 13  # orphans (10), all pungs (3), no flowers (1)
