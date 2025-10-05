from __future__ import annotations
from typing import TYPE_CHECKING
from game.utils import init_wall, check_win, check_kong, check_chow, check_pung, GameStateDict
from game.player import Player, HumanPlayer


if TYPE_CHECKING:
    from game.tile import Tile


NUM_PLAYERS = 4
WINDS = ["east", "south", "west", "north"]


class MahjongGame:
    table: list[Tile]
    players: list[Player]

    def __init__(self, seed: int | None = None) -> None:
        self.seed = seed
        self.players = [HumanPlayer(i) for i in range(NUM_PLAYERS)]
        self.init_game()

    def set_players(self, players: list[Player]) -> None:
        '''Set the players of the game'''
        if len(players) != NUM_PLAYERS:
            raise ValueError(f"Number of players must be {NUM_PLAYERS}")
        self.players = players
        self.init_game()

    def init_game(self) -> None:
        self.game_state: GameStateDict = {
            "wall": [],
            "round_wind": WINDS[0],
            "current_player": 0,  # idx into self.players
            "first": True,  # flag the very first turn
            "discard": False,  # skip drawing a tile
            "kong": False,  # for tracking win by kong, indicates if a replacement tile is to be drawn due to a kong
            "double_kong": False,  # for tracking win by double kong
            "draw": False,  # indicates if the game ends in a draw
            "done": False,
            "players": {
                i: {
                    "id": i,
                    "seat_wind": WINDS[i],
                    "hand": [],
                    "melds": [],
                    "discards": []
                } for i in range(NUM_PLAYERS)
            }
        }
        self.game_state["wall"] = init_wall()

        # deal 14 tiles to dealer, 13 tiles to others
        for i in range(NUM_PLAYERS):
            for _ in range(13):
                self.deal_tile(i)
        self.deal_tile(0)

    def deal_tile(self, p_id: int) -> Tile | None:
        '''Deals a tile to player and returns the dealt tile'''
        player_state = self.game_state["players"][p_id]
        while self.game_state["wall"]:
            tile = self.game_state["wall"].pop()
            if tile.suit == "flower":
                player_state["melds"].append([tile])
                print(f"Player {p_id} drew {tile}, drawing replacement tile")
                self.game_state["kong"] = True  # potential for win by kong
            else:
                player_state["hand"].append(tile)
                return tile

    def step(self) -> None:
        '''Initiates one turn of the game'''
        # Check for draw
        if not self.game_state["wall"]:
            print("Draw")
            self.game_state["done"] = True
            self.game_state["draw"] = True
            return

        p_id = self.game_state["current_player"]
        player = self.players[p_id]
        player_state = self.game_state["players"][p_id]

        # Check for heavenly hand
        if self.game_state["first"]:
            win_melds, state = check_win(player_state, None, True)
            if win_melds:
                opt = player.query_meld(self.game_state, "win", win_melds)
                if opt:
                    print(f"Player {p_id} wins with a heavenly hand")
                    state["round_wind"] = self.game_state["round_wind"]
                    state["win_condition"].append("heavenly_hand")
                    self.game_state["done"] = True
                    return

        # Player draws tile
        tile = None
        if not self.game_state["first"] and not self.game_state["discard"]:
            tile = self.deal_tile(p_id)
            print(f"Player {p_id} draws {tile}")

        # Check current player for win (self draw win)
        win_melds, state = check_win(player_state, tile, True)
        if win_melds:
            opt = player.query_meld(self.game_state, "win", win_melds)
            if opt:
                print(f"Player {p_id} wins")
                state["round_wind"] = self.game_state["round_wind"]
                if not self.game_state["wall"]:
                    state["win_condition"].append("last_draw")
                if self.game_state["kong"]:
                    if self.game_state["double_kong"]:
                        state["win_condition"].append("win_by_double_kong")
                    else:
                        state["win_condition"].append("win_by_kong")
                self.game_state["done"] = True
                return
        # Check current player for kong (from exposed pung)
        kong_meld = check_kong(player_state, tile, True)
        if kong_meld:
            opt = player.query_meld(self.game_state, "kong", kong_meld)
            if opt:
                # Check if other players can rob the kong
                for i in range(1, NUM_PLAYERS):
                    next_player_idx = (p_id + i) % NUM_PLAYERS
                    next_player = self.players[next_player_idx]
                    next_player_state = self.game_state["players"][next_player_idx]
                    rob_kong_meld, state = check_win(next_player_state, tile, False)
                    if rob_kong_meld:
                        rob_kong_opt = next_player.query_meld(self.game_state, "win", rob_kong_meld)
                        if rob_kong_opt:
                            print(f"Player {next_player_idx} wins")
                            state["round_wind"] = self.game_state["round_wind"]
                            state["win_condition"].append("rob_kong")
                            if not self.game_state["wall"]:
                                state["win_condition"].append("last_draw")
                            self.game_state["done"] = True
                            return
                # Otherwise, draw replacement tile
                print(kong_meld[opt-1])
                self.perform_meld(p_id, kong_meld[opt-1])
                print(f"Drawing replacement tile for player {p_id}")
                self.game_state["discard"] = False
                self.game_state["kong"] = True
                return

        # Player discards tile
        self.print_player_info(p_id)
        discard_idx = player.query_discard(self.game_state, True)  # decision point: what to discard?
        discarded_tile = player_state["hand"].pop(discard_idx)
        player_state["discards"].append(discarded_tile)
        print(f"Player {p_id} discarded {discarded_tile}")
        self.game_state["discard"] = False

        # Resolve potential actions from other players
        for i in range(1, NUM_PLAYERS):
            next_player_idx = (p_id + i) % NUM_PLAYERS
            next_player = self.players[next_player_idx]
            next_player_state = self.game_state["players"][next_player_idx]

            # Check for wins
            win_melds, state = check_win(next_player_state, discarded_tile, False)
            if win_melds:
                opt = next_player.query_meld(self.game_state, "win", win_melds)  # decision point: whether to win
                if opt:
                    print(f"Player {next_player_idx} wins")
                    state["round_wind"] = self.game_state["round_wind"]
                    state["win_condition"].append("win_by_discard")
                    if not self.game_state["wall"]:
                        state["win_condition"].append("last_draw")
                    self.game_state["done"] = True
                    return

            # Check for kongs
            kong_meld = check_kong(next_player_state, discarded_tile, False)
            if kong_meld:
                opt = next_player.query_meld(self.game_state, "kong", kong_meld)  # decision point: whether to kong
                if opt:
                    next_player_state["hand"].append(player_state["discards"].pop())  # add discarded tile to hand
                    self.perform_meld(next_player_idx, kong_meld[opt-1])
                    print(f"Player {next_player_idx} has performed a kong")
                    self.game_state["discard"] = True
                    self.game_state["current_player"] = next_player_idx
                    print(f"Drawing replacement tile for player {next_player_idx}")
                    self.game_state["discard"] = False
                    if self.game_state["kong"]:  # already had a kong this turn
                        self.game_state["double_kong"] = True
                    self.game_state["kong"] = True
                    return

            # Check for pungs
            pung_meld = check_pung(next_player_state, discarded_tile, False)
            if pung_meld:
                opt = next_player.query_meld(self.game_state, "pung", pung_meld)  # decision point: whether to pung
                if opt:
                    next_player_state["hand"].append(player_state["discards"].pop())
                    self.perform_meld(next_player_idx, pung_meld[opt-1])
                    print(f"Player {next_player_idx} has performed a pung")
                    self.game_state["discard"] = True
                    self.game_state["current_player"] = next_player_idx
                    self.game_state["kong"] = False
                    self.game_state["double_kong"] = False
                    if self.game_state["first"]:
                        self.game_state["first"] = False
                    return

            # Check for chows (only next player can chow)
            if i == 1:
                chow_meld = check_chow(next_player_state, discarded_tile, False)
                if chow_meld:
                    opt = next_player.query_meld(self.game_state, "chow", chow_meld)  # decision point: whether to chow
                    if opt:
                        next_player_state["hand"].append(player_state["discards"].pop())
                        self.perform_meld(next_player_idx, chow_meld[opt-1])
                        print(f"Player {next_player_idx} has performed a chow")
                        self.game_state["discard"] = True
                        self.game_state["current_player"] = next_player_idx
                        self.game_state["kong"] = False
                        self.game_state["double_kong"] = False
                        if self.game_state["first"]:
                            self.game_state["first"] = False
                        return

        self.game_state["kong"] = False
        self.game_state["double_kong"] = False
        if self.game_state["first"]:
            self.game_state["first"] = False
        self.game_state["current_player"] = (p_id + 1) % NUM_PLAYERS
        print()

    def perform_meld(self, p_id: int, to_meld: list[Tile]) -> None:
        player_state = self.game_state["players"][p_id]
        # handle exposed pung --> kong
        if len(to_meld) == 4:
            tile = to_meld[0]
            for meld in player_state["melds"]:
                if len(meld) == 3 and meld[0] == tile:
                    player_state["hand"].remove(tile)
                    meld.append(tile)
                    return
        # all other melds
        for tile in to_meld:
            player_state["hand"].remove(tile)
        player_state["melds"].append(to_meld)

    def print_player_info(self, p_id: int, sort_hand: bool = False) -> None:
        p_state = self.game_state["players"][p_id]
        if sort_hand:
            print(", ".join(str(tile) for tile in sorted(p_state["hand"])))
        else:
            print(", ".join(str(tile) for tile in p_state["hand"]))

        print(f"Melds: {p_state['melds']}")
