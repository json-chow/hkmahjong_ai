import pytest
from game.tile import Tile, Suit


@pytest.fixture
def tile1() -> Tile:
    return Tile(Suit.BAMBOO, "1")


@pytest.fixture
def tile2() -> Tile:
    return Tile(Suit.DRAGON, "green")


def test_eq(tile1: Tile) -> None:
    assert tile1 == tile1


def test_not_eq(tile1: Tile, tile2: Tile) -> None:
    assert tile1 != tile2


def test_lt(tile1: Tile, tile2: Tile) -> None:
    assert tile1 < tile2


def test_str(tile1: Tile) -> None:
    assert str(tile1) == "1_BAMBOO"
