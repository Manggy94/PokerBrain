from file_reader import *
from tracker import PlayerHistory

all_actions = np.array(list(cst.Action))
all_positions = np.array(list(Position))
all_streets = np.array(list(cst.Street))
all_cards = np.array(list(Card))


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

    @staticmethod
    def filter(hands) -> np.ndarray:
        return np.array([hand for hand in hands if hand is not None])

    def to_pandas(self, hands: np.ndarray) -> pd.DataFrame:
        hands = self.filter(hands)
        self.df = pd.DataFrame({"hand": hands})
        return self.df

    def load_hands(self, dir_name="history") -> pd.DataFrame:
        hands = self.parser.parse_directory(dir_name=dir_name)
        self.to_pandas(hands)
        self.convert_hand()
        self.filter_levels()
        return self.df

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

    def convert_hand_id(self):
        vfunc = np.vectorize(self.get_hand_id)
        self.df["hand_id"] = vfunc(self.df["hand"])

    @staticmethod
    def get_table_id(hand: HandHistory) -> str:
        return hand.table.ident

    def convert_table_id(self):
        vfunc = np.vectorize(self.get_table_id)
        self.df["table_id"] = vfunc(self.df["hand"])

    @staticmethod
    def get_tournament_id(hand: HandHistory) -> str:
        return hand.tournament.id

    def convert_tournament_id(self):
        vfunc = np.vectorize(self.get_tournament_id)
        self.df["tour_id"] = vfunc(self.df["hand"])

    @staticmethod
    def get_level(hand: HandHistory) -> int:
        return hand.level.level

    def convert_level(self):
        vfunc = np.vectorize(self.get_level)
        self.df["level"] = vfunc(self.df["hand"])

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

    def get_hero_hand(self, hand: HandHistory) -> str:
        try:
            combo = self.get_hero_combo(hand)
            return f"{combo.to_hand()}"
        except AttributeError:
            return "None"

    def get_hero_first_suit(self, hand: HandHistory) -> str:
        try:
            combo = self.get_hero_combo(hand)
            return f"{combo.first.suit}"
        except AttributeError:
            return "None"
        except TypeError:
            return "None"

    def get_hero_second_suit(self, hand: HandHistory) -> str:
        try:
            combo = self.get_hero_combo(hand)
            return f"{combo.second.suit}"
        except AttributeError:
            return "None"
        except TypeError:
            return "None"

    def get_hero_first_rank(self, hand: HandHistory) -> str:
        try:
            combo = self.get_hero_combo(hand)
            return f"{combo.first.rank}"
        except AttributeError:
            return "None"
        except TypeError:
            return "None"

    def get_hero_second_rank(self, hand: HandHistory) -> str:
        try:
            combo = self.get_hero_combo(hand)
            return f"{combo.second.rank}"
        except AttributeError:
            return "None"
        except TypeError:
            return "None"

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

    def get_hero_seat(self, hand: HandHistory) -> int:
        try:
            hero = self.get_hero(hand)
            return hero.seat
        except AttributeError:
            return 0

    def convert_hero_seat(self):
        vfunc = np.vectorize(self.get_hero_seat)
        self.df["hero_seat"] = vfunc(self.df["hand"])

    @staticmethod
    def get_max_pl(hand: HandHistory) -> int:
        return hand.table.max_players

    def convert_max_pl(self):
        vfunc = np.vectorize(self.get_max_pl)
        self.df["max_pl"] = vfunc(self.df["hand"])

    @staticmethod
    def get_btn(hand: HandHistory) -> int:
        return hand.button

    def convert_btn(self):
        vfunc = np.vectorize(self.get_btn)
        self.df["btn"] = vfunc(self.df["hand"])

    @staticmethod
    def get_buyin(hand: HandHistory) -> float:
        return hand.tournament.buyin

    def convert_buyin(self):
        vfunc = np.vectorize(self.get_buyin)
        self.df["buyin"] = vfunc(self.df["hand"])

    def convert_hand_info(self):
        self.convert_hand_id()
        self.convert_tournament_id()
        self.convert_table_id()
        self.convert_level()
        self.convert_bb()
        self.convert_ante()
        self.convert_max_pl()
        self.convert_btn()
        self.convert_buyin()
        self.convert_hero_combo()
        self.convert_hero_seat()

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

    @staticmethod
    def get_player(hand: HandHistory, index: int) -> Player or None:
        try:
            return hand.table.players.pl_list[index]
        except IndexError:
            return None

    def get_player_name(self, hand: HandHistory, index: int) -> str:
        try:
            player = self.get_player(hand, index)
            return player.name
        except AttributeError:
            return "None"

    def convert_player_name(self, index: int):
        vfunc = np.vectorize(self.get_player_name)
        self.df[f"P{index}_name"] = vfunc(self.df["hand"], index)

    def get_player_history(self, hand: HandHistory, index: int, dir_name: str = "history2") -> PlayerHistory or None:
        try:
            player = self.get_player(hand, index)
            hist = PlayerHistory()
            hist.load_pl_hands(pl_name=player.name, dir_name=dir_name)
            return hist
        except AttributeError:
            return None

    def convert_player_history(self, index: int, dir_name: str):
        self.convert_player_played_hands(index)
        self.convert_player_vpip(index)
        self.convert_player_vpip(index)

    def get_player_played_hands(self, hand: HandHistory, index: int, dir_name: str = "history") -> int:
        try:
            hist = self.get_player_history(hand=hand, index=index, dir_name=dir_name)
            return hist.played
        except AttributeError:
            return 0

    def convert_player_played_hands(self, index: int):
        vfunc = np.vectorize(self.get_player_played_hands)
        self.df[f"P{index}_played"] = vfunc(self.df["hand"], index)

    def get_player_vpip(self, hand: HandHistory, index: int, dir_name: str = "history") -> float:
        try:
            hist = self.get_player_history(hand=hand, index=index, dir_name=dir_name)
            return hist.vpip
        except AttributeError:
            return 0

    def convert_player_vpip(self, index: int):
        vfunc = np.vectorize(self.get_player_vpip)
        self.df[f"P{index}_vpip"] = vfunc(self.df["hand"], index)

    def get_player_pfr(self, hand: HandHistory, index: int, dir_name: str = "history") -> float:
        try:
            hist = self.get_player_history(hand=hand, index=index, dir_name=dir_name)
            return hist.pfr
        except AttributeError:
            return 0

    def convert_player_pfr(self, index: int):
        vfunc = np.vectorize(self.get_player_pfr)
        self.df[f"P{index}_pfr"] = vfunc(self.df["hand"], index)

    def get_player_seat(self, hand: HandHistory, index: int) -> int:
        try:
            player = self.get_player(hand, index)
            return player.seat
        except AttributeError:
            return 0

    def convert_player_seat(self, index: int):
        vfunc = np.vectorize(self.get_player_seat)
        self.df[f"P{index}_seat"] = vfunc(self.df["hand"], index)

    def get_player_stack(self, hand: HandHistory, index: int) -> float:
        try:
            player = self.get_player(hand, index)
            return player.init_stack
        except AttributeError:
            return 0

    def convert_player_stack(self, index: int):
        vfunc = np.vectorize(self.get_player_stack)
        self.df[f"P{index}_stack"] = vfunc(self.df["hand"], index)
        self.df[f"P{index}_stack_bb"] = self.df[f"P{index}_stack"] / self.df[f"bb"]

    def get_player_position(self, hand: HandHistory, index: int) -> str:
        try:
            player = self.get_player(hand, index)
            return f"{player.position}"
        except AttributeError:
            return f"None"

    def convert_player_position(self, index: int):
        vfunc = np.vectorize(self.get_player_position)
        self.df[f"P{index}_position"] = vfunc(self.df["hand"], index)

    def get_player_combo(self, hand: HandHistory, index: int) -> Combo or None:
        try:
            player = self.get_player(hand, index)
            return player.combo
        except AttributeError:
            return None

    def get_player_combo_str(self, hand: HandHistory, index: int) -> str:
        try:
            combo = self.get_player_combo(hand=hand, index=index)
            return f"{combo}"
        except AttributeError:
            return f"None"

    def get_player_hand(self, hand: HandHistory, index: int) -> Hand or None:
        try:
            combo = self.get_player_combo(hand=hand, index=index)
            return combo.to_hand()
        except AttributeError:
            return None

    def get_player_hand_str(self, hand: HandHistory, index: int) -> str:
        try:
            card_hand = self.get_player_hand(hand=hand, index=index)
            return f"{card_hand}"
        except AttributeError:
            return f"None"

    def convert_player_combo(self, index: int):
        vfunc_combo = np.vectorize(self.get_player_combo_str)
        vfunc_hand = np.vectorize(self.get_player_hand_str)
        self.df[f"P{index}_combo"] = vfunc_combo(self.df["hand"], index)
        self.df[f"P{index}_hand"] = vfunc_hand(self.df["hand"], index)
        
    def get_player_action(self, hand: HandHistory, pl_index: int, act_index: int) -> Action or None:
        try:
            player = self.get_player(hand=hand, index=pl_index)
            return player.actions[act_index]
        except AttributeError:
            return None
        except IndexError:
            return None

    def get_player_action_street(self, hand: HandHistory, pl_index: int, act_index: int) -> str:
        try:
            action = self.get_player_action(hand=hand, pl_index=pl_index, act_index=act_index)
            return f"{action['street']}"
        except AttributeError:
            return f"None"
        except TypeError:
            return f"None"

    def get_player_action_move(self, hand: HandHistory, pl_index: int, act_index: int) -> str:
        try:
            action = self.get_player_action(hand=hand, pl_index=pl_index, act_index=act_index)
            return f"{action['move']}"
        except AttributeError:
            return f"None"
        except TypeError:
            return f"None"

    def get_player_action_value(self, hand: HandHistory, pl_index: int, act_index: int) -> float:
        try:
            action = self.get_player_action(hand=hand, pl_index=pl_index, act_index=act_index)
            return action['value']
        except AttributeError:
            return 0
        except TypeError:
            return 0

    def convert_player_action(self, pl_index: int, act_index: int):
        i, j = pl_index, act_index
        vfunc_street = np.vectorize(self.get_player_action_street)
        vfunc_move = np.vectorize(self.get_player_action_move)
        vfunc_value = np.vectorize(self.get_player_action_value)
        self.df[f"P{i}_action_{j}_street"] = vfunc_street(self.df["hand"], i, j)
        self.df[f"P{i}_action_{j}_move"] = vfunc_move(self.df["hand"], i, j)
        self.df[f"P{i}_action_{j}_value"] = vfunc_value(self.df["hand"], i, j)
        self.df[f"P{i}_action_{j}_value_bb"] = self.df[f"P{i}_action_{j}_value"] / self.df[f"bb"]

    def convert_player_actions(self, pl_index: int):
        for i in range(8):
            self.convert_player_action(pl_index=pl_index, act_index=i)

    def convert_player(self, index: int):
        self.convert_player_name(index)
        self.convert_player_stack(index)
        self.convert_player_seat(index)
        self.convert_player_position(index)
        self.convert_player_combo(index)
        self.convert_player_actions(pl_index=index)

    def convert_players(self):
        for i in range(9):
            self.convert_player(i)

    def get_action(self, hand, street_index: int, action_index: int) -> Action or SDAction or None:
        try:
            street = self.get_street(hand=hand, index=street_index)
            return street.actions[action_index]
        except IndexError:
            return None
        except AttributeError:
            return None

    def get_action_seat(self, hand, street_index: int, action_index: int) -> int:
        try:
            action = self.get_action(hand, street_index=street_index, action_index=action_index)
            return action.player.seat
        except AttributeError:
            return 0

    def convert_action_seat(self, street_index: int, action_index: int):
        tab = ["pf", "flop", "turn", "river"]
        vfunc = np.vectorize(self.get_action_seat)
        self.df[f"{tab[street_index]}_action_{action_index}_seat"] = vfunc(self.df["hand"], street_index, action_index)

    def get_action_move(self, hand, street_index: int, action_index: int) -> str:
        try:
            action = self.get_action(hand, street_index=street_index, action_index=action_index)
            return f"{action.move}"
        except AttributeError:
            return "None"

    def convert_action_move(self, street_index: int, action_index: int):
        tab = ["pf", "flop", "turn", "river"]
        vfunc = np.vectorize(self.get_action_move)
        self.df[f"{tab[street_index]}_action_{action_index}_move"] = vfunc(self.df["hand"], street_index, action_index)

    def get_action_value(self, hand, street_index: int, action_index: int) -> float:
        try:
            action = self.get_action(hand, street_index=street_index, action_index=action_index)
            return action.value
        except AttributeError:
            return 0

    def convert_action_value(self, street_index: int, action_index: int):
        i, j = street_index, action_index
        tab = ["pf", "flop", "turn", "river"]
        vfunc = np.vectorize(self.get_action_value)
        self.df[f"{tab[i]}_action_{j}_value"] = vfunc(self.df["hand"], i, j)
        self.df[f"{tab[i]}_action_{j}_value_bb"] = self.df[f"{tab[i]}_action_{j}_value"]/self.df[f"bb"]

    def convert_action(self, street_index: int, action_index: int):
        self.convert_action_seat(street_index, action_index)
        self.convert_action_move(street_index, action_index)
        self.convert_action_value(street_index, action_index)

    def convert_street_actions(self, street_index: int):
        for i in range(24):
            self.convert_action(street_index=street_index, action_index=i)

    def convert_hand_actions(self):
        for i in range(4):
            self.convert_street_actions(street_index=i)

    @staticmethod
    def get_street(hand: HandHistory, index: int) -> Street or None:
        try:
            return hand.table.streets[index]
        except IndexError:
            return None

    def convert_hand(self):
        self.convert_hand_info()
        self.convert_players()
        self.convert_board()
        self.convert_flop_info()
        # self.convert_hand_actions()

    def filter_levels(self):
        self.df = self.df[self.df["level"] < 100]

    @staticmethod
    def get_idents(hands) -> pd.Index:
        return pd.Index([hand.hand_id for hand in hands])
