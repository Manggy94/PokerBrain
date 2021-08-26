import math

import numpy as np
import pandas as pd

import API.constants as cst
import API.Range
from file_reader import *
from API.timer import Timer

all_actions = np.array(list(cst.Action))
all_positions = np.array(list(Position))
all_combos = API.Range.all_combos
all_streets = np.array(list(cst.Street))
all_cards = np.array(list(Card))

def sparse_unknown_combo(table):
    sparsed = 0.5*np.ones(1326)
    board = table.board
    tab = np.array(board)
    if table.hero !=None:
        hero_combo = table.hero.combo
        tab= np.hstack((tab,hero_combo.first, hero_combo.second))
    for i in range(1326):
        x = all_combos[i]
        c1, c2 = x.first, x.second
        if c1 in tab or c2 in tab:
            sparsed[i] = 0
    return sparsed


class HandConverter:

    def __init__(self):
        self.streets = ["pf", "flop", "turn", "river"]
        self.labels = ["seat", "move", "value"]
        self.txt_label = "move"
        self.val_labels = ["seat", "value"]
        self.ext_cols = ["%s_action_%s_%s" % (s, k, l) for s in self.streets for k in range(24) for l in self.labels]
        self.hero_cols = ["p%s_hero" % i for i in range(9)]
        self.combo_cols = ["p%s_combo" % i for i in range(9)]
        self.stack_cols = ["p%s_stack" % i for i in range(9)]
        self.street_val_cols = ["%s_action_%s_value" % (s, k) for s in self.streets for k in range(24)]
        self.val_cols = np.hstack((["bb", "ante", "buyin"], self.stack_cols, self.street_val_cols))
        self.current_df = None
        self.droppable_info = np.hstack((self.combo_cols, ["hand_id", "tournament_id", "table_id"]))

    def convert_board(self, hands):
        idents = [hand.ident for hand in hands]
        board = np.vstack([hand.table.get_total_board() for hand in hands])
        bd_columns = ["Card_0", "Card_1", "Card_2", "Card_3", "Card_4", ]
        boards = pd.DataFrame(data=board, index=idents, columns=bd_columns)
        return boards

    def convert_hands_info(self, hands):
        idents = [hand.ident for hand in hands]
        info = np.vstack([hand.get_hand_info() for hand in hands])
        hi_columns = ["tournament_id", "table_id", "level", "bb", "ante", "max_pl", "btn", "buyin", "hero_seat"
            , "hero_combo"]
        hand_info = pd.DataFrame(data=info, columns=hi_columns, index=idents)
        return hand_info

    def convert_players_info(self, hands):
        idents = [hand.ident for hand in hands]
        players_info = np.vstack([hand.get_all_players_info() for hand in hands])
        labels = ["name", "seat", "stack", "position", "combo", "hero"]
        pl_columns = np.array(["p%s_%s" % (i, l) for i in range(9) for l in labels])
        players = pd.DataFrame(data=players_info, columns=pl_columns, index=idents)
        return players

    def convert_hand_actions(self, hands):
        timer = Timer()
        timer.start()
        idents = [hand.ident for hand in hands]
        streets = ["pf", "flop", "turn", "river"]
        labels = ["seat", "move", "value"]
        act_columns = (np.array(["%s_action_%s_%s" % (s, j, l) for s in streets for j in range(24) for l in labels]))
        actions = np.vstack([hand.table.get_table_action_info() for hand in hands])
        act_frame = pd.DataFrame(data=actions, index=idents, columns=act_columns)
        timer.stop()
        return act_frame

    def complete_convert(self, hands):
        streets = ["pf", "flop", "turn", "river"]
        labels = ["seat", "move", "value"]
        act_columns = (np.array(["%s_action_%s_%s" % (s, j, l) for s in streets for j in range(24) for l in labels]))
        actions = np.vstack([hand.get_consecutive_actions()[0] for hand in hands])
        board = np.vstack([hand.get_consecutive_actions()[2] for hand in hands])
        idents = np.hstack([hand.get_consecutive_actions()[3] for hand in hands])
        infos = np.vstack([hand.get_consecutive_actions()[4] for hand in hands])
        pl_info = np.vstack([hand.get_consecutive_actions()[5] for hand in hands])
        act_frame = pd.DataFrame(data=actions, index=idents, columns=act_columns)
        bd_columns = ["Card_0", "Card_1", "Card_2", "Card_3", "Card_4", ]
        bd_frame = pd.DataFrame(data=board, index=idents, columns=bd_columns)
        hi_columns = ["tournament_id", "table_id", "level", "bb", "ante", "max_pl", "btn", "buyin"]
        hi_frame = pd.DataFrame(data=infos, columns=hi_columns, index=idents)
        pl_labels = ["name", "seat", "stack", "position", "combo", "hero"]
        pl_columns = np.array(["p%s_%s" % (i, l) for i in range(9) for l in pl_labels])
        pl_frame = pd.DataFrame(data=pl_info, columns=pl_columns, index=idents)
        # print(bd_frame, act_frame, hi_frame, pl_frame)
        df = pd.concat([hi_frame, pl_frame, act_frame, bd_frame], axis=1).reset_index().rename(columns={"index":"hand_id"})
        self.current_df = df
        return df

    def convert_hands(self, hands):
        pl_frame = self.convert_players_info(hands)
        hi_frame = self.convert_hands_info(hands)
        act_frame = self.convert_hand_actions(hands)
        bd_frame = self.convert_board(hands)
        df = pd.concat([hi_frame, pl_frame, act_frame, bd_frame], axis=1).reset_index().rename(columns={"index":"hand_id"})
        self.current_df = df
        return df

    def convert_single_hand(self, hand: WinamaxHandHistory):
        return self.convert_hands([hand])

    def get_hero_combo(self, line: int=0):
        try:
            #print([self.current_df[f"p{pl_index}_combo"].loc[line] for pl_index in range(9) if self.current_df[f"p{pl_index}_hero"].loc[line] == "True"][0])
            return [self.current_df[f"p{pl_index}_combo"].loc[line] for pl_index in range(9) if self.current_df[f"p{pl_index}_hero"].loc[line] == "True"][0]
        except IndexError:
            return None

    def transform_to_guess(self, pl_index: int, line: int=0):
        seat = self.current_df[f"p{pl_index}_seat"].loc[line]
        combo = self.current_df[f"p{pl_index}_combo"].loc[line]
        hero_combo = self.get_hero_combo(line)
        # print(hero_combo, combo)
        infos = self.current_df.iloc[line, :].drop(self.droppable_info)
        indexes = np.hstack((infos.index.to_numpy(), ["seat", "hero_combo"]))
        inf = np.hstack((infos.to_numpy(), [seat, hero_combo])).reshape(1,indexes.shape[0])
        infos = pd.DataFrame(columns=indexes, data=inf)
        combo = pd.Series({"combo":combo})
        return combo, infos


    def extract_player_infos(self, line: int=0):
        try:
            combos = pd.concat([self.transform_to_guess(pl_index=pl_index, line=line)[0] for pl_index in range(9)
                if self.transform_to_guess(pl_index=pl_index, line=line)[0]["combo"] not in [None, "None"]
            ])
            infos = pd.concat([
                self.transform_to_guess(pl_index=pl_index, line=line)[1] for pl_index in range(9)
                if self.transform_to_guess(pl_index=pl_index, line=line)[0]["combo"] not in [None, "None"]
            ], axis=0)
            #print(combos.shape, infos.shape)
            return combos, infos
        except ValueError:
            return None, None

    def extract_all_info(self):
        n = self.current_df.shape[0]
        combos = pd.concat([self.extract_player_infos(line=line)[0] for line in range(n)])
        infos = pd.concat([self.extract_player_infos(line=line)[1] for line in range(n)], axis=0)
        return combos, infos


