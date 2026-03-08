from enum import IntEnum
from game.tile import Tile, Suit, Value

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

NUMBER_VALUES = list(Value)[:9]
DRAGON_VALUES = list(Value)[9:12]
WIND_VALUES = list(Value)[12:]

TILE_TO_ID = {}

cnt = 0
for suit in Suit:
    if suit.name in {"DOT", "BAMBOO", "CHARACTER"}:
        for value in NUMBER_VALUES:
            tile = Tile(suit, value)
            TILE_TO_ID[tile] = cnt
            cnt += 1
    elif suit.name == "DRAGON":
        for value in DRAGON_VALUES:
            tile = Tile(suit, value)
            TILE_TO_ID[tile] = cnt
            cnt += 1
    elif suit.name == "WIND":
        for value in WIND_VALUES:
            tile = Tile(suit, value)
            TILE_TO_ID[tile] = cnt
            cnt += 1

CHOW_TO_ID = {}

cnt = 0
for suit in ["DOT", "BAMBOO", "CHARACTER"]:
    for value in list(Value)[:7]:
        tile = Tile(Suit[suit], value)
        CHOW_TO_ID[tile] = cnt
        cnt += 1
