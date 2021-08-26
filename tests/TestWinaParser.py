import unittest
# import numpy as np
import numpy as np

from file_reader import *
import sys


sys.path.append("..")

FP = FileParser()
files = FP.get_holdem_game_files("history")
tour_file = files[10]
tour = open(f"{FP.root}/history/{tour_file}", "r")
tour_content = tour.readlines()
tour.close()
tour = open(f"../history/{tour_file}", "r")
tour_text = tour.read()
tour.close()
freeroll_file = files[0]
freeroll = open(f"../history/{freeroll_file}", "r", encoding="utf-8")
freeroll_content = freeroll.readlines()
freeroll.close()
freeroll = open(f"../history/{freeroll_file}", "r", encoding="utf-8")
freeroll_text = freeroll.read()
freeroll.close()


class TestParser(unittest.TestCase):

    def setUp(self):
        self.dir_name = "history"
        self.FP = FileParser()
        self.files = self.FP.get_holdem_game_files(self.dir_name)
        self.file_name = self.files[0]
        self.tour_content = tour_content
        self.tour_text = tour_text
        self.freeroll_text = freeroll_text
        self.freeroll_content = freeroll_content
        self.raw_array = self.FP.split_raw_file(self.tour_text)
        self.unsplitted_hand = self.raw_array[0]
        self.hand_array = self.FP.split_raw_hand(self.unsplitted_hand)

    def test_holdem_game_files_getter(self):
        self.assertGreater(len(self.files), 0)

    def test_holdem_summary_files_getter(self):
        summaries = self.FP.get_holdem_summary_files(self.dir_name)
        self.assertGreater(len(summaries), 0)

    def test_finds_files(self):
        file = open(f"../history/{self.file_name}", "r")
        content = file.readlines()
        file.close()
        length = len(content)
        self.assertIsInstance(content, list)
        self.assertGreater(length, 0)

    def test_pk_type_parse(self):
        result = self.FP.parse_pk_type(tour_content[0])
        self.assertIsInstance(result, str)

    def test_tournament_name_parse(self):
        result = self.FP.parse_tournament_name(self.tour_content[0])
        self.assertIsInstance(result, str)

    #def test_buyin_parse(self):
        #result = self.FP.parse_buyin(self.tour_content[0])
        # self.assertIsInstance(result, float)

    #def test_freeroll_parse(self):
        #r = self.FP.parse_freeroll_buyin(self.freeroll_content[0])
        # self.assertIsInstance(r, float)
        # self.assertEqual(r, 0)

    def test_entry_parse(self):
        r1 = self.FP.parse_entry(self.freeroll_content[0])
        r2 = self.FP.parse_entry(self.tour_content[0])
        # self.assertIsInstance(r1, float)
        # self.assertEqual(r1, 0)
        # self.assertIsInstance(r2, float)

    def test_level_parse(self):
        result = self.FP.parse_level(self.tour_content[0])
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)

    def test_hand_id_parse(self):
        result = self.FP.parse_hand_id(tour_content[0])
        self.assertIsInstance(result, str)

    def test_blinds_parse(self):
        r = self.FP.parse_blinds(self.tour_content[0])
        ante, sb, bb = r["ante"], r["sb"], r["bb"]
        self.assertIsInstance(r, dict)
        self.assertIsInstance(ante, float)
        self.assertIsInstance(sb, float)
        self.assertIsInstance(bb, float)
        self.assertGreaterEqual(bb, sb)
        self.assertGreaterEqual(sb, ante)
        self.assertGreaterEqual(ante, 0)

    def test_table_parse(self):
        r = self.FP.parse_table(self.tour_text)
        tour_id = r["tour_id"]
        table_id = r["table_id"]
        max_seat = r["max_seat"]
        money_type = r["money_type"]
        btn = r["btn"]
        self.assertIsInstance(r, dict)
        self.assertIsInstance(tour_id, str)
        self.assertIsInstance(table_id, str)
        self.assertIsInstance(max_seat, int)
        self.assertIsInstance(money_type, str)
        self.assertIsInstance(btn, int)
        self.assertGreaterEqual(max_seat, 2)
        self.assertLess(max_seat, 10)
        self.assertLessEqual(btn, max_seat)
        self.assertGreaterEqual(btn, 0)

    def test_seat_parse(self):
        r = self.FP.parse_seat(self.tour_text)
        seat, pl_name, stack = r["seat"], r["pl_name"], r["stack"]
        self.assertIsInstance(r, dict)
        self.assertIsInstance(seat, int)
        self.assertIsInstance(pl_name, str)
        self.assertIsInstance(stack, float)

    def test_pot_parse(self):
        r = self.FP.parse_pot(self.tour_text)
        self.assertIsInstance(r, float)

    def test_ante_parse(self):
        r = self.FP.parse_ante(tour_text)
        if r:
            pl_name, amount = r["pl_name"], r["amount"]
            self.assertIsInstance(r, dict)
            self.assertIsInstance(pl_name, str)
            self.assertIsInstance(amount, float)

    def test_action_parse(self):
        r = self.FP.parse_action(tour_text)
        pl_name, move, value = r["pl_name"], r["move"], r["value"]
        self.assertIsInstance(r, dict)
        self.assertIsInstance(pl_name, str)
        self.assertIsInstance(move, cst.Action)
        self.assertIsInstance(value, float)

    def test_sd_action_parse(self):
        r = self.FP.parse_sd_action(tour_text)
        pl_name, move, c1, c2 = r["pl_name"], r["move"], r["c1"], r["c2"]
        self.assertIsInstance(r, dict)
        self.assertIsInstance(pl_name, str)
        self.assertIsInstance(move, str)
        self.assertIsInstance(c1, Card)
        self.assertIsInstance(c2, Card)

    def test_flop_parse(self):
        r = self.FP.parse_flop(tour_text)
        c1, c2, c3 = r["c1"], r["c2"], r["c3"]
        self.assertIsInstance(r, dict)
        self.assertIsInstance(c1, Card)
        self.assertIsInstance(c2, Card)
        self.assertIsInstance(c3, Card)

    def test_hero_parse(self):
        r = self.FP.parse_hero(tour_text)
        name, c1, c2 = r["name"], r["c1"], r["c2"]
        self.assertIsInstance(r, dict)
        self.assertIsInstance(name, str)
        self.assertIsInstance(c1, Card)
        self.assertIsInstance(c2, Card)

    def test_turn_parse(self):
        r = self.FP.parse_turn(tour_text)
        self.assertIsInstance(r, Card)

    def test_river_parse(self):
        r = self.FP.parse_river(tour_text)
        self.assertIsInstance(r, Card)

    def test_date_parse(self):
        r = self.FP.parse_date(tour_content[0])
        self.assertIsInstance(r, str)

    def test_sb_parse(self):
        r = self.FP.parse_sb(tour_text)
        pl_name, sb = r["pl_name"], r["sb"]
        self.assertIsInstance(r, dict)
        self.assertIsInstance(pl_name, str)
        self.assertIsInstance(r, dict)

    def test_bb_parse(self):
        r = self.FP.parse_bb(tour_text)
        pl_name, bb = r["pl_name"], r["bb"]
        self.assertIsInstance(r, dict)
        self.assertIsInstance(pl_name, str)
        self.assertIsInstance(bb, float)

    def test_winner_parse(self):
        r = self.FP.parse_winner(tour_text)
        pl_name, amount = r["pl_name"], r["amount"]
        self.assertIsInstance(r, dict)
        self.assertIsInstance(pl_name, str)
        self.assertIsInstance(amount, float)

    def test_file_splitter(self):
        raw = self.FP.split_raw_file(self.freeroll_text)
        self.assertIsInstance(raw, np.ndarray)
        self.assertIsInstance(raw[0], str)

    def test_split_hand(self):
        splitted = self.FP.split_raw_hand(self.unsplitted_hand)
        self.assertIsInstance(splitted, np.ndarray)

    def test_parse_hand(self):
        hh = self.FP.parse_hand(self.hand_array)
        self.assertIsInstance(hh, HandHistory)
        self.assertIsInstance(hh.hand_id, str)

    def test_parse_header(self):
        header = self.hand_array[0]
        header_info = self.FP.parse_header(header)
        self.assertIsInstance(header_info, dict)

    def test_parse_table(self):
        table = self.hand_array[1]
        table_info = self.FP.parse_table(table)
        self.assertIsInstance(table_info, dict)

    def test_create_tournament(self):
        header = self.hand_array[0]
        header_info = self.FP.parse_header(header)
        table = self.hand_array[1]
        table_info = self.FP.parse_table(table)
        tournament = self.FP.create_tournament(header_info=header_info, table_info=table_info)
        self.assertIsInstance(tournament, Tournament)

    def test_create_level(self):
        header = self.hand_array[0]
        header_info = self.FP.parse_header(header)
        level = self.FP.create_level(header_info=header_info)
        self.assertIsInstance(level, Level)

    def test_create_table(self):
        table_txt = self.hand_array[1]
        table_info = self.FP.parse_table(table_txt)
        table = self.FP.create_table(table_info)
        self.assertIsInstance(table, Table)

    def test_create_player(self):
        seat = self.hand_array[2]
        player = self.FP.create_player(seat_txt=seat)
        self.assertIsInstance(player, Player)

    def test_file_parser(self):
        hands = self.FP.parse_file(file_name=self.file_name)
        self.assertIsInstance(hands, np.ndarray)

    def test_directory_parser(self):
        hands = self.FP.parse_directory(dir_name=self.dir_name)
        self.assertIsInstance(hands, np.ndarray)

if __name__ == '__main__':
    unittest.main()
