import unittest
import numpy as np
from file_reader import FileReader, FileParser


class MyTestCase(unittest.TestCase):

    def setUp(self):
        file = open(f"historyexample.txt", "r")
        self.text = file.read()
        file.close()
        self.FR = FileReader()
        self.FP = FileParser()
        self.raw_array = self.FR.split_raw_file(self.text)
        self.hand_txt_0 = self.raw_array[0]
        self.hand_array = self.FR.split_raw_hand(self.hand_txt_0)
        self.header_txt_0 = self.hand_array[0]

    def test_read_file(self):
        self.assertIsInstance(self.text, str)

    def test_split_raw_file(self):
        self.assertIsInstance(self.raw_array, np.ndarray)
        self.assertIsInstance(self.hand_txt_0, str)

    def test_split_raw_hand(self):
        self.assertIsInstance(self.hand_array, np.ndarray)

    def test_floatify(self):
        text_nb = "124"
        float_nb = self.FR.floatify(text_nb)
        self.assertIsInstance(float_nb, float)
        self.assertEqual(float_nb, 124.0)

    def test_parse_pk_type(self):
        pktype = self.FP.parse_pk_type(self.header_txt_0)
        self.assertEqual(pktype, "Tournament")
        self.assertIsInstance(pktype, str)

    def test_parse_tournament_name(self):
        tournament_name = self.FP.parse_tournament_name(self.header_txt_0)
        self.assertEqual(tournament_name, "Hold'em")
        self.assertIsInstance(tournament_name, str)

    def test_buyin_parse(self):
        result = self.FP.parse_buyin(self.header_txt_0)
        self.assertIsInstance(result, float)
        self.assertEqual(result, 0.9)




if __name__ == '__main__':
    unittest.main()
