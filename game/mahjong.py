from __future__ import annotations
import typing
from game.utils import init_wall, check_win, check_kong, check_chow, check_pung
from game.player import Player


if typing.TYPE_CHECKING:
    from game.tile import Tile


NUM_PLAYERS = 4
WINDS = ["east", "south", "west", "north"]


class MahjongGame:

    def __init__(self, seed: int | None = None) -> None:
        self.wall = init_wall(seed)
        self.table = []  # discards
        self.players = [Player(i, wind=WINDS[i]) for i in range(NUM_PLAYERS)]
        self.round_wind = WINDS[0]
        self.current_player = 0  # idx into self.players
        self.first = True  # flag the very first turn
        self.discard = False  # skip drawing a tile
        self.draw = False  # indicates if the game ends in a draw
        self.done = False

        # deal 14 tiles to dealer, 13 tiles to others
        for i in range(NUM_PLAYERS):
            for _ in range(13):
                self.deal_tile(self.players[i])
        self.deal_tile(self.players[0])

    def deal_tile(self, player: Player) -> Tile:
        '''Deals a tile to player and returns the dealt tile'''
        while True:
            tile = self.wall.pop()
            if tile.suit == "flower":
                player.melds.append([tile])
                print(f"Player {player} drew {tile}, drawing replacement tile")
            else:
                player.hand.append(tile)
                return tile

    def step(self) -> None:
        '''Initiates one turn of the game'''
        # Check for draw
        if not self.wall:
            print("Draw")
            self.done = True
            self.draw = True
            return

        player = self.players[self.current_player]
        print(f"Player {player}'s turn... ")  # TODO: remove later

        # Check for heavenly hand
        if self.first:
            win_melds = check_win(player, None, True)
            if win_melds:
                opt = player.query_meld("win", win_melds)
                if opt:
                    print(f"Player {player} wins with a heavenly hand")
                    self.done = True
                    return

        # Player draws tile
        tile = None
        if not self.first and not self.discard:
            tile = self.deal_tile(player)
            print(f"Player {player} draws {tile}")

        # Check current player for win or kong
        win_melds = check_win(player, tile, True)
        if win_melds:
            opt = player.query_meld("win", win_melds)
            if opt:
                print(f"Player {player} wins")
                self.done = True
                return
        if self.first:
            self.first = False

        # Player discards tile
        print("Hand: ", end="")
        player.print_hand(True)
        print("Melds: ", end="")
        player.print_melds()
        discard_idx = int(input(f"Choose a discard (0...{len(player.hand)-1}): "))  # TODO: remove later
        discarded_tile = player.discard_tile(discard_idx, True)
        self.table.append(discarded_tile)
        print(f"Player {player} discarded {discarded_tile}")
        self.discard = False

        actions = {}
        for i in range(1, NUM_PLAYERS):
            next_player_idx = (self.current_player + i) % NUM_PLAYERS
            next_player = self.players[next_player_idx]
            actions[next_player_idx] = {
                "win": check_win(next_player, discarded_tile, False),
                "kong": check_kong(next_player, discarded_tile, False),
                "pung": check_pung(next_player, discarded_tile, False),
                "chow": check_chow(next_player, discarded_tile, False) if (i == 1) else []
            }

        # Resolve potential actions
        for action in ["win", "kong", "pung", "chow"]:
            for i in range(1, NUM_PLAYERS):
                next_player_idx = (self.current_player + i) % NUM_PLAYERS
                options = actions[next_player_idx][action]
                if options:
                    player = self.players[next_player_idx]
                    print("Hand: ", end="")
                    player.print_hand(True)
                    print("Melds: ", end="")
                    player.print_melds()
                    opt = int(player.query_meld(action, options))
                    if opt:
                        player.hand.append(self.table.pop())  # add discarded tile to player's hand
                        player.perform_meld(options[opt-1])
                        if action == "win":
                            print(f"Player {next_player_idx} wins")
                            self.done = True
                            return
                        print(f"Player {next_player_idx} has performed a {action}")
                        self.discard = True
                        self.current_player = next_player_idx
                        if action == "kong":
                            print(f"Drawing replacement tile for player {next_player_idx}")
                            self.discard = False
                        return

        self.current_player = (self.current_player + 1) % NUM_PLAYERS
        print()
