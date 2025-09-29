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
        self.kong = False  # for tracking win by kong, indicates if a replacement tile is to be drawn due to a kong
        self.double_kong = False  # for tracking win by double kong
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
                self.kong = True  # potential for win by kong
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
            win_melds, state = check_win(player, None, True)
            if win_melds:
                opt = player.query_meld("win", win_melds)
                if opt:
                    print(f"Player {player} wins with a heavenly hand")
                    state["round_wind"] = self.round_wind
                    state["win_condition"].append("heavenly_hand")
                    self.done = True
                    return

        # Player draws tile
        tile = None
        if not self.first and not self.discard:
            tile = self.deal_tile(player)
            print(f"Player {player} draws {tile}")

        # Check current player for win (self draw win)
        win_melds, state = check_win(player, tile, True)
        if win_melds:
            opt = player.query_meld("win", win_melds)
            if opt:
                print(f"Player {player} wins")
                state["round_wind"] = self.round_wind
                if not self.wall:
                    state["win_condition"].append("last_draw")
                if self.kong:
                    if self.double_kong:
                        state["win_condition"].append("win_by_double_kong")
                    else:
                        state["win_condition"].append("win_by_kong")
                self.done = True
                return
        # Check current player for kong (from exposed pung)
        kong_meld = check_kong(player, tile, True)
        if kong_meld:
            opt = player.query_meld("kong", kong_meld)
            if opt:
                # Check if other players can rob the kong
                for i in range(1, NUM_PLAYERS):
                    next_player_idx = (self.current_player + i) % NUM_PLAYERS
                    next_player = self.players[next_player_idx]
                    rob_kong_meld, state = check_win(next_player, tile, False)
                    if rob_kong_meld:
                        rob_kong_opt = next_player.query_meld("win", rob_kong_meld)
                        if rob_kong_opt:
                            print(f"Player {next_player_idx} wins")
                            state["round_wind"] = self.round_wind
                            state["win_condition"].append("rob_kong")
                            if not self.wall:
                                state["win_condition"].append("last_draw")
                            self.done = True
                            return
                # Otherwise, draw replacement tile
                player.perform_meld(kong_meld)
                print(f"Drawing replacement tile for player {player.id}")
                self.discard = False
                self.kong = True
                return

        # Player discards tile
        print("Hand: ", end="")
        player.print_hand(True)
        print("Melds: ", end="")
        player.print_melds()
        discard_idx = int(input(f"Choose a discard (0...{len(player.hand)-1}): "))  # decision point: what to discard?
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
                if action == "win":
                    options, state = actions[next_player_idx][action]
                else:
                    options = actions[next_player_idx][action]
                if options:
                    player = self.players[next_player_idx]
                    print("Hand: ", end="")
                    player.print_hand(True)
                    print("Melds: ", end="")
                    player.print_melds()
                    opt = int(player.query_meld(action, options))  # decision point: what meld to perform?
                    if opt:
                        player.hand.append(self.table.pop())  # add discarded tile to player's hand
                        player.perform_meld(options[opt-1])
                        if action == "win":
                            print(f"Player {next_player_idx} wins")
                            state["round_wind"] = self.round_wind
                            if not self.wall:
                                state["win_condition"].append("last_draw")
                            if self.first:
                                state["win_condition"].append("earthly_hand")
                            self.done = True
                            return
                        print(f"Player {next_player_idx} has performed a {action}")
                        self.discard = True
                        self.current_player = next_player_idx
                        if action == "kong":
                            print(f"Drawing replacement tile for player {next_player_idx}")
                            self.discard = False
                            if self.kong:  # already had a kong this turn
                                self.double_kong = True
                            self.kong = True
                            return
                        self.kong = False
                        self.double_kong = False
                        if self.first:
                            self.first = False
                        return
        self.kong = False
        self.double_kong = False
        if self.first:
            self.first = False
        self.current_player = (self.current_player + 1) % NUM_PLAYERS
        print()
