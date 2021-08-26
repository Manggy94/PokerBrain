import unittest
from file_reader import *

FP = FileParser()
files = FP.get_holdem_game_files("../history")
summaries = FP.get_holdem_summary_files("../history")
freeroll_file = files[0]
tour_file = files[100]
freeroll = open(f"../history/{freeroll_file}", "r", encoding="utf-8")
freeroll_content = freeroll.readlines()
freeroll.close()
freeroll = open(f"../history/{freeroll_file}", "r", encoding="utf-8")
freeroll_text = freeroll.read()
freeroll.close()
tour = open(f"../history/{tour_file}", "r")
tour_content = tour.readlines()
tour.close()
tour = open(f"../history/{tour_file}", "r")
tour_text = tour.read()
tour.close()
summary_file = summaries[0]
summary = open(f"../history/{summary_file}", "r", encoding="utf-8")
summary_text = summary.read()
summary.close()


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.freeroll_text = freeroll_text
        self.freeroll_content = freeroll_content
        self.tour_text = tour_text
        self.tour_content = tour_content
        self.FR = FP
        self.summary_text = summary_text

    def test_good_instance(self):
        self.assertIsInstance(self.FR, FileReader)

    def test_parser_regex(self):
        # print(f"{self.tour_content[2:10]}\n{self.freeroll_content[2:10]}")
        self.assertRegex(self.tour_content[0], self.FR._winamax_new_hand_re)
        self.assertRegex(self.tour_content[0], self.FR._pk_type)
        self.assertRegex(self.tour_content[0], self.FR._tournament_name_re)
        self.assertRegex(self.tour_content[0], self.FR._buyin_txt_re)
        self.assertRegex(self.freeroll_content[0], self.FR._freeroll_re)
        self.assertRegex(self.tour_content[0], self.FR._level_re)
        self.assertRegex(self.tour_content[0], self.FR._hand_id_re)
        self.assertRegex(self.tour_content[0], self.FR._blinds_re)
        self.assertRegex(self.tour_content[0], self.FR._date_re)
        self.assertRegex(self.tour_content[1], self.FR._table_re)

    def test_wina_new_hand_regex(self):
        self.assertRegex(self.tour_content[0], self.FR._winamax_new_hand_re)
        self.assertRegex(self.freeroll_content[0], self.FR._winamax_new_hand_re)

    def test_poker_type_regex(self):
        self.assertRegex(self.tour_content[0], self.FR._pk_type)
        self.assertRegex(self.freeroll_content[0], self.FR._pk_type)

    def test_poker_tour_name_regex(self):
        self.assertRegex(self.tour_content[0], self.FR._tournament_name_re)
        self.assertRegex(self.freeroll_content[0], self.FR._tournament_name_re)

    def test_buyin_regex(self):
        self.assertRegex(self.tour_content[0], self.FR._buyin_txt_re)

    def test_freeroll_regex(self):
        self.assertRegex(self.freeroll_content[0], self.FR._freeroll_re)

    def test_level_regex(self):
        self.assertRegex(self.tour_content[0], self.FR._level_re)
        self.assertRegex(self.freeroll_content[0], self.FR._level_re)

    def test_hand_id_regex(self):
        self.assertRegex(self.tour_content[0], self.FR._hand_id_re)
        self.assertRegex(self.freeroll_content[0], self.FR._hand_id_re)

    def test_blinds_regex(self):
        self.assertRegex(self.tour_content[0], self.FR._blinds_re)
        self.assertRegex(self.freeroll_content[0], self.FR._blinds_re)

    def test_date_regex(self):
        self.assertRegex(self.tour_content[0], self.FR._date_re)
        self.assertRegex(self.freeroll_content[0], self.FR._date_re)

    def test_table_regex(self):
        self.assertRegex(self.tour_content[1], self.FR._table_re)

    def test_seat_regex(self):
        self.assertRegex(self.tour_text, self.FR._seat_re)

    def test_pot_regex(self):
        self.assertRegex(self.tour_text, self.FR._pot_re)

    def test_ante_regex(self):
        self.assertRegex(self.tour_text, self.FR._ante_re)

    def test_board_regex(self):
        self.assertRegex(self.tour_text, self.FR._board_re)

    def test_action_regex(self):
        self.assertRegex(self.tour_text, self.FR._action_re)

    def test_fold_regex(self):
        self.assertRegex(self.tour_text, self.FR._action_2_re)

    def test_sd_action_regex(self):
        self.assertRegex(self.tour_text, self.FR._sd_action_re)

    def test_flop_regex(self):
        self.assertRegex(self.tour_text, self.FR._flop_re)

    def test_hero_regex(self):
        self.assertRegex(self.tour_text, self.FR._hero_re)

    def test_turn_regex(self):
        self.assertRegex(self.tour_text, self.FR._turn_re)

    def test_river_regex(self):
        self.assertRegex(self.tour_text, self.FR._river_re)

    def test_showdown_regex(self):
        self.assertRegex(self.tour_text, self.FR._showdown_re)

    def test_summary_regex(self):
        self.assertRegex(self.tour_text, self.FR._summary_re)

    def test_winner_regex(self):
        self.assertRegex(self.tour_text, self.FR._winner_re)

    def test_sb_regex(self):
        self.assertRegex(self.tour_text, self.FR._sb_re)

    def test_bb_regex(self):
        self.assertRegex(self.tour_text, self.FR._bb_re)

    def test_tour_name_regex(self):
        self.assertRegex(self.summary_text, self.FR._tour_name_re)

    def test_total_players_regex(self):
        self.assertRegex(self.summary_text, self.FR._total_players_re)

    def test_prizepool_regex(self):
        self.assertRegex(self.summary_text, self.FR._prizepool_re)

    def test_game_mode_regex(self):
        self.assertRegex(self.summary_text, self.FR._game_mode_re)

    def test_ttype_regex(self):
        self.assertRegex(self.summary_text, self.FR._ttype_re)

    def test_speed_regex(self):
        self.assertRegex(self.summary_text, self.FR._speed_re)

    def test_buyins_regex(self):
        self.assertRegex(self.summary_text, self.FR._buyin_re)

    def test_levels_regex(self):
        self.assertRegex(self.summary_text, self.FR._levels_re)


if __name__ == '__main__':
    unittest.main()
