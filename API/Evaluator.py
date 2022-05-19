import pandas as pd

from API.Table import *
from API.card import *
from API.hand import *
import treys


class Evaluator:

    def __init__(self):
        #self.evaluator = treys.Evaluator()
        pass

    def evaluate(self, hand, board):
        try:
            return self.evaluator.evaluate(hand, board)
        except KeyError:
            return pd.NA

    @staticmethod
    def transform_card(card: Card):
        return treys.Card.new(f"{card}")

    def transform_board(self, board):
        return [self.transform_card(card) for card in board]

    def get_rank(self, hand, board):
        score = self.evaluate(hand, board)
        return self.evaluator.get_rank_class(score)

    def get_combination(self, hand, board):
        rank = self.get_rank(hand, board)
        return self.evaluator.class_to_string(rank)

    def transform_combo(self, combo: Combo):
        return [self.transform_card(combo.first), self.transform_card(combo.second)]

    def evaluate_combo(self, combo: Combo, board):
        hand = self.transform_combo(combo)
        bd = self.transform_board(board)
        return self.evaluate(hand=hand, board=bd)


class Simulator:

    def __init__(self):
        pass
