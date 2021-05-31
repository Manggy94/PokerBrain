from API.card import *
import treys

class Evaluator:

    def __init__(self):
        self.evaluator=treys.Evaluator()

    def transform_card(self,card):
        return treys.Card.new(str(card))

    def transform_cards(self,cards):
        array=[]
        for card in cards:
            array.append(self.transform_card(card))
        return array

    def evaluate(self,hand,board):
        return (self.evaluator.evaluate(hand, board))

    def get_rank(self,hand,board):
        score=self.evaluate(hand,board)
        return self.evaluator.get_rank_class(score)

    def get_combination(self,hand,board):
        rank=self.get_rank(hand,board)
        return self.evaluator.class_to_string(rank)

As=Card("As")
Ks=Card("Ks")
Qs=Card("Qs")
Js=Card("Js")
Ts=Card("Ts")
Ad=Card("Ad")
Kd=Card("Kd")
Qd=Card("Qd")
Ac=Card("Ac")
Ah=Card("Ah")
Th=Card("Th")
Qc=Card("Qc")

hand1=[Ah,Ac]
hand2=[Ks,Qs]
flop=[As, Ad, Js]
turn=Qd
river=Ts

Eva=Evaluator()
h1=Eva.transform_cards(hand1)
h2=Eva.transform_cards(hand2)
board=Eva.transform_cards(flop)
print (h1)
print(h2)
print (board)
print(Eva.get_combination(h1, board))
print(Eva.get_combination(h2, board))
board.append(Eva.transform_card(turn))
print(Eva.get_combination(h1, board))
print(Eva.get_combination(h2, board))
board.append(Eva.transform_card(river))
print(Eva.get_combination(h1, board))
print(Eva.get_combination(h2, board))


