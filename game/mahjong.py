from game.utils import init_wall, check_win, check_kong, check_chow, check_pung
from game.player import Player


NUM_PLAYERS = 4
WINDS = ["E", "S", "W", "N"]


class MahjongGame:

    def __init__(self, seed=None):
        self.wall = init_wall(seed)
        self.table = []  # discards
        self.players = [Player(i, wind=WINDS[i]) for i in range(NUM_PLAYERS)]
        self.round_wind = WINDS[0]
        self.current_player = 0  # idx into self.players
        self.first = True  # flag the very first turn

        # deal 14 tiles to dealer, 13 tiles to others
        for i in range(NUM_PLAYERS):
            for _ in range(13):
                self.deal_tile(self.players[i])
        self.deal_tile(self.players[0])

    def deal_tile(self, player):
        '''Deals a tile to player and returns the dealt tile'''
        while True:
            tile = self.wall.pop()
            if tile.suit == "flower":
                player.melds.append([tile])
                print(f"Player {player} drew {tile}, drawing replacement tile")
            else:
                player.hand.append(tile)
                return tile

    def step(self):
        '''Initiates one turn of the game'''
        player = self.players[self.current_player]
        print(f"Player {player}'s turn... ")  # TODO: remove later

        # TODO: check for heavenly hand

        # Player draws tile
        if not self.first:
            tile = self.deal_tile(player)
            print(f"Player {player} draws {tile}")

        # Check current player for win or kong
        if check_win(player, tile, True):
            print(f"Player {player} wins")
            return
        if not self.first:
            if check_kong(player, tile, True):
                # TODO: tile replacement on kong
                pass
        else:
            self.first = False

        # Player discards tile
        player.print_hand(True)
        discard_idx = int(input())  # TODO: remove later
        discarded_tile = player.discard_tile(discard_idx, True)
        self.table.append(discarded_tile)
        print(f"Player {player} discarded {discarded_tile}")

        # TODO: Check other players for pung, chow, kong, win
        actions = {}
        for i in range(1, NUM_PLAYERS+1):
            next_player = self.players[(self.current_player + 1) % NUM_PLAYERS]
            c, p, k, w = False, False, False, False
            if (i == 1):
                c = check_chow(next_player, discarded_tile, False)
            p = check_pung(next_player, discarded_tile, False)
            k = check_kong(next_player, discarded_tile, False)
            w = check_win(next_player, discarded_tile, False)
            actions[next_player] = (c, p, k, w)

        # Check for draw
        if not self.wall:
            print("Draw")
            return

        self.current_player = (self.current_player + 1) % NUM_PLAYERS
        print()
