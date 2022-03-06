import numpy as np
import API.constants as cst
from API.card import Card
from API.hand import Hand

all_actions = np.hstack(list(cst.Action))
all_cards = np.hstack(list(Card))
all_combos = np.hstack([hand.to_combos() for hand in list(Hand)])
all_hands = np.hstack(list(Hand))
all_positions = np.hstack([position for position in list(cst.Position)])
all_streets = np.hstack(list(cst.Street))
str_actions = all_actions.astype(str)
str_positions = all_positions.astype(str)
str_combos = all_combos.astype(str)
str_hands = all_hands.astype(str)
str_streets = all_streets.astype(str)
