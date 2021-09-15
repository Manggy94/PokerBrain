from file_reader import *

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
    def filter(hands):
        return np.array([hand for hand in hands if hand is not None])

    def to_pandas(self, hands: np.ndarray):
        hands = self.filter(hands)
        self.df = pd.DataFrame({"hand": hands})
        return self.df

    def load_hands(self, dir_name="history"):
        hands = self.parser.parse_directory(dir_name=dir_name)
        self.to_pandas(hands)
        self.convert_hand()
        self.filter_levels()
        return self.df

    @staticmethod
    def get_hand_info(hand: HandHistory):
        return {"tour_id": hand.tournament.id, "table_id": hand.table.ident, "level": hand.level.level,
                "bb": hand.level.bb, "ante": hand.level.ante, "max_pl": hand.table.max_players, "btn": hand.button,
                "buyin": hand.tournament.buyin}

    def get_hand_id(self, hand: HandHistory):
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
    def get_table_id(hand: HandHistory):
        return hand.table.ident

    def convert_table_id(self):
        vfunc = np.vectorize(self.get_table_id)
        self.df["table_id"] = vfunc(self.df["hand"])

    @staticmethod
    def get_tournament_id(hand: HandHistory):
        return hand.tournament.id

    def convert_tournament_id(self):
        vfunc = np.vectorize(self.get_tournament_id)
        self.df["tour_id"] = vfunc(self.df["hand"])

    @staticmethod
    def get_level(hand: HandHistory):
        return hand.level.level

    def convert_level(self):
        vfunc = np.vectorize(self.get_level)
        self.df["level"] = vfunc(self.df["hand"])

    @staticmethod
    def get_bb(hand: HandHistory):
        return hand.level.bb

    def convert_bb(self):
        vfunc = np.vectorize(self.get_bb)
        self.df["bb"] = vfunc(self.df["hand"])

    @staticmethod
    def get_ante(hand: HandHistory):
        return hand.level.ante

    def convert_ante(self):
        vfunc = np.vectorize(self.get_ante)
        self.df["ante"] = vfunc(self.df["hand"])

    @staticmethod
    def get_hero(hand: HandHistory):
        try:
            return hand.table.hero
        except TypeError:
            print(hand.table)

    def get_hero_combo(self, hand: HandHistory):
        try:
            hero = self.get_hero(hand)
            return hero.combo
        except AttributeError:
            return None
        except TypeError:
            return None

    def get_hero_combo_str(self, hand: HandHistory):
        try:
            combo = self.get_hero_combo(hand)
            return str(combo)
        except AttributeError:
            return str(None)
        except TypeError:
            return str(None)

    def get_hero_first_suit(self, hand: HandHistory):
        try:
            combo = self.get_hero_combo(hand)
            return str(combo.first.suit)
        except AttributeError:
            return None
        except TypeError:
            return None

    def get_hero_second_suit(self, hand: HandHistory):
        try:
            combo = self.get_hero_combo(hand)
            return str(combo.second.suit)
        except AttributeError:
            return None
        except TypeError:
            return None

    def get_hero_first_rank(self, hand: HandHistory):
        try:
            combo = self.get_hero_combo(hand)
            return str(combo.first.rank)
        except AttributeError:
            return str(None)
        except TypeError:
            return str(None)

    def get_hero_second_rank(self, hand: HandHistory):
        try:
            combo = self.get_hero_combo(hand)
            return str(combo.second.rank)
        except AttributeError:
            return None
        except TypeError:
            return None

    def convert_hero_combo(self):
        vfunc = np.vectorize(self.get_hero_combo_str)
        vfunc_fs = np.vectorize(self.get_hero_first_suit)
        vfunc_ss = np.vectorize(self.get_hero_second_suit)
        vfunc_fr = np.vectorize(self.get_hero_first_rank)
        vfunc_sr = np.vectorize(self.get_hero_second_rank)
        self.df["hero_combo"] = vfunc(self.df["hand"])
        self.df["hero_first_suit"] = vfunc_fs(self.df["hand"])
        self.df["hero_second_suit"] = vfunc_ss(self.df["hand"])
        self.df["hero_first_rank"] = vfunc_fr(self.df["hand"])
        self.df["hero_second_rank"] = vfunc_sr(self.df["hand"])

    def get_hero_seat(self, hand: HandHistory):
        try:
            hero = self.get_hero(hand)
            return hero.seat
        except AttributeError:
            return 0

    def convert_hero_seat(self):
        vfunc = np.vectorize(self.get_hero_seat)
        self.df["hero_seat"] = vfunc(self.df["hand"])

    @staticmethod
    def get_max_pl(hand: HandHistory):
        return hand.table.max_players

    def convert_max_pl(self):
        vfunc = np.vectorize(self.get_max_pl)
        self.df["max_pl"] = vfunc(self.df["hand"])

    @staticmethod
    def get_btn(hand: HandHistory):
        return hand.button

    def convert_btn(self):
        vfunc = np.vectorize(self.get_btn)
        self.df["btn"] = vfunc(self.df["hand"])

    @staticmethod
    def get_buyin(hand: HandHistory):
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
    def get_card(hand: HandHistory, index: int):
        try:
            return hand.table.board[index]
        except IndexError:
            return None

    def get_card_str(self, hand: HandHistory, index: int):
        try:
            card = self.get_card(hand, index)
            return str(card)
        except AttributeError:
            return "None"

    def get_card_rank(self, hand: HandHistory, index: int):
        try:
            card = self.get_card(hand, index)
            return str(card.rank)
        except AttributeError:
            return "None"

    def get_card_suit(self, hand: HandHistory, index: int):
        try:
            card = self.get_card(hand, index)
            return str(card.suit)
        except AttributeError:
            return "None"

    def convert_board(self):
        vfunc = np.vectorize(self.get_card)
        vfunc_rank = np.vectorize(self.get_card_rank)
        vfunc_suit = np.vectorize(self.get_card_suit)
        for i in range(5):
            self.df[f"Card_{i}"] = vfunc(self.df["hand"], i)
            self.df[f"Card_{i}_rank"] = vfunc_rank(self.df["hand"], i)
            self.df[f"Card_{i}_suit"] = vfunc_suit(self.df["hand"], i)

    @staticmethod
    def get_player(hand: HandHistory, index: int):
        try:
            return hand.table.players.pl_list[index]
        except IndexError:
            return None

    def get_player_name(self, hand: HandHistory, index: int):
        try:
            player = self.get_player(hand, index)
            return player.name
        except AttributeError:
            return "None"

    def convert_player_name(self, index: int):
        vfunc = np.vectorize(self.get_player_name)
        self.df[f"P{index}_name"] = vfunc(self.df["hand"], index)

    def get_player_seat(self, hand: HandHistory, index: int):
        try:
            player = self.get_player(hand, index)
            return player.seat
        except AttributeError:
            return 0

    def convert_player_seat(self, index: int):
        vfunc = np.vectorize(self.get_player_seat)
        self.df[f"P{index}_seat"] = vfunc(self.df["hand"], index)

    def get_player_stack(self, hand: HandHistory, index: int):
        try:
            player = self.get_player(hand, index)
            return player.init_stack
        except AttributeError:
            return 0

    def convert_player_stack(self, index: int):
        vfunc = np.vectorize(self.get_player_stack)
        self.df[f"P{index}_stack"] = vfunc(self.df["hand"], index)

    def get_player_position(self, hand: HandHistory, index: int):
        try:
            player = self.get_player(hand, index)
            return str(player.position)
        except AttributeError:
            return str(None)

    def convert_player_position(self, index: int):
        vfunc = np.vectorize(self.get_player_position)
        self.df[f"P{index}_position"] = vfunc(self.df["hand"], index)

    def get_player_combo(self, hand: HandHistory, index: int):
        try:
            player = self.get_player(hand, index)
            return player.combo
        except AttributeError:
            return None

    def get_player_combo_str(self, hand: HandHistory, index: int):
        try:
            combo = self.get_player_combo(hand=hand, index=index)
            return str(combo)
        except AttributeError:
            return str(None)

    def convert_player_combo(self, index: int):
        vfunc = np.vectorize(self.get_player_combo_str)
        self.df[f"P{index}_combo"] = vfunc(self.df["hand"], index)

    def convert_player(self, index: int):
        self.convert_player_name(index)
        self.convert_player_stack(index)
        self.convert_player_seat(index)
        self.convert_player_position(index)
        self.convert_player_combo(index)

    def convert_players(self):
        for i in range(9):
            self.convert_player(i)

    def get_action(self, hand, street_index: int, action_index: int):
        try:
            street = self.get_street(hand=hand, index=street_index)
            return street.actions[action_index]
        except IndexError:
            return None
        except AttributeError:
            return None

    def get_action_seat(self, hand, street_index: int, action_index: int):
        try:
            action = self.get_action(hand, street_index=street_index, action_index=action_index)
            return action.player.seat
        except AttributeError:
            return 0

    def convert_action_seat(self, street_index: int, action_index: int):
        tab = ["pf", "flop", "turn", "river"]
        vfunc = np.vectorize(self.get_action_seat)
        self.df[f"{tab[street_index]}_action_{action_index}_seat"] = vfunc(self.df["hand"], street_index, action_index)

    def get_action_move(self, hand, street_index: int, action_index: int):
        try:
            action = self.get_action(hand, street_index=street_index, action_index=action_index)
            return str(action.move)
        except AttributeError:
            return str(None)

    def convert_action_move(self, street_index: int, action_index: int):
        tab = ["pf", "flop", "turn", "river"]
        vfunc = np.vectorize(self.get_action_move)
        self.df[f"{tab[street_index]}_action_{action_index}_move"] = vfunc(self.df["hand"], street_index, action_index)

    def get_action_value(self, hand, street_index: int, action_index: int):
        try:
            action = self.get_action(hand, street_index=street_index, action_index=action_index)
            return action.value
        except AttributeError:
            return 0

    def convert_action_value(self, street_index: int, action_index: int):
        tab = ["pf", "flop", "turn", "river"]
        vfunc = np.vectorize(self.get_action_value)
        self.df[f"{tab[street_index]}_action_{action_index}_value"] = vfunc(self.df["hand"], street_index, action_index)

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
    def get_street(hand: HandHistory, index: int):
        try:
            return hand.table.streets[index]
        except IndexError:
            return None

    def convert_hand(self):
        self.convert_hand_info()
        self.convert_players()
        self.convert_board()
        self.convert_hand_actions()

    def filter_levels(self):
        self.df = self.df[self.df["level"] < 100]

    @staticmethod
    def get_idents(hands):
        return pd.Index([hand.hand_id for hand in hands])
