import unittest


class TestTable(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


    def test_generate_board(self):
        tab2 = table.Table()
        tab2.draw_flop("As", "Ad", "Ah")
        new_board = tab2.generate_board()
        self.assertIsInstance(new_board, table.Board)
        self.assertEqual(new_board["flop_1"], "As")
        self.assertEqual(new_board["flop_2"], "Ad")
        self.assertEqual(new_board["flop_3"], "Ah")
        tab2.draw_turn("Kh")
        new_board = tab2.generate_board()
        self.assertEqual(new_board["flop_1"], "As")
        self.assertEqual(new_board["flop_2"], "Ad")
        self.assertEqual(new_board["flop_3"], "Ah")
        self.assertEqual(new_board["turn"], "Kh")
        boards = tab2.generate_boards(10)
        self.assertIsInstance(boards, np.ndarray)
        self.assertEqual(boards.shape, (10, 5))


if __name__ == '__main__':
    unittest.main()
