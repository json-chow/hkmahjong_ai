from game.tile import Tile
from game.constants import Action, NUM_ACTIONS, TILE_TO_ID, CHOW_TO_ID
import random
from collections import Counter
from typing import TypedDict


FAAN = {
    # Hand types
    "common_hand": 1,
    "all_pung_kong": 3,
    "half_flush": 3,
    "full_flush": 7,
    "all_honors": 7,
    "small_dragons": 5,
    "great_dragons": 8,
    "small_winds": 6,
    "great_winds": 10,
    "thirteen_orphans": 13,
    "eighteen_arhats": 10,
    "orphans": 10,
    "nine_gates": 10,
    # Extra based on melds
    "seat_wind": 1,
    "round_wind": 1,
    "dragon": 1,
    "mixed_orphans": 1,
    # Extra based on win condition
    "self_pick": 1,  #
    "concealed_hand": 1,  #
    "rob_kong": 1,  #
    "last_draw": 1,  #
    "win_by_kong": 1,  #
    "win_by_double_kong": 8,  #
    "heavenly_hand": 13,  #
    "earthly_hand": 13,  #
    # Extra based on flowers
    "no_flowers": 1,
    "own_flower": 1,
    "set_of_flowers": 2
}


class HandStateDict(TypedDict):
    win_condition: list[str]
    thirteen_orphans: bool
    nine_gates: bool
    seat_wind: str
    round_wind: str | None


class PlayerStateDict(TypedDict):
    id: int
    seat_wind: str
    hand: list[Tile]
    melds: list[list[Tile]]
    discards: list[Tile]


class GameStateDict(TypedDict):
    wall: list[Tile]
    round_wind: str
    current_player: int
    first: bool
    discard: bool
    kong: bool
    double_kong: bool
    draw: bool
    done: bool
    winning_hand_state: HandStateDict | None
    phase: str
    players: dict[int, PlayerStateDict]


def init_wall(seed: int | None = None) -> list[Tile]:
    '''Initializes and shuffles the mahjong wall'''
    wall = []
    for suit in Tile.suits:
        if suit in {"dot", "bamboo", "character"}:
            for value in Tile.values[:9]:
                tile = Tile(suit, value)
                wall.append(tile)
        elif suit == "dragon":
            for value in Tile.values[9:12]:
                tile = Tile(suit, value)
                wall.append(tile)
        elif suit == "wind":
            for value in Tile.values[12:]:
                tile = Tile(suit, value)
                wall.append(tile)
    wall *= 4
    # Add in flower tiles
    for value in Tile.values[:8]:
        tile = Tile("flower", value)
        wall.append(tile)

    rng = random.Random(seed)
    rng.shuffle(wall)
    return wall


def score_hand(melds: list[list[Tile]], state: HandStateDict) -> int:
    '''Given melds and game state, return the number of faan'''
    score = 0
    suits = set()
    flowers = []
    chows = 0
    pungs = 0
    kongs = 0
    dragons = 0  # pungs
    winds = 0  # pungs
    all_flowers = [0, 0, 0, 0]
    all_seasons = [0, 0, 0, 0]
    orphan = True  # tracks if hand contains 1s and 9s and honors only
    pair = None

    for meld in melds:
        # Deal with flower 'melds'
        if meld[0].suit == "flower":
            flowers.append(meld[0])
            flower_val = int(meld[0].value)
            if flower_val >= 5:  # seasons are flower tiles w/values 5 to 8
                all_seasons[flower_val - 5] = 1
            else:  # flower
                all_flowers[flower_val - 1] = 1
            continue

        # Deal with general melds
        suits.add(meld[0].suit)
        if len(meld) == 3:
            # If the first and second tiles in the meld are the same, must be a pung
            if meld[0] == meld[1]:
                pungs += 1
                if meld[0].value not in {"1", "9"} and meld[0].suit not in {"dragon", "wind"}:
                    orphan = False
            # Otherwise, it must be a chow
            else:
                chows += 1
                orphan = False
        elif len(meld) == 4:
            kongs += 1
            # Orphan condition exists for kongs as well
            if meld[0].value not in {"1", "9"} and meld[0].suit not in {"dragon", "wind"}:
                orphan = False
        else:
            pair = meld[0]
            # Orphan condition for pairs as well
            if meld[0].value not in {"1", "9"} and meld[0].suit not in {"dragon", "wind"}:
                orphan = False
            continue  # don't go through honor meld logics if meld is a pair

        # Deal with honor melds
        if meld[0].suit == "dragon":
            dragons += 1
        elif meld[0].suit == "wind":
            winds += 1
            # Round wind
            if meld[0].value == state["round_wind"]:
                score += FAAN["round_wind"]
            # Seat wind
            if meld[0].value == state["seat_wind"]:
                score += FAAN["seat_wind"]

    # No flowers
    if len(flowers) == 0:
        score += FAAN["no_flowers"]
    # Own flower
    pos_to_wind = {1: "east", 2: "south", 3: "west", 4: "north"}
    for flower in flowers:
        if pos_to_wind[((int(flower.value) - 1) % 4) + 1] == state["seat_wind"]:
            score += FAAN["own_flower"]
    # All flower or season tiles
    if all(all_flowers):
        score += FAAN["set_of_flowers"]
    if all(all_seasons):
        score += FAAN["set_of_flowers"]

    # Win conditions -- self pick, win by kong, etc.
    for win_condition in state["win_condition"]:
        score += FAAN[win_condition]

    # Special hands (13 orphans, 9 gates, ...) [max points]
    if state["thirteen_orphans"]:
        return FAAN["thirteen_orphans"]
    if state["nine_gates"]:
        return FAAN["nine_gates"]

    # Common hand
    if pungs == 0 and kongs == 0:
        score += FAAN["common_hand"]
    if chows == 0:
        # All kongs hand
        if kongs == 4:
            score += FAAN["eighteen_arhats"]
        # All triplets or incl. kongs
        else:
            score += FAAN["all_pung_kong"]

    if ("dragon" in suits) or ("wind" in suits):
        if ("dragon" in suits) and ("wind" in suits):
            # Half flush (single suit and honors) -- dragon, wind, and a suit
            if len(suits) == 3:
                score += FAAN["half_flush"]
            # All honors hand
            elif len(suits) == 2:
                score += FAAN["all_honors"]
        else:
            # Half flush -- dragon or wind and a suit
            if len(suits) == 2:
                score += FAAN["half_flush"]
        # Great dragons
        if dragons == 3:
            score += FAAN["great_dragons"]
        # Small dragons
        elif (dragons == 2) and (pair and pair.suit == "dragon"):
            score += FAAN["small_dragons"]

        # Great winds
        if winds == 4:
            score += FAAN["great_winds"]
        # Small winds
        elif (winds == 3) and (pair and pair.suit == "wind"):
            score += FAAN["small_winds"]

        # Terminals + honors
        if orphan:
            score += FAAN["mixed_orphans"]
    else:
        # Full flush
        if len(suits) == 1:
            score += FAAN["full_flush"]

        # Only terminals
        if orphan:
            score += FAAN["orphans"]

    score += dragons  # 1 point per dragon
    return min(score, 13)  # 13 faan is max


def check_win(p_state: PlayerStateDict, tile: Tile | None, current_player: bool) -> tuple[list[list[Tile]], HandStateDict]:
    '''
    Checks if the player has either a self-draw win or a win by discard
    Returns the highest scoring meld combination that can be used to win
    '''

    state: HandStateDict = {
        "win_condition": [],
        "thirteen_orphans": False,
        "nine_gates": False,
        "seat_wind": p_state["seat_wind"],
        "round_wind": None
    }

    # Count number of tiles in current hand
    tile_counts = Counter(p_state["hand"])

    # Check for win by discard -- check if tile can be used to win
    if tile and not current_player:
        tile_counts[tile] += 1
    # ... otherwise, check for self-draw win -- check if current hand is a win
    else:
        state["win_condition"].append("self_pick")

    if len(p_state["melds"]) == 0 or all(len(i) == 1 for i in p_state["melds"]):
        # if no melds or all flower melds, then the current hand is concealed
        state["win_condition"].append("concealed_hand")

    # Check for thirteen orphans
    thirteen_orphans = {
        Tile("bamboo", "1"),
        Tile("bamboo", "9"),
        Tile("dot", "1"),
        Tile("dot", "9"),
        Tile("character", "1"),
        Tile("character", "9"),
        Tile("dragon", "red"),
        Tile("dragon", "green"),
        Tile("dragon", "white"),
        Tile("wind", "east"),
        Tile("wind", "west"),
        Tile("wind", "south"),
        Tile("wind", "north")
    }
    if thirteen_orphans.issubset(tile_counts):
        # If all required tiles are in the hand, then it must be that the hand is a thirteen orphans
        state["thirteen_orphans"] = True
        return [p_state["hand"]], state

    # Check for nine gates
    if state["win_condition"]:
        # Check if all tiles are of a single suit
        if len(set(tile.suit for tile in p_state["hand"])) == 1:
            suit = p_state["hand"][0].suit
            # Check if each number of the suit is in the hand
            for val in range(1, 10):
                if Tile(suit, str(val)) not in p_state["hand"]:
                    break
            else:
                # Check if there are three of 1 and three of 9 in the hand
                if len([tile for tile in p_state["hand"] if tile.value == "1"]) == 3 and \
                   len([tile for tile in p_state["hand"] if tile.value == "9"]) == 3:
                    state["nine_gates"] = True
                    return [p_state["hand"]], state

    possible_wins = []
    for tile in tile_counts:
        # Check over all possible pairs
        if tile_counts[tile] >= 2:
            tile_counts[tile] -= 2
            status, melds = _check_meld(tile_counts)
            if status:
                for meld in melds:
                    possible_wins.append(meld + [[tile]*2])
            tile_counts[tile] += 2
    best_win = max(possible_wins, key=lambda x: score_hand(x, state)) if possible_wins else []
    return best_win, state


def _check_meld(tile_counts: Counter) -> tuple[bool, list[list[list[Tile]]]]:
    '''Checks and returns all melds if melds can be formed in a hand'''
    if tile_counts.total() == 0:
        return True, [[]]

    # Get tile with a non-zero count
    for tile in tile_counts:
        if tile_counts[tile] > 0:
            break

    melds = []
    # Check for kongs
    if tile_counts[tile] == 4:
        tile_counts[tile] -= 4
        status, other_melds = _check_meld(tile_counts)
        if status:
            for meld in other_melds:
                melds.append(meld + [[tile]*4])
        tile_counts[tile] += 4

    # Check for pungs
    if tile_counts[tile] >= 3:
        tile_counts[tile] -= 3
        status, other_melds = _check_meld(tile_counts)
        if status:
            for meld in other_melds:
                melds.append(meld + [[tile]*3])
        tile_counts[tile] += 3

    # Check for chows
    if tile.suit in Tile.suits[:3] and int(tile.value) <= 7:
        t2 = Tile(tile.suit, str(int(tile.value)+1))
        t3 = Tile(tile.suit, str(int(tile.value)+2))
        if tile_counts[t2] > 0 and tile_counts[t3] > 0:
            tile_counts[tile] -= 1
            tile_counts[t2] -= 1
            tile_counts[t3] -= 1
            status, other_melds = _check_meld(tile_counts)
            if status:
                for meld in other_melds:
                    melds.append(meld + [[tile, t2, t3]])
            tile_counts[tile] += 1
            tile_counts[t2] += 1
            tile_counts[t3] += 1
    return bool(melds), melds


def check_kong(p_state: PlayerStateDict, tile: Tile | None, current_player: bool) -> list[list[Tile]]:
    '''Checks if the given tile can be used by player to form a kong'''
    if not tile:
        return []
    # Check if a kong can be formed from an exposed pung
    if current_player:
        if [tile] * 3 in p_state["melds"]:
            return [[tile] * 4]
    else:
        if p_state["hand"].count(tile) == 3:
            return [[tile] * 4]
    return []


def check_pung(p_state: PlayerStateDict, tile: Tile, current_player: bool) -> list[list[Tile]]:
    '''Checks if the given tile can be used by player to form a pung'''
    if current_player:
        if p_state["hand"].count(tile) == 3:
            return [[tile] * 3]
    else:
        if p_state["hand"].count(tile) == 2:
            return [[tile] * 3]
    return []


def check_chow(p_state: PlayerStateDict, tile: Tile, current_player: bool) -> list[list[Tile]]:
    '''Checks if the given tile can be used by player to form a chow'''
    # Suit must be dots, bamboo, or characters
    if tile.suit not in Tile.suits[:3]:
        return []

    hand = p_state["hand"].copy()
    # If not current player, pretend tile is in hand
    if not current_player:
        hand.append(tile)

    possible_chows = []
    # Check if tile is in middle position of chow
    tl = Tile(tile.suit, str(int(tile.value)-1))
    tr = Tile(tile.suit, str(int(tile.value)+1))
    if tl in hand and tr in hand:
        possible_chows.append([tl, tile, tr])

    # Check if tile is in leftmost position of chow
    trr = Tile(tile.suit, str(int(tile.value)+2))
    if tr in hand and trr in hand:
        possible_chows.append([tile, tr, trr])

    # Check if tile is in rightmost position of chow
    tll = Tile(tile.suit, str(int(tile.value)-2))
    if tll in hand and tl in hand:
        possible_chows.append([tll, tl, tile])

    return possible_chows


def get_action_mask(game_state: GameStateDict, p_id: int, discarded_tile: Tile | None) -> list[int]:
    '''Given valid actions for the current state, returns an action mask'''
    mask = [0] * NUM_ACTIONS
    player_state = game_state["players"][p_id]
    player_hand = player_state["hand"]

    # Action mask for discard phase
    if game_state["phase"] == "discard":
        for tile in player_hand:
            mask[Action.DISCARD + TILE_TO_ID[tile]] = 1
        return mask

    # Action mask for meld phase
    # Can always pass
    mask[Action.PASS] = 1
    # Check for possible chows, pungs, kongs, wins
    if check_win(player_state, discarded_tile, p_id == game_state["current_player"])[0]:
        mask[Action.WIN] = 1
    for kong in check_kong(player_state, discarded_tile, p_id == game_state["current_player"]):
        tile_id = TILE_TO_ID[kong[0]]
        mask[Action.KONG + tile_id] = 1
    if discarded_tile:
        for chow in check_chow(player_state, discarded_tile, False):
            chow_id = CHOW_TO_ID[chow[0]]
            mask[Action.CHOW + chow_id] = 1  # offset by 2 for leftmost tile in chow
        for pung in check_pung(player_state, discarded_tile, False):
            tile_id = TILE_TO_ID[pung[0]]
            mask[Action.PUNG + tile_id] = 1
    return mask
