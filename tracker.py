from file_reader import *

all_actions = np.array(list(cst.Action))
all_positions = np.array(list(Position))
all_streets = np.array(list(cst.Street))
all_cards = np.array(list(Card))


class PlayerHistory:

    def __init__(self):
        self.df = None
        self.parser = FileParser()

    @staticmethod
    def filter(hands) -> np.ndarray:
        return np.array([hand for hand in hands if hand is not None])

    def to_pandas(self, hands: np.ndarray) -> pd.DataFrame:
        hands = self.filter(hands)
        self.df = pd.DataFrame({"hand": hands})
        return self.df

    def load_pl_hands(self, pl_name: str,  dir_name="history") -> pd.DataFrame:
        hands = self.parser.parse_directory(dir_name=dir_name)
        self.to_pandas(hands)
        self.df = self.get_player_hands(pl_name)
        self.convert_hands(pl_name)
        return self.df

    def build_history(self, hands: np.ndarray, pl_name: str):
        self.to_pandas(hands)
        self.df = self.get_player_hands(pl_name)
        self.convert_hands(pl_name)
        return self.df

    def convert_hands(self, pl_name):
        self.convert_max_pl()
        self.convert_level()
        self.filter_levels()
        self.convert_ante()
        self.convert_bb()
        self.convert_stack(pl_name)
        self.convert_position(pl_name)
        self.convert_combo(pl_name)
        self.convert_actions(pl_name)
        self.convert_played()
        self.convert_vpip()
        self.convert_pfr()

    @staticmethod
    def pl_in_players(hand: HandHistory, pl_name: str) -> bool:
        return pl_name in hand.table.players.name_dict.keys()

    def get_player_hands(self, pl_name: str):
        vfunc = np.vectorize(self.pl_in_players)
        df = self.df[vfunc(self.df["hand"], pl_name)]
        return df

    @staticmethod
    def get_level(hand: HandHistory) -> int:
        return hand.level.level

    def convert_level(self):
        vfunc = np.vectorize(self.get_level)
        self.df["level"] = vfunc(self.df["hand"])

    def filter_levels(self):
        self.df = self.df[self.df["level"] < 100]
        self.df.reset_index(drop=True, inplace=True)

    @staticmethod
    def get_bb(hand: HandHistory) -> float:
        return hand.level.bb

    def convert_bb(self):
        vfunc = np.vectorize(self.get_bb)
        self.df["bb"] = vfunc(self.df["hand"])

    @staticmethod
    def get_ante(hand: HandHistory) -> float:
        return hand.level.ante

    def convert_ante(self):
        vfunc = np.vectorize(self.get_ante)
        self.df["ante"] = vfunc(self.df["hand"])

    @staticmethod
    def get_max_pl(hand: HandHistory) -> int:
        return hand.table.max_players

    def convert_max_pl(self):
        vfunc = np.vectorize(self.get_max_pl)
        self.df["max_pl"] = vfunc(self.df["hand"])

    @staticmethod
    def get_player(hand: HandHistory, pl_name: str) -> Player:
        return hand.table.players.name_dict[pl_name]

    def get_stack(self, hand: HandHistory, pl_name) -> float:
        player = self.get_player(hand, pl_name)
        return player.init_stack

    def convert_stack(self, pl_name: int):
        vfunc = np.vectorize(self.get_stack)
        self.df[f"stack"] = vfunc(self.df["hand"], pl_name)
        self.df[f"stack_bb"] = self.df[f"stack"] / self.df[f"bb"]

    def get_position(self, hand: HandHistory, pl_name: str) -> str:
        player = self.get_player(hand, pl_name)
        return f"{player.position}"

    def convert_position(self, pl_name):
        vfunc = np.vectorize(self.get_position)
        self.df[f"position"] = vfunc(self.df["hand"], pl_name)

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
        vfunc_combo = np.vectorize(self.get_combo_str)
        vfunc_hand = np.vectorize(self.get_hand_str)
        self.df[f"combo"] = vfunc_combo(self.df["hand"], pl_name)
        self.df[f"hand_cards"] = vfunc_hand(self.df["hand"], pl_name)

    def get_action(self, hand: HandHistory, pl_name: str, act_index: int) -> Action or None:
        try:
            player = self.get_player(hand=hand, pl_name=pl_name)
            return player.actions[act_index]
        except AttributeError:
            return None
        except IndexError:
            return None

    def get_action_street(self, hand: HandHistory, pl_name: str, act_index: int) -> str:
        try:
            action = self.get_action(hand=hand, pl_name=pl_name, act_index=act_index)
            return f"{action['street']}"
        except AttributeError:
            return f"None"
        except TypeError:
            return f"None"

    def get_action_move(self, hand: HandHistory, pl_name: str, act_index: int) -> str:
        try:
            action = self.get_action(hand=hand, pl_name=pl_name, act_index=act_index)
            return f"{action['move']}"
        except AttributeError:
            return f"None"
        except TypeError:
            return f"None"

    def get_action_value(self, hand: HandHistory, pl_name: str, act_index: int) -> float:
        try:
            action = self.get_action(hand=hand, pl_name=pl_name, act_index=act_index)
            return action['value']
        except AttributeError:
            return 0
        except TypeError:
            return 0

    def convert_action(self, pl_name: str, act_index: int):
        j = act_index
        vfunc_street = np.vectorize(self.get_action_street)
        vfunc_move = np.vectorize(self.get_action_move)
        vfunc_value = np.vectorize(self.get_action_value)
        self.df[f"action_{j}_street"] = vfunc_street(self.df["hand"], pl_name, j)
        self.df[f"action_{j}_move"] = vfunc_move(self.df["hand"], pl_name, j)
        self.df[f"action_{j}_value"] = vfunc_value(self.df["hand"], pl_name, j)
        self.df[f"action_{j}_value_bb"] = self.df[f"action_{j}_value"] / self.df[f"bb"]

    def convert_actions(self, pl_name: str):
        for i in range(8):
            self.convert_action(pl_name=pl_name, act_index=i)

    def convert_played(self):
        self.df["played_bool"] = self.df["action_0_move"] != "None"

    def convert_vpip(self):
        self.df["VPIP_bool"] = (self.df["action_0_move"] == "call") |\
                               (self.df["action_0_move"] == "bet") |\
                               (self.df["action_0_move"] == "raise")

    def convert_pfr(self):
        self.df["PFR_bool"] = (self.df["action_0_move"] == "bet") |\
                               (self.df["action_0_move"] == "raise")

    @property
    def played(self):
        return self.df["played_bool"].sum()

    @property
    def vpip(self):
        return self.df["VPIP_bool"].sum()/self.played

    @property
    def pfr(self):
        return self.df["PFR_bool"].sum()/self.played
