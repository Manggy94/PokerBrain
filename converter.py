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


def name_to_array(player_name):
    """Converts a player name into a 12-sized array to be recognized easily in Tensorflow"""
    name_byte = player_name.encode(encoding='ASCII')
    tab = np.zeros(12)
    for i in range(12):
        try:
            tab[i] = name_byte[i]
        except:
            tab[i] = 0
    return tab

def card_to_int(card: Card):
    try:
        return np.where(all_cards == card)[0][0]
    except:
            return all_cards.size

def board_to_int(board):
    int_board = []
    for i in range(5):
        try:
            int_board.append(card_to_int(board[i]))
        except:
            int_board.append(52)
    return int_board


def combo_to_int(combo: Combo):
    try:
        return np.where(all_combos == combo)[0][0]
    except:
        return all_combos.size


def int_to_combo(k: int):
    if k<1326:
        return all_combos[k]
    else:
        return None


def sparse_int(k: int, n: int = 1326):
    sparsed = np.zeros(n)
    sparsed[k] = 1
    return sparsed


def sparse_combo(player: Player, table: Table):
    if player.combo == None:
        return sparse_unknown_combo(table)
    else:
        return sparse_int(combo_to_int(player.combo))


def unsparse_range(sparsed: np.ndarray):
    combo_range=[]
    for i in range(sparsed.size):
        if sparsed[i] ==1:
            combo_range.append(int_to_combo(i))
    return np.array(combo_range)


def get_table_players(hand: WinamaxHandHistory):
    """
    Getting Preflop information about each player on a basis of a 10-rounded table.
    Information about player's name, position on the table, seat and initial stack.
    Converted to floats for usage in Tensorflow
    :param hand: WinamaxHandHistory
    :return: list
    """
    a = np.array([])
    players = hand.table.players
    for i in range(9):
        try:
            pl = players[i]
            name = name_to_array(pl.name)
            pos = np.where(all_positions == pl.position)[0][0]
            seat = pl.seat
            init = pl.init_stack
        except:
            name = np.zeros(12)
            pos = init = seat = 0
        a = np.hstack((a, name, pos, init, seat))
    return a


def get_street_actions(street: Street, n: int = 24):
    """"""
    ext = np.array([])
    actions = street.actions
    for i in range(n):
        try:
            action = actions[i]
            pl = action.player
            seat = pl.seat
            move = cst.Action(action.move)
            move = np.where(all_actions == move)[0][0]+1
            value = action.value
        except:
            seat = move = value = 0
        ext = np.hstack((ext, seat, move, value))
    ext = np.hstack((ext, np.zeros(72-3*n)))
    return ext


def get_previous_actions(table, street, n: int=24):

    # First we define an empty np.array for actions (and card)
    actions = np.array([])
    # Then two running variables i and k are defined to describe every step of the hand
    i = street.index
    k = n
    # This while keeps going for every known step
    while(i, k) != (0, 0):
        # Extension np.array
        ext = np.array([])
        # For every previous street, compute vector for street actions and add it to extension
        for j in range(i):
            res = get_street_actions(table.streets[j])
            if ext.shape[0] == 0:
                ext = res
            else:
                ext = np.hstack((ext, res))
        # Compute current street and add it to extension
        current = get_street_actions(table.streets[i], k)
        if ext.shape[0] == 0:
            ext = current
        else:
            ext = np.hstack((ext, current))
        ext = np.hstack((ext, np.zeros(72*(3-i))))
        # Transform board cards and add it to extension
        int_board = board_to_int(table.board)
        if i == 0:
            board = 52 * np.ones(5)
        else:
            board = np.hstack((int_board[:i + 2], 52 * np.ones(3 - i)))
        ext = np.hstack((ext, board))
        # Add extension to actions
        if actions.shape[0] == 0:
            actions = ext
        else:
            actions = np.vstack((actions, ext))
        # Modify i and k to keep running
        if k > 0:
            k -= 1
        elif i > 0:
            i -= 1
            k = 24
    return actions


hands = parse_file("historyexample2.txt")
#hands=parse_finished_hands("history2")
#hands = parse_directory("history2")
print(hands.shape)

hand=hands[2]
print(hand.table.streets)
#print(hand.table.streets[0].active_players)
player=hand.table.players[0]
#print(combo_to_int(player.combo))
#print(get_previous_actions(hand.table, hand.table.streets[3]).shape)

def player_history_to_vec(player: Player, hand: WinamaxHandHistory):
    """
    Transforms information about a player into an Input vector that can be used in TF
    This key function is to be modified to add features that are going to be used in our Model input
    :param player:
    :param hand:
    :return:
    """
    #timer = Timer()
    #timer.start()
    vec = np.array([])
    # define some parameters
    table = hand.table
    last_street = table.streets[min(table.progression, 3)]
    n = len(last_street.actions)
    level = hand.level
    # Get target from player combo
    yi = sparse_combo(player, table)
    # Create a vector
    player_info = np.array([])
    # Get the name of the player at stake
    pl_name = name_to_array(player.name)
    # Get hero's combo
    int_combo = combo_to_int(table.hero.combo)
    # Get the number of players involved
    max_players, players_nb = table.max_players, len(table.players)
    # Get players information
    players = get_table_players(hand)
    # Get level information
    level_nb, ante, sb, bb = level.nb, level.ante, level.sb, level.bb
    player_info = np.hstack((
        player_info,
        pl_name,
        int_combo,
        max_players,
        players_nb,
        players,
        level_nb,
        ante,
        sb,
        bb
    ))
    # Get streets information
    all_actions = get_previous_actions(table=table, street=last_street, n=n)
    for action_sample in all_actions:
        ext = np.hstack((player_info, action_sample))
        if vec.shape[0] == 0:
            vec = ext
        else:
            vec = np.vstack((vec, ext))
    p = vec.shape[0]
    target = np.ones((p,1))*yi
    #timer.stop()
    return vec, target


a, b = player_history_to_vec(player,hand)
print(a.shape, b.shape)


def hand_to_vecs(hand, showdown_only: bool = True):
    """
    :param hand:
    :return:
    """
    # timer=Timer()
    # timer.start()
    x, y = np.array([]), np.array([])
    if showdown_only:
        try:
            players = hand.table.streets[4].active_players
        except:
            return np.array([])
    else:
        players = hand.table.players
    for player in players:
        a, b = player_history_to_vec(player, hand)
        if x.size == 0:
            x, y = a, b
        else:
            x, y = np.vstack((x, a)), np.vstack((y, b))
    # timer.stop()
    return x, y

def vectorize_file(file_name: str, showdown_only: bool=True, limit: int=math.inf):

    features = targets = np.array([])
    hands = parse_file(file_name)
    for hand in hands:
        if features.shape[0] > limit:
            break
        a, b = hand_to_vecs(hand, showdown_only)
        if features.size == 0:
            features, targets = a, b
        else:
            features, targets = np.vstack((features, a)), np.vstack((targets, b))
    return features, targets



def vectorize_dir(dir_name: str="history", showdown_only: str=True, limit: int=math.inf ):
    # timer = Timer()
    hands = parse_directory(dir_name)
    # timer.start()
    features = targets = np.array([])
    count_hands = 0
    for hand in hands:
        count_hands+=1
        if features.shape[0] > limit:
            break
        a, b = hand_to_vecs(hand, showdown_only)
        if features.size == 0:
            features, targets = a, b
        else:
            features, targets = np.vstack((features, a)), np.vstack((targets, b))
    # timer.stop()
    print(count_hands)
    return features, targets

feat, tar = vectorize_dir(dir_name="history2", showdown_only=False, limit=400)
print(feat.shape)


class Converter:
    def __init__(self):
        pass


# vecs, targets = vectorize("history")
# print(vecs.shape, targets.shape)
