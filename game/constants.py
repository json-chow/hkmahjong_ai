from enum import IntEnum
from game.tile import Tile, Suit

# number of unique tiles, excl flowers
NUM_TILES = 34


class Action(IntEnum):
    # Possible discards
    DISCARD = 0
    DISCARD_END = NUM_TILES

    # Possible chows
    CHOW = DISCARD_END
    CHOW_END = CHOW + 21  # 7 per suit

    # Possible pungs
    PUNG = CHOW_END
    PUNG_END = PUNG + NUM_TILES

    # Possible kongs
    KONG = PUNG_END
    KONG_END = KONG + NUM_TILES

    # Other actions
    WIN = KONG_END
    PASS = WIN + 1


NUM_ACTIONS = Action.PASS + 1

TILE_TO_ID = {}

cnt = 0
for suit in Suit:
    if suit.name in {"DOT", "BAMBOO", "CHARACTER"}:
        for value in Tile.values[:9]:
            tile = Tile(suit, value)
            TILE_TO_ID[tile] = cnt
            cnt += 1
    elif suit.name == "DRAGON":
        for value in Tile.values[9:12]:
            tile = Tile(suit, value)
            TILE_TO_ID[tile] = cnt
            cnt += 1
    elif suit.name == "WIND":
        for value in Tile.values[12:]:
            tile = Tile(suit, value)
            TILE_TO_ID[tile] = cnt
            cnt += 1

CHOW_TO_ID = {}

cnt = 0
for suit in ["DOT", "BAMBOO", "CHARACTER"]:
    for value in Tile.values[:7]:
        tile = Tile(Suit[suit], value)
        CHOW_TO_ID[tile] = cnt
        cnt += 1
