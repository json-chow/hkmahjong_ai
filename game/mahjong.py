from __future__ import annotations
import typing
from game.utils import init_wall, check_win, check_kong, check_chow, check_pung
from game.player import Player, HumanPlayer


if typing.TYPE_CHECKING:
    from game.tile import Tile


NUM_PLAYERS = 4
WINDS = ["east", "south", "west", "north"]


class MahjongGame:
    table: list[Tile]
    players: list[Player]

    def __init__(self, seed: int | None = None) -> None:
        self.wall = init_wall(seed)
        self.table = []  # discards
        self.players = [HumanPlayer(i, wind=WINDS[i]) for i in range(NUM_PLAYERS)]
        self.init_game()

    def set_players(self, players: list[Player]) -> None:
        '''Set the players of the game'''
        if len(players) != NUM_PLAYERS:
            raise ValueError(f"Number of players must be {NUM_PLAYERS}")
        self.players = players
        for i in range(NUM_PLAYERS):
            self.players[i].seat_wind = WINDS[i]
        self.init_game()

    def init_game(self) -> None:
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
                print(f"Player {player.id} drew {tile}, drawing replacement tile")
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

        # Check for heavenly hand
        if self.first:
            win_melds, state = check_win(player, None, True)
            if win_melds:
                opt = player.query_meld("win", win_melds)
                if opt:
                    print(f"Player {player.id} wins with a heavenly hand")
                    state["round_wind"] = self.round_wind
                    state["win_condition"].append("heavenly_hand")
                    self.done = True
                    return

        # Player draws tile
        tile = None
        if not self.first and not self.discard:
            tile = self.deal_tile(player)
            print(f"Player {player.id} draws {tile}")

        # Check current player for win (self draw win)
        win_melds, state = check_win(player, tile, True)
        if win_melds:
            opt = player.query_meld("win", win_melds)
            if opt:
                print(f"Player {player.id} wins")
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
                player.perform_meld(kong_meld[opt-1])
                print(f"Drawing replacement tile for player {player.id}")
                self.discard = False
                self.kong = True
                return

        # Player discards tile
        print(player)
        discarded_tile = player.query_discard(True)  # decision point: what to discard?
        self.table.append(discarded_tile)
        print(f"Player {player.id} discarded {discarded_tile}")
        self.discard = False

        # Resolve potential actions from other players
        for i in range(1, NUM_PLAYERS):
            next_player_idx = (self.current_player + i) % NUM_PLAYERS
            next_player = self.players[next_player_idx]

            # Check for wins
            win_melds, state = check_win(next_player, discarded_tile, False)
            if win_melds:
                opt = next_player.query_meld("win", win_melds)  # decision point: whether to win
                if opt:
                    print(f"Player {next_player_idx} wins")
                    state["round_wind"] = self.round_wind
                    state["win_condition"].append("win_by_discard")
                    if not self.wall:
                        state["win_condition"].append("last_draw")
                    self.done = True
                    return

            # Check for kongs
            kong_meld = check_kong(next_player, discarded_tile, False)
            if kong_meld:
                opt = next_player.query_meld("kong", kong_meld)  # decision point: whether to kong
                if opt:
                    next_player.hand.append(self.table.pop())  # add discarded tile to player's hand
                    next_player.perform_meld(kong_meld[opt-1])
                    print(f"Player {next_player_idx} has performed a kong")
                    self.discard = True
                    self.current_player = next_player_idx
                    print(f"Drawing replacement tile for player {next_player_idx}")
                    self.discard = False
                    if self.kong:  # already had a kong this turn
                        self.double_kong = True
                    self.kong = True
                    return

            # Check for pungs
            pung_meld = check_pung(next_player, discarded_tile, False)
            if pung_meld:
                opt = next_player.query_meld("pung", pung_meld)  # decision point: whether to pung
                if opt:
                    next_player.hand.append(self.table.pop())
                    next_player.perform_meld(pung_meld[opt-1])
                    print(f"Player {next_player_idx} has performed a pung")
                    self.discard = True
                    self.current_player = next_player_idx
                    self.kong = False
                    self.double_kong = False
                    if self.first:
                        self.first = False
                    return

            # Check for chows (only next player can chow)
            if i == 1:
                chow_meld = check_chow(next_player, discarded_tile, False)
                if chow_meld:
                    opt = next_player.query_meld("chow", chow_meld)  # decision point: whether to chow
                    if opt:
                        next_player.hand.append(self.table.pop())
                        next_player.perform_meld(chow_meld[opt-1])
                        print(f"Player {next_player_idx} has performed a chow")
                        self.discard = True
                        self.current_player = next_player_idx
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
