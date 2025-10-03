import pytest
from game.player import HumanPlayer
from game.tile import Tile


@pytest.fixture
def p1():
    return HumanPlayer(1, "east")


def test_discard_tile(p1):
    t1 = [Tile("bamboo", "1")]
    t2 = [Tile("bamboo", "2")]
    t3 = [Tile("bamboo", "3")]
    t4 = [Tile("dragon", "red")]
    t5 = [Tile("wind", "west")]
    p1.hand = t1 * 3 + t2 * 3 + t3 * 3 + t4 * 3 + t5 * 2
    p1.query_discard(idx=4)
    assert p1.hand == t1 * 3 + t2 * 2 + t3 * 3 + t4 * 3 + t5 * 2
    assert p1.discards == t2


def test_perform_meld(p1):
    t1 = [Tile("bamboo", "1")]
    t2 = [Tile("bamboo", "2")]
    t3 = [Tile("bamboo", "3")]
    t4 = [Tile("dragon", "red")]
    t5 = [Tile("wind", "west")]
    p1.hand = t1 * 3 + t2 * 3 + t3 * 3 + t4 * 3 + t5 * 2
    p1.perform_meld(t3*3)
    assert p1.hand == t1 * 3 + t2 * 3 + t4 * 3 + t5 * 2
    assert p1.melds == [t3*3]
