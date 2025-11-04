from __future__ import annotations
from typing import TYPE_CHECKING
from game.utils import init_wall, check_win, check_kong, check_chow, check_pung, score_hand, GameStateDict
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
            "winning_hand_state": None,
            "phase": "meld",  # game phase -- "meld", "discard", informs action mask generation
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
        self.game_state["wall"] = init_wall(self.seed)

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
        return None

    def step(self) -> None:
        '''
        Initiates one turn of the game
        tile draw, (meld forming), discard, (meld forming for others)
        meld forming leads to another turn for that player where they will then discard
        '''
        if self.check_game_draw():
            return

        p_id = self.game_state["current_player"]

        if self.check_heavenly_hand(p_id):
            return

        tile = self.deal_tile_step(p_id)

        if self.check_current_player_options(p_id, tile):
            return

        discarded_tile = self.discard_tile_step(p_id)

        if self.resolve_other_actions(discarded_tile, p_id):  # don't want to change current player if action taken
            return

        self.prepare_next_turn(p_id)

    def check_game_draw(self) -> bool:
        if not self.game_state["wall"]:
            print("Draw")
            self.game_state["done"] = True
            self.game_state["draw"] = True
            return True
        return False

    def check_heavenly_hand(self, p_id: int) -> bool:
        player = self.players[p_id]
        player_state = self.game_state["players"][p_id]

        if self.game_state["first"]:
            win_melds, state = check_win(player_state, None, True)
            if not win_melds:
                return False
            options = {
                "win": win_melds
            }
            _, meld = player.query_meld(self.game_state, options)
            if meld:
                print(f"Player {p_id} wins with a heavenly hand")
                state["round_wind"] = self.game_state["round_wind"]
                state["win_condition"].append("heavenly_hand")
                self.game_state["done"] = True
                self.game_state["winning_hand_state"] = state
                return True
        return False

    def deal_tile_step(self, p_id: int) -> Tile | None:
        tile = None
        if not self.game_state["first"] and not self.game_state["discard"]:
            tile = self.deal_tile(p_id)
            print(f"Player {p_id} draws {tile}")
        return tile

    def resolve_kong(self, p_id: int, next_p_id: int, meld: list[Tile]) -> None:
        player_state = self.game_state["players"][p_id]
        next_player_state = self.game_state["players"][next_p_id]

        tile = meld[0]
        # Check if other players can rob the kong
        if (p_id != next_p_id):
            # only if it's from an exposed pung
            if ([tile] * 3 in next_player_state["melds"]) and self.check_rob_kong(tile, next_p_id):
                if self.check_rob_kong(tile, next_p_id):
                    return
            # add discarded tile to hand
            next_player_state["hand"].append(player_state["discards"].pop())
        elif tile is not None:
            # add drawn tile to hand
            next_player_state["hand"].append(tile)

        self.set_draw_replacement_after_kong(next_p_id)

    def check_current_player_options(self, p_id: int, tile: Tile | None) -> bool:
        player = self.players[p_id]
        player_state = self.game_state["players"][p_id]

        # Check current player for win (self draw win)
        win_melds, state = check_win(player_state, tile, True)
        options = {
            "win": win_melds,
            "kong": check_kong(player_state, tile, True),
        }
        if not any(options.values()):
            return False  # no options available
        action, meld = player.query_meld(self.game_state, options)
        if action == "win":
            if meld:
                self.perform_win(p_id, meld)
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
                self.game_state["winning_hand_state"] = state
                print("Winning hand: ", player_state["melds"])
                print("Winning hand state: ", state)
                print("Winning hand score: ", score_hand(player_state["melds"], state))
                return True

        # Check current player for kong (from exposed pung)
        if action == "kong":
            self.resolve_kong(p_id, p_id, meld)
            return True
        return False

    def check_rob_kong(self, discarded_tile: Tile | None, p_id: int) -> bool:
        '''Check if any other player can rob the kong of player p_id'''
        for i in range(1, NUM_PLAYERS):
            next_player_idx = (p_id + i) % NUM_PLAYERS
            next_player = self.players[next_player_idx]
            next_player_state = self.game_state["players"][next_player_idx]
            rob_kong_meld, state = check_win(next_player_state, discarded_tile, False)
            options = {
                "win": rob_kong_meld
            }
            _, meld = next_player.query_meld(self.game_state, options)
            if meld:
                self.perform_single_meld(next_player_idx, meld)
                print(f"Player {next_player_idx} wins")
                state["round_wind"] = self.game_state["round_wind"]
                state["win_condition"].append("rob_kong")
                if not self.game_state["wall"]:
                    state["win_condition"].append("last_draw")
                self.game_state["done"] = True
                self.game_state["winning_hand_state"] = state
                return True
        return False

    def set_draw_replacement_after_kong(self, p_id) -> None:
        '''Set the game state to draw a replacement tile after a kong for player p_id'''
        self.game_state["current_player"] = p_id
        if self.game_state["kong"]:  # already had a kong this turn
            self.game_state["double_kong"] = True
        print(f"Drawing replacement tile for player {p_id}")
        self.game_state["discard"] = False
        self.game_state["kong"] = True

    def discard_tile_step(self, p_id: int) -> Tile:
        player = self.players[p_id]
        player_state = self.game_state["players"][p_id]
        self.game_state["phase"] = "discard"

        self.print_player_info(p_id)
        discard_idx = player.query_discard(self.game_state, False)  # decision point: what to discard?
        discarded_tile = player_state["hand"].pop(discard_idx)
        player_state["discards"].append(discarded_tile)
        print(f"Player {p_id} discarded {discarded_tile}")
        self.game_state["discard"] = False
        self.game_state["phase"] = "meld"
        return discarded_tile

    def resolve_other_actions(self, discarded_tile: Tile, p_id: int) -> bool:
        player_state = self.game_state["players"][p_id]
        # Get potential actions for other players
        player_actions = {}
        for i in range(1, NUM_PLAYERS):
            next_player_idx = (p_id + i) % NUM_PLAYERS
            next_player = self.players[next_player_idx]
            next_player_state = self.game_state["players"][next_player_idx]

            win_melds, state = check_win(next_player_state, discarded_tile, False)
            kong_meld = check_kong(next_player_state, discarded_tile, False)
            pung_meld = check_pung(next_player_state, discarded_tile, False)
            chow_meld = check_chow(next_player_state, discarded_tile, False) if i == 1 else []

            options = {
                "win": win_melds,
                "kong": kong_meld,
                "pung": pung_meld,
                "chow": chow_meld
            }
            if any(options.values()):
                meld_type, meld = next_player.query_meld(self.game_state, options)
            else:
                meld_type, meld = "", []

            player_actions[next_player_idx] = {
                "meld_type": meld_type,
                "meld": meld,
                "state": {}
            }
            if meld_type == "win":
                player_actions[next_player_idx]["state"] = state
        if not player_actions:
            return False  # everyone skips

        # Choose action to resolve based on priority and seat position
        player_to_act = -1
        for meld_type in ["win", "kong", "pung", "chow"]:
            for i in range(1, NUM_PLAYERS):
                next_player_idx = (p_id + i) % NUM_PLAYERS
                if player_actions[next_player_idx]["meld_type"] == meld_type:
                    player_to_act = next_player_idx
                    break
            if player_to_act != -1:
                break
        else:
            return False  # everyone skips

        # Resolve chosen action
        meld_type = player_actions[player_to_act]["meld_type"]
        meld = player_actions[player_to_act]["meld"]

        next_player_state = self.game_state["players"][player_to_act]
        next_player_state["hand"].append(player_state["discards"].pop())
        if meld_type == "win":
            self.perform_win(next_player_idx, meld)
            print(f"Player {next_player_idx} wins")
            state["round_wind"] = self.game_state["round_wind"]
            if not self.game_state["wall"]:
                state["win_condition"].append("last_draw")
            if self.game_state["first"]:
                state["win_condition"].append("earthly_hand")
            self.game_state["done"] = True
            self.game_state["winning_hand_state"] = state
            print("Winning hand: ", next_player_state["melds"])
            print("Winning hand state: ", state)
            print("Winning hand score: ", score_hand(next_player_state["melds"], state))
            return True
        self.perform_single_meld(next_player_idx, meld)
        if meld_type == "kong":
            self.resolve_kong(p_id, next_player_idx, meld)
            return True
        if meld_type in ["pung", "chow"]:
            print(f"Player {next_player_idx} has performed a {meld_type}")
            self.game_state["discard"] = True
            self.game_state["current_player"] = next_player_idx
            self.game_state["kong"] = False
            self.game_state["double_kong"] = False
            if self.game_state["first"]:
                self.game_state["first"] = False
            return True
        return False

    def prepare_next_turn(self, p_id: int) -> None:
        self.game_state["kong"] = False
        self.game_state["double_kong"] = False
        if self.game_state["first"]:
            self.game_state["first"] = False
        self.game_state["current_player"] = (p_id + 1) % NUM_PLAYERS
        print()

    def perform_single_meld(self, p_id: int, to_meld: list[Tile]) -> None:
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

    def perform_win(self, p_id: int, to_meld: list[list[Tile]]) -> None:
        player_state = self.game_state["players"][p_id]
        # handle win -- multiple melds, list of list of tiles
        for meld in to_meld:
            for tile in meld:
                player_state["hand"].remove(tile)
            player_state["melds"].append(meld)

    def print_player_info(self, p_id: int, sort_hand: bool = False) -> None:
        p_state = self.game_state["players"][p_id]
        if sort_hand:
            print(", ".join(str(tile) for tile in sorted(p_state["hand"])))
        else:
            print(", ".join(str(tile) for tile in p_state["hand"]))

        print(f"Melds: {p_state['melds']}")
