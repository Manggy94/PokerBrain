import numpy as np
import pandas as pd
from API.card import Card
from API.listings import all_streets, str_positions
from API.Table import Combo, HandHistory, Player
from file_reader import FileParser
from tracker import PlayerHistory


class HandConverter:
    """A class to transform Handhistory objects into pandas tables"""
    def __init__(self):
        self.streets = ["pf", "flop", "turn", "river"]
        self.labels = ["seat", "move", "value"]
        self.txt_label = "move"
        self.val_labels = ["seat", "value"]
        self.ext_cols = [f"{s}_action_{k}_{label}" for s in self.streets for k in range(24) for label in self.labels]
        self.stack_cols = [f"P{i}_stack" for i in range(9)]
        self.street_val_cols = [f"{s}_action_{k}_value" for s in self.streets for k in range(24)]
        self.df = None
        self.current_df = None
        self.none_count = 0
        self.parser = FileParser()
        self.histories = None

    @staticmethod
    def filter(hands) -> np.ndarray:
        return np.array([hand for hand in hands if hand is not None])

    def import_hands(self, dir_name: str = "history"):
        return self.filter(self.parser.parse_directory(dir_name=dir_name))

    def to_pandas(self, hands: np.ndarray, inplace: bool = True) -> pd.DataFrame:
        hands = self.filter(hands)
        df = pd.DataFrame({"hand": hands})
        if inplace:
            self.df = pd.DataFrame({"hand": hands})
        return df

    def build_hands(self, hands: np.ndarray) -> pd.DataFrame:
        self.to_pandas(hands)
        self.convert_hand()
        self.filter_levels()
        self.df.reset_index(drop=True, inplace=True)
        return self.df

    def convert_single_hand(self, hand: HandHistory) -> pd.DataFrame:
        np_hand = np.array([hand])
        return self.build_hands(np_hand)

    def get_names(self, np_hands):
        np_hands = self.filter(np_hands)
        return np.unique(np.hstack([np.array([player.name for player in hand.table.players]) for hand in np_hands]))

    def build_histories(self, input_hands: np.ndarray) -> np.ndarray:
        names = self.get_names(input_hands)
        return np.array([PlayerHistory().build_history(input_hands=input_hands, name=name) for name in names])

    @staticmethod
    def histories_resume(histories: np.ndarray):
        names = np.array([history.player_name for history in histories])
        played = np.array([history.played for history in histories], dtype="int32")
        vpip = np.array([history.vpip for history in histories], dtype="float16")
        pfr = np.array([history.pfr for history in histories], dtype="float16")
        resume = pd.DataFrame({"name": names, "played": played, "vpip": vpip, "pfr": pfr}, index=names)
        return resume

    def save_histories(self, input_hands: np.ndarray):
        names = self.get_names(input_hands)
        histories = self.build_histories(input_hands)
        played = np.array([history.played for history in histories], dtype="int32")
        vpip = np.array([history.vpip for history in histories], dtype=float)
        pfr = np.array([history.pfr for history in histories])
        df = pd.DataFrame({"name": names, "played": played, "vpip": vpip, "pfr": pfr}, index=names)
        df.to_csv(f"{self.parser.root}/Data/histories.csv")

    def get_histories(self):
        histories = pd.read_csv(f"{self.parser.root}/Data/histories.csv", index_col=0)
        self.histories = histories
        return histories

    def load_hands(self, dir_name="history") -> pd.DataFrame:
        hands = self.parser.parse_directory(dir_name=dir_name)
        return self.build_hands(hands)

    @staticmethod
    def get_hand_info(hand: HandHistory) -> dict:
        return {"tour_id": hand.tournament.id, "table_id": hand.table.ident, "level": hand.level.level,
                "bb": hand.level.bb, "ante": hand.level.ante, "max_pl": hand.table.max_players, "btn": hand.button,
                "buyin": hand.tournament.buyin}

    def get_hand_id(self, hand: HandHistory) -> str:
        try:
            return f"{hand.hand_id}"
        except AttributeError:
            phr = f" None{self.none_count}"
            self.none_count += 1
            return phr

    def get_hand_id_series(self, input_hands: np.ndarray) -> pd.Series:
        return pd.Series([self.get_hand_id(hand) for hand in input_hands], name="hand_id")

    def convert_hand_id(self):
        vfunc = np.vectorize(self.get_hand_id)
        self.df["hand_id"] = vfunc(self.df["hand"])

    @staticmethod
    def get_table_id(hand: HandHistory) -> str:
        return hand.table.ident

    def get_table_id_series(self, input_hands: np.ndarray) -> pd.Series:
        return pd.Series([self.get_table_id(hand) for hand in input_hands], name="table_id")

    def convert_table_id(self):
        vfunc = np.vectorize(self.get_table_id)
        self.df["table_id"] = vfunc(self.df["hand"])

    @staticmethod
    def get_tournament_id(hand: HandHistory) -> str:
        return hand.tournament.id

    def get_tournament_id_series(self, input_hands: np.ndarray) -> pd.Series:
        return pd.Series([self.get_tournament_id(hand) for hand in input_hands], name="tour_id")

    def convert_tournament_id(self):
        vfunc = np.vectorize(self.get_tournament_id)
        self.df["tour_id"] = vfunc(self.df["hand"])

    @staticmethod
    def get_level(hand: HandHistory) -> int:
        return hand.level.level

    def get_level_series(self, input_hands: np.ndarray) -> pd.Series:
        return pd.Series([self.get_level(hand) for hand in input_hands], name="level", dtype="int8")

    def convert_level(self):
        vfunc = np.vectorize(self.get_level)
        self.df["level"] = vfunc(self.df["hand"])

    @staticmethod
    def get_bb(hand: HandHistory) -> float:
        return hand.level.bb

    def get_bb_series(self, input_hands: np.ndarray) -> pd.Series:
        return pd.Series([self.get_bb(hand) for hand in input_hands], name="bb")

    def convert_bb(self):
        vfunc = np.vectorize(self.get_bb)
        self.df["bb"] = vfunc(self.df["hand"])

    @staticmethod
    def get_ante(hand: HandHistory) -> float:
        return hand.level.ante

    def get_ante_series(self, input_hands: np.ndarray) -> pd.Series:
        return pd.Series([self.get_ante(hand) for hand in input_hands], name="ante")

    def convert_ante(self):
        vfunc = np.vectorize(self.get_ante)
        self.df["ante"] = vfunc(self.df["hand"])

    @staticmethod
    def get_hero(hand: HandHistory) -> Player:
        try:
            return hand.table.hero
        except TypeError:
            print(hand.table)

    def get_hero_combo(self, hand: HandHistory) -> Combo or None:
        try:
            hero = self.get_hero(hand)
            return hero.combo
        except AttributeError:
            return None
        except TypeError:
            return None

    def get_hero_combo_str(self, hand: HandHistory) -> str:
        try:
            combo = self.get_hero_combo(hand)
            return str(combo)
        except AttributeError:
            return "None"
        except TypeError:
            return "None"

    def get_hero_combo_str_series(self, input_hands: np.ndarray) -> pd.Series:
        return pd.Series([self.get_hero_combo_str(hand) for hand in input_hands], name="hero_combo")

    def get_hero_hand(self, hand: HandHistory) -> str:
        try:
            combo = self.get_hero_combo(hand)
            return f"{combo.to_hand()}"
        except AttributeError:
            pass

    def get_hero_hand_series(self, input_hands: np.ndarray) -> pd.Series:
        return pd.Series([self.get_hero_hand(hand) for hand in input_hands], name="hero_hand")

    def get_hero_first_suit(self, hand: HandHistory) -> str:
        try:
            combo = self.get_hero_combo(hand)
            return f"{combo.first.suit}"
        except AttributeError:
            return "None"
        except TypeError:
            return "None"

    def get_hero_first_suit_series(self, input_hands: np.ndarray) -> pd.Series:
        return pd.Series([self.get_hero_first_suit(hand) for hand in input_hands], name="hero_first_suit")

    def get_hero_second_suit(self, hand: HandHistory) -> str:
        try:
            combo = self.get_hero_combo(hand)
            return f"{combo.second.suit}"
        except AttributeError:
            return "None"
        except TypeError:
            return "None"

    def get_hero_second_suit_series(self, input_hands: np.ndarray) -> pd.Series:
        return pd.Series([self.get_hero_second_suit(hand) for hand in input_hands], name="hero_second_suit")

    def get_hero_first_rank(self, hand: HandHistory) -> str:
        try:
            combo = self.get_hero_combo(hand)
            return f"{combo.first.rank}"
        except AttributeError:
            return "None"
        except TypeError:
            return "None"

    def get_hero_first_rank_series(self, input_hands: np.ndarray) -> pd.Series:
        return pd.Series([self.get_hero_first_rank(hand) for hand in input_hands], name="hero_first_rank")

    def get_hero_second_rank(self, hand: HandHistory) -> str:
        try:
            combo = self.get_hero_combo(hand)
            return f"{combo.second.rank}"
        except AttributeError:
            return "None"
        except TypeError:
            return "None"

    def get_hero_second_rank_series(self, input_hands: np.ndarray) -> pd.Series:
        return pd.Series([self.get_hero_second_rank(hand) for hand in input_hands], name="hero_second_rank")

    def convert_hero_combo(self):
        vfunc = np.vectorize(self.get_hero_combo_str)
        vfunc_fs = np.vectorize(self.get_hero_first_suit)
        vfunc_ss = np.vectorize(self.get_hero_second_suit)
        vfunc_fr = np.vectorize(self.get_hero_first_rank)
        vfunc_sr = np.vectorize(self.get_hero_second_rank)
        vfunc_hd = np.vectorize(self.get_hero_hand)
        self.df["hero_combo"] = vfunc(self.df["hand"])
        self.df["hero_hand"] = vfunc_hd(self.df["hand"])
        self.df["hero_first_suit"] = vfunc_fs(self.df["hand"])
        self.df["hero_second_suit"] = vfunc_ss(self.df["hand"])
        self.df["hero_first_rank"] = vfunc_fr(self.df["hand"])
        self.df["hero_second_rank"] = vfunc_sr(self.df["hand"])

    def get_hero_position(self, hand: HandHistory) -> str:
        try:
            hero = self.get_hero(hand)
            return f"{hero.position}"
        except AttributeError:
            pass

    def convert_hero_position(self):
        vfunc = np.vectorize(self.get_hero_position)
        self.df["hero_position"] = vfunc(self.df["hand"])

    @staticmethod
    def get_max_pl(hand: HandHistory) -> int:
        return hand.table.max_players

    def get_max_pl_series(self, input_hands: np.ndarray) -> pd.Series:
        return pd.Series([self.get_max_pl(hand) for hand in input_hands], name="max_pl")

    def convert_max_pl(self):
        vfunc = np.vectorize(self.get_max_pl)
        self.df["max_pl"] = vfunc(self.df["hand"])
        self.df["max_pl"] = self.df["max_pl"].astype("int8")

    @staticmethod
    def get_buyin(hand: HandHistory) -> float:
        return hand.tournament.buyin

    def convert_buyin(self):
        vfunc = np.vectorize(self.get_buyin)
        self.df["buyin"] = vfunc(self.df["hand"])

    @staticmethod
    def get_current_street(hand: HandHistory):
        return hand.table.current_street.name

    def convert_current_street(self):
        vfunc = np.vectorize(self.get_current_street)
        self.df["current_street"] = vfunc(self.df["hand"])

    def convert_hand_info(self):
        self.convert_hand_id()
        self.convert_tournament_id()
        self.convert_table_id()
        self.convert_level()
        self.convert_current_street()
        self.convert_bb()
        self.convert_ante()
        self.convert_max_pl()
        self.convert_buyin()
        self.convert_hero_combo()
        self.convert_hero_position()

    @staticmethod
    def get_card(hand: HandHistory, index: int) -> Card or None:
        try:
            return hand.table.board[index]
        except IndexError:
            return None

    def get_card_str(self, hand: HandHistory, index: int) -> str:
        try:
            card = self.get_card(hand, index)
            return f"{card}"
        except AttributeError:
            return "None"

    def get_card_rank(self, hand: HandHistory, index: int) -> str:
        try:
            card = self.get_card(hand, index)
            return f"{card.rank}"
        except AttributeError:
            return f"None"

    def get_card_suit(self, hand: HandHistory, index: int) -> str:
        try:
            card = self.get_card(hand, index)
            return f"{card.suit}"
        except AttributeError:
            return f"None"

    def convert_board(self):
        vfunc = np.vectorize(self.get_card)
        vfunc_rank = np.vectorize(self.get_card_rank)
        vfunc_suit = np.vectorize(self.get_card_suit)
        for i in range(5):
            self.df[f"Card_{i}"] = vfunc(self.df["hand"], i)
            self.df[f"Card_{i}_rank"] = vfunc_rank(self.df["hand"], i)
            self.df[f"Card_{i}_suit"] = vfunc_suit(self.df["hand"], i)

    @staticmethod
    def get_is_rainbow(hand: HandHistory) -> str:
        return f"{hand.table.is_rainbow}"

    def convert_is_rainbow(self):
        vf = np.vectorize(self.get_is_rainbow)
        self.df["is_rainbow"] = vf(self.df["hand"])

    @staticmethod
    def get_is_monotone(hand: HandHistory) -> str:
        return f"{hand.table.is_monotone}"

    def convert_is_monotone(self):
        vf = np.vectorize(self.get_is_monotone)
        self.df["is_monotone"] = vf(self.df["hand"])

    @staticmethod
    def get_is_triplet(hand: HandHistory) -> str:
        return f"{hand.table.is_triplet}"

    def convert_is_triplet(self):
        vf = np.vectorize(self.get_is_triplet)
        self.df["is_triplet"] = vf(self.df["hand"])

    def convert_flop_info(self):
        self.convert_is_rainbow()
        self.convert_is_triplet()
        self.convert_is_monotone()
        self.convert_has_pair()
        self.convert_has_straightdraw()
        self.convert_has_gutshot()
        self.convert_has_flushdraw()

    @staticmethod
    def get_has_pair(hand: HandHistory) -> str:
        return f"{hand.table.has_pair}"

    def convert_has_pair(self):
        vf = np.vectorize(self.get_has_pair)
        self.df["has_pair"] = vf(self.df["hand"])

    @staticmethod
    def get_has_straightdraw(hand: HandHistory) -> str:
        return f"{hand.table.has_straightdraw}"

    def convert_has_straightdraw(self):
        vf = np.vectorize(self.get_has_straightdraw)
        self.df["has_straightdraw"] = vf(self.df["hand"])

    @staticmethod
    def get_has_gutshot(hand: HandHistory) -> str:
        return f"{hand.table.has_gutshot}"

    def convert_has_gutshot(self):
        vf = np.vectorize(self.get_has_gutshot)
        self.df["has_gutshot"] = vf(self.df["hand"])

    @staticmethod
    def get_has_flushdraw(hand: HandHistory) -> str:
        return f"{hand.table.has_flushdraw}"

    def convert_has_flushdraw(self):
        vf = np.vectorize(self.get_has_flushdraw)
        self.df["has_flushdraw"] = vf(self.df["hand"])

    def convert_hand(self):
        self.convert_hand_info()
        self.convert_positions()
        self.convert_board()
        self.convert_flop_info()

    def filter_levels(self):
        self.df = self.df[self.df["level"] < 100]
        self.df = self.df[self.df["level"] >= 0]

    @staticmethod
    def get_idents(hands) -> pd.Index:
        return pd.Index([hand.hand_id for hand in hands])

    @staticmethod
    def get_position_player(hand: HandHistory, position):
        player = hand.table.players.positions.get(position)
        if player is None:
            raise EmptyPositionError
        return player

    def get_position_name(self, hand: HandHistory, position):
        try:
            player = self.get_position_player(hand, position)
            return player.name
        except AttributeError:
            return pd.NA
        except EmptyPositionError:
            return pd.NA

    def convert_position_name(self, position):
        vfunc = np.vectorize(self.get_position_name)
        self.df[f"{position}_name"] = vfunc(self.df["hand"], position)

    def get_position_stack(self, hand: HandHistory, position):
        try:
            player = self.get_position_player(hand, position)
            return float(player.init_stack)
        except AttributeError:
            pass
        except TypeError:
            return 0.0
        except EmptyPositionError:
            return np.nan

    def convert_position_stack(self, position):
        vfunc = np.vectorize(self.get_position_stack)
        self.df[f"{position}_stack"] = vfunc(self.df["hand"], position)
        self.df[f"{position}_stack_bb"] = self.df[f"{position}_stack"] / self.df[f"bb"]

    def get_position_combo(self, hand: HandHistory, position):
        try:
            player = self.get_position_player(hand, position)
            return player.combo
        except AttributeError:
            return pd.NA
        except EmptyPositionError:
            return pd.NA

    def get_position_combo_str(self, hand: HandHistory, position):
        try:
            combo = self.get_position_combo(hand, position)
            return f"{combo}"
        except AttributeError:
            return None
        except EmptyPositionError:
            return pd.NA

    def get_position_hand_str(self, hand: HandHistory, position):
        try:
            combo = self.get_position_combo(hand, position)
            return f"{combo.to_hand()}"
        except AttributeError:
            return None
        except EmptyPositionError:
            return pd.NA

    def convert_position_combo(self, position):
        vfunc_combo = np.vectorize(self.get_position_combo_str)
        vfunc_hand = np.vectorize(self.get_position_hand_str)
        self.df[f"{position}_combo"] = vfunc_combo(self.df["hand"], position)
        self.df[f"{position}_hand"] = vfunc_hand(self.df["hand"], position)

    def get_action(self, hand: HandHistory, position, street, index):

        player = self.get_position_player(hand, position)
        return player.actions.get(street)[index]

    def get_action_move(self, hand: HandHistory, position, street, index):
        try:
            action = self.get_action(hand, position, street, index)
            return action.get("move")
        except EmptyPositionError:
            return pd.NA
        except IndexError:
            return pd.NA

    def convert_action_move(self, position, street, index):
        vfunc = np.vectorize(self.get_action_move)
        self.df[f"{position}_{street}_action_{index}_move"] = vfunc(self.df["hand"], position, street, index)

    def get_action_value(self, hand: HandHistory, position, street, index):
        try:
            action = self.get_action(hand, position, street, index)
            return float(action.get("value"))
        except EmptyPositionError:
            return np.nan
        except IndexError:
            return np.nan

    def get_action_pot(self, hand: HandHistory, position, street, index):
        try:
            action = self.get_action(hand, position, street, index)
            return float(action.get("pot"))
        except EmptyPositionError:
            return np.nan
        except IndexError:
            return np.nan

    def get_action_stack(self, hand: HandHistory, position, street, index):
        try:
            action = self.get_action(hand, position, street, index)
            return float(action.get("stack"))
        except EmptyPositionError:
            return np.nan
        except IndexError:
            return np.nan

    def get_action_to_call(self, hand: HandHistory, position, street, index):
        try:
            action = self.get_action(hand, position, street, index)
            return float(action.get("to_call"))
        except EmptyPositionError:
            return np.nan
        except IndexError:
            return np.nan

    def get_action_odds(self, hand: HandHistory, position, street, index):
        try:
            action = self.get_action(hand, position, street, index)
            if float(action.get("odds")) > 1e5:
                return 1e5
            return float(action.get("odds"))
        except EmptyPositionError:
            return np.nan
        except IndexError:
            return np.nan

    def convert_action_value(self, pos, street, idx):
        vfunc = np.vectorize(self.get_action_value)
        self.df[f"{pos}_{street}_action_{idx}_val"] = vfunc(self.df["hand"], pos, street, idx) / self.df[f"bb"]
        self.df[f"{pos}_{street}_action_{idx}_ratio"] = self.df[f"{pos}_{street}_action_{idx}_val"] / self.df[f"{pos}_{street}_action_{idx}_stack"]

    def convert_action_pot(self, pos, street, idx):
        vfunc = np.vectorize(self.get_action_pot)
        self.df[f"{pos}_{street}_action_{idx}_pot"] = vfunc(self.df["hand"], pos, street, idx) / self.df[f"bb"]

    def convert_action_stack(self, pos, street, idx):
        vfunc = np.vectorize(self.get_action_stack)
        self.df[f"{pos}_{street}_action_{idx}_stack"] = vfunc(self.df["hand"], pos, street, idx) / self.df[f"bb"]

    def convert_action_to_call(self, pos, street, idx):
        vfunc = np.vectorize(self.get_action_to_call)
        self.df[f"{pos}_{street}_action_{idx}_to_call"] = vfunc(self.df["hand"], pos, street, idx) / self.df[f"bb"]

    def convert_action_odds(self, pos, street, idx):
        vfunc = np.vectorize(self.get_action_odds)
        self.df[f"{pos}_{street}_action_{idx}_odds"] = vfunc(self.df["hand"], pos, street, idx)
        self.df[f"{pos}_{street}_action_{idx}_req_equity"] = 1/(1+self.df[f"{pos}_{street}_action_{idx}_odds"])

    def convert_action(self, position, street, index):
        self.convert_action_pot(position, street, index)
        self.convert_action_stack(position, street, index)
        self.convert_action_to_call(position, street, index)
        self.convert_action_odds(position, street, index)
        self.convert_action_move(position, street, index)
        self.convert_action_value(position, street, index)

    def convert_actions(self, position, street):
        for index in range(2):
            self.convert_action(position, street, index)

    def convert_position_actions(self, position):
        for street in all_streets[:-1]:
            self.convert_actions(position, f"{street}")

    def convert_position(self, pos):
        self.convert_position_name(pos)
        self.convert_position_stack(pos)
        self.convert_position_combo(pos)
        self.convert_position_actions(pos)

    def convert_positions(self):
        for position in np.delete(str_positions, [3, 4]):
            self.convert_position(position)


class EmptyPositionError(Exception):
    pass
