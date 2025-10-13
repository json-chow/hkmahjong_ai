from game.mahjong import MahjongGame
from game.player import HumanPlayer, RandomAIPlayer
from game.tile import Tile


def test_init_game():
    game = MahjongGame()
    state = game.game_state
    num_hand_tiles = sum([len(state["players"][p]["hand"]) for p in state["players"]])
    num_flowers = sum([len(state["players"][p]["melds"]) for p in state["players"]])
    assert len(state["wall"]) + num_hand_tiles + num_flowers == 144


def test_game_draw():
    game = MahjongGame()
    game.set_players([HumanPlayer(i) for i in range(4)])
    game.game_state["wall"] = []
    assert game.check_game_draw() is True


def test_check_heavenly_hand():
    game = MahjongGame()
    game.set_players([RandomAIPlayer(i) for i in range(4)])
    t1 = Tile("bamboo", "1")
    t2 = Tile("bamboo", "2")
    t3 = Tile("bamboo", "3")
    t4 = Tile("dragon", "red")
    t5 = Tile("wind", "west")
    game.game_state["players"][0]["hand"] = [t1, t2, t3] * 3 + [t4] * 3 + [t5] * 2
    game.step()
    assert game.game_state["winning_hand_state"] is not None
    assert "heavenly_hand" in game.game_state["winning_hand_state"]["win_condition"]


def test_check_earthly_hand():
    game = MahjongGame()
    game.set_players([RandomAIPlayer(i) for i in range(4)])
    t1 = Tile("bamboo", "1")
    t2 = Tile("bamboo", "2")
    t3 = Tile("bamboo", "3")
    t4 = Tile("dragon", "red")
    t5 = Tile("wind", "west")
    game.game_state["players"][1]["hand"] = [t1, t2, t3] * 3 + [t4] * 3 + [t5]
    game.game_state["players"][0]["discards"] = [Tile("wind", "west")]
    game.resolve_other_actions(t5, 0)
    assert game.game_state["winning_hand_state"] is not None
    assert "earthly_hand" in game.game_state["winning_hand_state"]["win_condition"]


def test_deal_tile():
    game = MahjongGame()
    game.set_players([RandomAIPlayer(i) for i in range(4)])
    tile = Tile("dot", "1")
    game.game_state["players"][0]["hand"] = []
    game.game_state["wall"] = [tile]
    game.deal_tile(0)
    assert tile in game.game_state["players"][0]["hand"]
    assert len(game.game_state["wall"]) == 0
