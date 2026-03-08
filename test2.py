from game.mahjong import MahjongGame
from game.player import RandomAIPlayer
from game.utils import score_hand
from game.tile import Suit

game = MahjongGame(123)
bots = [RandomAIPlayer(i) for i in range(4)]
game.set_players(bots)

wins = []
for i in range(1000):
    game = MahjongGame()
    print(game.seed)
    bots = [RandomAIPlayer(i) for i in range(4)]
    game.set_players(bots)
    while not game.game_state["done"]:
        game.step()
