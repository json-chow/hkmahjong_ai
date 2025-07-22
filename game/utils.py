from game.tile import Tile
from game.player import Player
import random
from collections import Counter


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
    "orphans": 7,
    "nine_gates": 10,
    # Extra based on melds
    "seat_wind": 1,
    "round_wind": 1,
    "dragon": 1,
    "mixed_orphans": 1,
    # Extra based on win condition
    "self_pick": 1,
    "concealed_hand": 1,
    "rob_kong": 1,
    "last_draw": 1,
    "win_by_kong": 1,
    "win_by_double_kong": 8,
    "heavenly_hand": 13,
    "earthly_hand": 13,
    # Extra based on flowers
    "no_flowers": 1,
    "own_flower": 1,
    "set_of_flowers": 2
}


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

    random.seed(seed)
    random.shuffle(wall)
    return wall


def precompute_wins():
    '''
    Precomputes winning tile combinations, doesn't include special combos
    Will probably stay unused since there are so many combos, faster to just use check_win()
    '''
    tile_counts = Counter(init_wall())
    # Remove flowers
    for i in range(1, 9):
        tile_counts.pop(Tile("flower", str(i)))
    # Check over all possible pairs
    combos = set()
    for tile in tile_counts:
        print(tile, len(combos))
        current_combo = [[tile]*2]
        tile_counts[tile] -= 2
        # Check through all combos via backtracking
        _precompute(current_combo, combos, tile_counts, 0)
        tile_counts[tile] += 2
    return combos


def _precompute(current: list[list[Tile]], res: set[tuple[tuple[Tile, ...], ...]], tile_counts: Counter, idx: int) -> None:
    '''Helper function for precompute_wins*()'''
    if len(current) == 5:  # 4 combos and a pair
        res.add(tuple(tuple(meld) for meld in current))
        return

    for tile_idx in range(idx, len(tile_counts)):
        tile = list(tile_counts.keys())[tile_idx]
        # Check for kongs
        if tile_counts[tile] == 4:
            tile_counts[tile] -= 4
            current.append([tile]*4)
            _precompute(current, res, tile_counts, tile_idx)
            current.pop()
            tile_counts[tile] += 4

        # Check for pungs
        if tile_counts[tile] >= 3:
            tile_counts[tile] -= 3
            current.append([tile]*3)
            _precompute(current, res, tile_counts, tile_idx)
            current.pop()
            tile_counts[tile] += 3

        # Check for chows
        if tile.suit in Tile.suits[:3] and int(tile.value) <= 7:
            t2 = Tile(tile.suit, str(int(tile.value)+1))
            t3 = Tile(tile.suit, str(int(tile.value)+2))
            if tile_counts[t2] > 0 and tile_counts[t3] > 0:
                tile_counts[tile] -= 1
                tile_counts[t2] -= 1
                tile_counts[t3] -= 1
                current.append([tile, t2, t3])
                _precompute(current, res, tile_counts, tile_idx)
                current.pop()
                tile_counts[tile] += 1
                tile_counts[t2] += 1
                tile_counts[t3] += 1


def score_hand(player: Player, state: dict) -> int:
    '''Given a player's winning hand, return the number of faan'''
    melds = player.melds
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
    for meld in melds:
        # Deal with flower 'melds'
        if meld[0].suit == "flower":
            flowers.append(meld[0])
            flower_val = int(meld[0].value)
            if flower_val >= 5:  # season
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

        # Deal with honor melds
        if meld[0].suit == "dragon":
            dragons += 1
        elif meld[0].suit == "wind":
            winds += 1
            # Round wind
            if meld[0].value == state["round_wind"]:
                score += FAAN["round_wind"]
            # Seat wind
            if meld[0].value == player.seat_wind:
                score += FAAN["seat_wind"]

    # No flowers
    if len(flowers) == 0:
        score += FAAN["no_flowers"]
    # Own flower
    pos_to_wind = {1: "east", 2: "south", 3: "west", 4: "north"}
    for flower in flowers:
        if pos_to_wind[((int(flower.value) - 1) % 4) + 1] == player.seat_wind:
            score += FAAN["own_flower"]
    # All flower or season tiles
    if all(all_flowers):
        score += FAAN["set_of_flowers"]
    if all(all_seasons):
        score += FAAN["set_of_flowers"]

    # Win conditions -- self pick, win by kong, etc.
    for win_condition in state["win_condition"]:
        score += FAAN[win_condition]

    # Special hands (13 orphans, 9 gates, ...)
    if state["thirteen_orphans"]:
        return score + FAAN["thirteen_orphans"]
    if state["nine_gates"]:
        return score + FAAN["nine_gates"]

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
        elif (dragons == 2) and (pair.suit == "dragon"):
            score += FAAN["small_dragons"]

        # Great winds
        if winds == 4:
            score += FAAN["great_winds"]
        # Small winds
        elif (winds == 3) and (pair.suit == "wind"):
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
    return score


def check_win(player: Player, tile: Tile | None, current_player: bool) -> list[list[list[Tile]]]:
    '''Checks if the player has either a self-draw win or a win by discard'''
    # Count number of tiles in current hand
    tile_counts = Counter(player.hand)

    # Check for win by discard -- check if tile can be used to win
    if not current_player:
        tile_counts[tile] += 1
    # ... otherwise, check for self-draw win -- check if current hand is a win

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
    # Check for thirteen orphans
    return possible_wins


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
            melds.append(other_melds + [tile]*4)
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


def check_kong(player: Player, tile: Tile, current_player: bool) -> list[list[Tile]]:
    '''Checks if the given tile can be used by player to form a kong'''
    # Check if a kong can be formed from an exposed pung
    if current_player:
        if [tile] * 3 in player.melds:
            return [[tile] * 4]
        # Check if a kong can be formed from a concealed pung
        if player.hand.count(tile) == 4:
            return [[tile] * 4]
    else:
        if player.hand.count(tile) == 3:
            return [[tile] * 4]
    return []


def check_pung(player: Player, tile: Tile, current_player: bool) -> list[list[Tile]]:
    '''Checks if the given tile can be used by player to form a pung'''
    if current_player:
        if player.hand.count(tile) == 3:
            return [[tile] * 3]
    else:
        if player.hand.count(tile) == 2:
            return [[tile] * 3]
    return []


def check_chow(player: Player, tile: Tile, current_player: bool) -> list[list[Tile]]:
    '''Checks if the given tile can be used by player to form a chow'''
    # Suit must be dots, bamboo, or characters
    if tile.suit not in Tile.suits[:3]:
        return []

    hand = player.hand.copy()
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
