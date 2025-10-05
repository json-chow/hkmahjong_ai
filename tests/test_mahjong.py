from game.mahjong import MahjongGame


def test_init_game():
    game = MahjongGame()
    state = game.game_state
    num_hand_tiles = sum([len(state["players"][p]["hand"]) for p in state["players"]])
    num_flowers = sum([len(state["players"][p]["melds"]) for p in state["players"]])
    assert len(state["wall"]) + num_hand_tiles + num_flowers == 144
