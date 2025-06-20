from game.tile import Tile
import random
from collections import Counter


def init_wall(seed=None):
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
    flowers = []
    for value in Tile.values[:4]:
        tile = Tile("flower", value)
        flowers.append(tile)
    wall.extend(flowers * 2)

    random.seed(seed)
    random.shuffle(wall)
    return wall


def check_win(player, tile, current_player: bool) -> list[list[list[Tile]]]:
    '''Checks if the player has either a self-draw win or a win by discard'''
    # TODO: probably just precompute all winning hands, shouldn't be that many
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
    return possible_wins


def _check_meld(tile_counts) -> tuple[bool, list[list[list[Tile]]]]:
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
    if tile.suit in Tile.suits[:3]:
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


def check_kong(player, tile, current_player: bool) -> list[list[Tile]]:
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


def check_pung(player, tile, current_player: bool) -> list[list[Tile]]:
    '''Checks if the given tile can be used by player to form a pung'''
    if current_player:
        if player.hand.count(tile) == 3:
            return [[tile] * 3]
    else:
        if player.hand.count(tile) == 2:
            return [[tile] * 3]
    return []


def check_chow(player, tile, current_player: bool) -> list[list[Tile]]:
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
