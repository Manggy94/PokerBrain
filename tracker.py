import pandas as pd
import numpy as np
from API.hand import Combo, Hand
# from API.listings import all_actions
from API.Table import Action, HandHistory, Player
from file_reader import FileParser


class PlayerHistory:

    def __init__(self):
        self.df = None
        self.parser = FileParser()
        self.player_name = None

    @staticmethod
    def filter(hands) -> np.ndarray:
        return np.array([hand for hand in hands if hand is not None])

    def to_pandas(self, hands: np.ndarray) -> pd.DataFrame:
        hands = self.filter(hands)
        self.df = pd.DataFrame({"hand": hands})
        return self.df

    def load_pl_hands(self, pl_name: str,  dir_name="history") -> pd.DataFrame:
        hands = self.parser.parse_directory(dir_name=dir_name)
        return self.build_history(input_hands=hands, name=pl_name).df

    def get_action(self, hand: HandHistory, name: str, act_index: int) -> Action or None:
        try:
            player = self.get_player(hand, name)
            return player.actions[act_index]
        except AttributeError:
            return None
        except IndexError:
            return None

    def get_action_street(self, hand: HandHistory, name: str, act_index: int) -> str:
        try:
            action = self.get_action(hand=hand, name=name, act_index=act_index)
            return f"{action['street']}"
        except AttributeError:
            return f"None"
        except TypeError:
            return f"None"

    def get_action_move(self, hand: HandHistory, name: str, act_index: int) -> str:
        try:
            action = self.get_action(hand=hand, name=name, act_index=act_index)
            return f"{action['move']}"
        except AttributeError:
            return f"None"
        except TypeError:
            return f"None"

    def get_action_value(self, hand: HandHistory, name: str, act_index: int) -> float:
        try:
            action = self.get_action(hand=hand, name=name, act_index=act_index)
            return action['value']
        except AttributeError:
            return 0
        except TypeError:
            return 0

    def build_history(self, input_hands: np.ndarray, name: str):
        self.player_name = name
        name_filter = np.array([self.pl_in_players(hand, name) for hand in input_hands])
        new_hands = input_hands[name_filter]
        levels = np.array([self.get_level(hand) for hand in new_hands], dtype="int8")
        bb = np.array([self.get_bb(hand) for hand in new_hands])
        max_pl = np.array([self.get_max_pl(hand) for hand in new_hands])
        stacks = np.array([self.get_stack(hand, name) for hand in new_hands])
        stacks_bb = stacks / bb
        positions = np.array([self.get_position(hand, name) for hand in new_hands])
        combos = np.array([self.get_combo_str(hand, name) for hand in new_hands])
        hands = np.array([self.get_hand_str(hand, name) for hand in new_hands])
        act_val = np.vstack([np.array([self.get_action_value(hand, name, i) for i in range(8)], dtype=float) for hand in new_hands])
        act_data = np.vstack([np.hstack([np.array([self.get_action_street(hand, name, i), self.get_action_move(hand, name, i)])for i in range(8)]) for hand in new_hands])
        tab2 = pd.DataFrame(columns=[f"action_{i}_{j}" for i in range(8) for j in ["street", "move"]], data=act_data)
        tab3 = pd.DataFrame(columns=[f"action_{i}_value" for i in range(8)], data=act_val)
        tab = pd.DataFrame({"level": levels, "bb": bb, "max_pl": max_pl, "stack": stacks, "stack_bb": stacks_bb, "position": positions, "combo": combos, "hand": hands})
        new_df = tab.join([tab2, tab3])
        for i in range(8):
            new_df[f"action_{i}_value"].astype(float)
            new_df[f"action_{i}_value_bb"] = new_df[f"action_{i}_value"] / new_df["bb"]
        new_df["played"] = new_df["action_0_move"] != "None"
        new_df["VPIP"] = (new_df["action_0_move"] == "call") | (new_df["action_0_move"] == "bet") | (
                    new_df["action_0_move"] == "raise")
        new_df["PFR"] = (new_df["action_0_move"] == "bet") | (new_df["action_0_move"] == "raise")
        self.df = new_df
        return self

    def save_history(self):
        self.df.to_csv(f"{self.parser.root}/Data/Pl_histories/{self.player_name}.csv")

    def get_history(self, player_name: str):
        self.player_name = player_name
        self.df = pd.read_csv(f"{self.parser.root}/Data/Pl_histories/{player_name}.csv")

    @staticmethod
    def pl_in_players(hand: HandHistory, pl_name: str) -> bool:
        return pl_name in hand.table.players.name_dict.keys()

    def get_player_hands(self, pl_name: str):
        vfunc = np.vectorize(self.pl_in_players)
        df = self.df[vfunc(self.df["hand"], pl_name)]
        return df

    @staticmethod
    def get_level(hand: HandHistory) -> int:
        try:
            return hand.level.level
        except AttributeError:
            return 0

    def filter_levels(self):
        self.df = self.df[self.df["level"] < 100]
        self.df = self.df[self.df["level"] > 0]
        self.df.reset_index(drop=True, inplace=True)

    @staticmethod
    def get_bb(hand: HandHistory) -> float:
        try:
            return hand.level.bb
        except AttributeError:
            return 0

    def convert_bb(self):
        try:
            vfunc = np.vectorize(self.get_bb)
            self.df["bb"] = vfunc(self.df["hand"])
        except ValueError:
            self.df["bb"] = 0

    @staticmethod
    def get_ante(hand: HandHistory) -> float:
        try:
            return hand.level.ante
        except AttributeError:
            return 0

    def convert_ante(self):
        try:
            vfunc = np.vectorize(self.get_ante)
            self.df["ante"] = vfunc(self.df["hand"])
        except ValueError:
            self.df["ante"] = 0

    @staticmethod
    def get_max_pl(hand: HandHistory) -> int:
        try:
            return hand.table.max_players
        except AttributeError:
            return 0

    def convert_max_pl(self):
        try:
            vfunc = np.vectorize(self.get_max_pl)
            self.df["max_pl"] = vfunc(self.df["hand"])
        except ValueError:
            self.df["max_pl"] = 0

    @staticmethod
    def get_player(hand: HandHistory, pl_name: str) -> Player or None:
        try:
            return hand.table.players.name_dict[pl_name]
        except AttributeError:
            return None

    def get_stack(self, hand: HandHistory, pl_name) -> float:
        try:
            player = self.get_player(hand, pl_name)
            return player.init_stack
        except AttributeError:
            return 0

    def convert_stack(self, pl_name: int):
        try:
            vfunc = np.vectorize(self.get_stack)
            self.df[f"stack"] = vfunc(self.df["hand"], pl_name)
            self.df[f"stack_bb"] = self.df[f"stack"] / self.df[f"bb"]
        except ValueError:
            self.df["stack"] = 0
            self.df["stack_bb"] = 0

    def get_position(self, hand: HandHistory, pl_name: str) -> str:
        try:
            player = self.get_player(hand, pl_name)
            return f"{player.position}"
        except AttributeError:
            return "None"

    def get_combo(self, hand: HandHistory, pl_name: str) -> Combo or None:
        try:
            player = self.get_player(hand, pl_name)
            return player.combo
        except AttributeError:
            return None

    def get_combo_str(self, hand: HandHistory, pl_name: str) -> str:
        try:
            combo = self.get_combo(hand=hand, pl_name=pl_name)
            return f"{combo}"
        except AttributeError:
            return f"None"

    def get_hand(self, hand: HandHistory, pl_name: str) -> Hand or None:
        try:
            combo = self.get_combo(hand=hand, pl_name=pl_name)
            return combo.to_hand()
        except AttributeError:
            return None

    def get_hand_str(self, hand: HandHistory, pl_name: str) -> str:
        try:
            card_hand = self.get_hand(hand=hand, pl_name=pl_name)
            return f"{card_hand}"
        except AttributeError:
            return f"None"

    def convert_combo(self, pl_name: str):
        try:
            vfunc_combo = np.vectorize(self.get_combo_str)
            vfunc_hand = np.vectorize(self.get_hand_str)
            self.df[f"combo"] = vfunc_combo(self.df["hand"], pl_name)
            self.df[f"hand_cards"] = vfunc_hand(self.df["hand"], pl_name)
        except ValueError:
            self.df[f"combo"] = "None"
            self.df[f"hand_cards"] = "None"

    @property
    def played(self):
        return self.df["played"].sum()

    @property
    def vpip_sum(self):
        return self.df["VPIP"].sum()

    @property
    def vpip(self):
        if self.played == 0:
            return 0
        return self.vpip_sum/self.played

    @property
    def pfr_sum(self):
        return self.df["PFR"].sum()

    @property
    def pfr(self):
        if self.played == 0:
            return 0
        return self.pfr_sum/self.played
