import unittest
import pandas as pd
from API.Table import CombosRange, str_combos


class TestCombosRange(unittest.TestCase):

    def setUp(self) -> CombosRange:
        self.combos_range = CombosRange()

    def test_is_DataFrame(self):
        self.assertIsInstance(self.combos_range, pd.DataFrame)

    def test_index(self):
        self.assertTrue((self.combos_range.index.to_numpy() == str_combos).all())

    def test_p_sum(self):
        self.assertEqual(self.combos_range["p"].sum(), 1)


if __name__ == '__main__':
    unittest.main()
