from game.mahjong import MahjongGame
from game.player import RandomAIPlayer
from game.tile import Tile
from game.utils import check_win, get_action_mask
from game.constants import TILE_TO_ID

# SEED = 342
# # g = MahjongGame(SEED)
# g = MahjongGame()
# g.set_players([RandomAIPlayer(i, SEED) for i in range(4)])
# while not g.game_state["done"]:
#     g.step()

# game = MahjongGame()
# game.set_players([RandomAIPlayer(i) for i in range(4)])
# t1 = Tile("bamboo", "1")
# t2 = Tile("bamboo", "2")
# t3 = Tile("bamboo", "4")
# t4 = Tile("dragon", "red")
# t5 = Tile("wind", "west")
# game.game_state["players"][0]["hand"] = [t1, t2, t3] * 3 + [t4] + [t5]
# game.game_state["players"][0]["melds"] = [[t4]*3]
# game.check_current_player_options(0, t4)
# print(game.game_state)
# print(check_win(game.game_state["players"][0], None, True))

t1 = Tile("bamboo", "2")
t2 = Tile("bamboo", "3")
t3 = Tile("bamboo", "4")
t4 = Tile("bamboo", "5")
t5 = Tile("wind", "west")
p0_state = {
    "id": 0,
    "seat_wind": "east",
    "hand": [t1, t1, t1, t2, t2, t3, t3, t4, t4, t5, t5, t5, t5],
    "melds": [],
    "discards": []
}
game_state = {
    "players": {
        0: p0_state
    },
    "wall": [],
    "round_wind": "east",
    "current_player": 0,  # idx into self.players
    "first": False,  # flag the very first turn
    "discard": False,  # skip drawing a tile
    "kong": False,  # for tracking win by kong, indicates if a replacement tile is to be drawn due to a kong
    "double_kong": False,  # for tracking win by double kong
    "draw": False,  # indicates if the game ends in a draw
    "done": False,
    "winning_hand_state": None,
    "phase": "meld",  # game phase -- "meld", "discard", informs action mask generation
}
mask = get_action_mask(game_state, 0, t4)
print(mask)
