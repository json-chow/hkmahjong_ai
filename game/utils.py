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


def check_win(player, tile, current_player: bool):
    '''Checks if the player has either a self-draw win or a win by discard'''
    # TODO: probably just precompute all winning hands, shouldn't be that many
    # Count number of tiles in current hand
    tile_counts = Counter(player.hand)

    # Check for win by discard -- check if tile can be used to win
    if not current_player:
        tile_counts[tile] += 1
    # ... otherwise, check for self-draw win -- check if current hand is a win

    for tile in tile_counts:
        # Check over all possible pairs
        if tile_counts[tile] >= 2:
            tile_counts[tile] -= 2
            if _check_meld(tile_counts):
                return True
            tile_counts[tile] += 2
    return False


def _check_meld(tile_counts):
    '''Checks if melds can be formed using all tiles in a hand'''
    if tile_counts.total() == 0:
        return True

    # Get tile with a non-zero count
    for tile in tile_counts:
        if tile_counts[tile] > 0:
            break

    # Check for kongs
    if tile_counts[tile] == 4:
        tile_counts[tile] -= 4
        if _check_meld(tile_counts):
            return True
        tile_counts[tile] += 4

    # Check for pungs
    if tile_counts[tile] >= 3:
        tile_counts[tile] -= 3
        if _check_meld(tile_counts):
            return True
        tile_counts[tile] += 3

    # Check for chows
    if tile.suit in Tile.suits[:3]:
        t2 = Tile(tile.suit, str(int(tile.value)+1))
        t3 = Tile(tile.suit, str(int(tile.value)+2))
        if tile_counts[t2] > 0 and tile_counts[t3] > 0:
            tile_counts[tile] -= 1
            tile_counts[t2] -= 1
            tile_counts[t3] -= 1
            if _check_meld(tile_counts):
                return True
            tile_counts[tile] += 1
            tile_counts[t2] += 1
            tile_counts[t3] += 1
    return False


def check_kong(player, tile, current_player: bool):
    '''Checks if the given tile can be used by player to form a kong'''
    # Check if a kong can be formed from an exposed pung
    if current_player:
        if [tile] * 3 in player.melds:
            return True
        # Check if a kong can be formed from a concealed pung
        if player.hand.count(tile) == 4:
            return True
    else:
        if player.hand.count(tile) == 3:
            return True
    return False


def check_pung(player, tile, current_player: bool):
    '''Checks if the given tile can be used by player to form a pung'''
    if current_player:
        if player.hand.count(tile) == 3:
            return True
    else:
        if player.hand.count(tile) == 2:
            return True
    return False


def check_chow(player, tile, current_player: bool):
    '''Checks if the given tile can be used by player to form a chow'''
    # Suit must be dots, bamboo, or characters
    if tile.suit not in Tile.suits[:3]:
        return False

    # If not current player, pretend tile is in hand
    if not current_player:
        player.hand.append(tile)

    # Check if tile is in middle position of chow
    tl = Tile(tile.suit, str(int(tile.value)-1))
    tr = Tile(tile.suit, str(int(tile.value)+1))
    if tl in player.hand and tr in player.hand:
        if not current_player:
            player.hand.pop()
        return True

    # Check if tile is in leftmost position of chow
    trr = Tile(tile.suit, str(int(tile.value)+2))
    if tr in player.hand and trr in player.hand:
        if not current_player:
            player.hand.pop()
        return True

    # Check if tile is in rightmost position of chow
    tll = Tile(tile.suit, str(int(tile.value)-2))
    if tll in player.hand and tl in player.hand:
        if not current_player:
            player.hand.pop()
        return True

    if not current_player:
        player.hand.pop()
    return False
