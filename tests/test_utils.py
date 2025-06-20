import pytest
from game.utils import check_win, check_kong, check_pung, check_chow
from game.tile import Tile
from game.player import Player


@pytest.fixture
def p1():
    return Player(1, "E")


def test_check_kong_exposed(p1):
    t1 = Tile("bamboo", "2")
    p1.melds.append([t1] * 3)
    assert check_kong(p1, t1, True) == [[t1]*4]


def test_check_not_kong_exposed(p1):
    t1 = Tile("bamboo", "2")
    t2 = Tile("bamboo", "3")
    p1.melds.append([t1] * 2 + [t2])
    assert not check_kong(p1, t1, True)


def test_check_kong_concealed_cp(p1):
    t1 = Tile("bamboo", "2")
    p1.hand.extend([t1] * 4)
    assert check_kong(p1, t1, True) == [[t1]*4]


def test_check_kong_concealed_notcp(p1):
    t1 = Tile("bamboo", "2")
    p1.hand.extend([t1] * 3)
    assert check_kong(p1, t1, False) == [[t1]*4]


def test_check_not_kong_concealed(p1):
    t1 = Tile("bamboo", "2")
    t2 = Tile("bamboo", "3")
    p1.hand.extend([t1] * 2 + [t2])
    assert not check_kong(p1, t1, True)


def test_check_win_selfdraw(p1):
    t1 = [Tile("bamboo", "1")]
    t2 = [Tile("bamboo", "2")]
    t3 = [Tile("bamboo", "3")]
    t4 = [Tile("dragon", "red")]
    t5 = [Tile("wind", "west")]
    hand = t1 * 3 + t2 * 3 + t3 * 3 + t4 * 3 + t5 * 2
    p1.hand = hand
    w = check_win(p1, None, True)
    ref = [[t1*3] + [t2*3] + [t3*3] + [t4*3] + [t5*2],
           [t1 + t2 + t3]*3 + [t4*3] + [t5*2]]
    for i in range(len(w)):
        assert set(tuple(i) for i in w[i]) == set(tuple(i) for i in ref[i])


def test_check_win_selfdraw2(p1):
    t1 = [Tile("dot", "1")]
    t2 = [Tile("dot", "2")]
    t3 = [Tile("dot", "3")]
    t4 = [Tile("dragon", "red")]
    t5 = [Tile("wind", "west")]
    t6 = [Tile("bamboo", "1")]
    hand = t1 * 2 + t2 * 2 + t3 * 2 + t4 * 3 + t5 * 3 + t6 * 2
    p1.hand = hand
    w = check_win(p1, None, True)
    ref = [[t1 + t2 + t3]*2 + [t4*3] + [t5*3] + [t6*2]]
    for i in range(len(w)):
        assert set(tuple(i) for i in w[i]) == set(tuple(i) for i in ref[i])


def test_check_win_discard(p1):
    t1 = [Tile("dot", "1")]
    t2 = [Tile("dot", "2")]
    t3 = [Tile("dot", "3")]
    t4 = [Tile("dragon", "red")]
    t5 = [Tile("wind", "west")]
    t6 = [Tile("bamboo", "1")]
    hand = t1 * 2 + t2 + t3 * 2 + t4 * 3 + t5 * 3 + t6 * 2
    p1.hand = hand
    w = check_win(p1, t2[0], False)
    ref = [[t1 + t2 + t3]*2 + [t4*3] + [t5*3] + [t6*2]]
    for i in range(len(w)):
        assert set(tuple(i) for i in w[i]) == set(tuple(i) for i in ref[i])


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
