from game.mahjong import MahjongGame


def test_init_game():
    game = MahjongGame()
    num_hand_tiles = sum([len(p.hand) for p in game.players])
    num_flowers = sum([len(p.melds) for p in game.players])
    assert len(game.wall) + num_hand_tiles + num_flowers == 144
