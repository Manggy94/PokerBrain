import unittest
from predictor import Predictor, CombosRange


class TestPredictor(unittest.TestCase):

    def setUp(self) -> None:
        self.pred = Predictor()

    def test_combos_range(self):
        print(self.pred.predict_combos())
        self.assertIsInstance(self.pred.predict_combos(), CombosRange)


if __name__ == '__main__':
    unittest.main()
