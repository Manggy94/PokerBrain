import numpy as np

import API.constants as cst
import API.Range
from file_reader import *
from API.timer import Timer

all_actions = np.array(list(cst.Action))
all_positions = np.array(list(Position))
all_combos = API.Range.all_combos


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


def combo_to_int(combo: Combo):
    try:
        return np.where(all_combos == combo)[0][0]
    except:
        return len(all_combos)


def int_to_combo(k: int):
    return all_combos[k]


def sparse_int(k: int, n: int = 1326):
    sparsed = np.zeros(n)
    sparsed[k] = 1
    return sparsed


def sparse_combo(combo: Combo):
    return sparse_int(combo_to_int(combo))

def unsparse_range(sparsed: np.ndarray):
    combo_range=[]
    for i in range(len(sparsed)):
        if sparsed[i] ==1:
            combo_range.append(int_to_combo(i))
    return np.array(combo_range)


def card_to_int(card):
    return np.where(np.array(list(Card)) == card)[0][0]


def get_table_players(hand):
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


def get_heros_combo(table):
    try:
        return table.get_hero().combo
    except:
        pass


def get_street_actions(street):
    """"""
    ext = np.array([])
    actions = street.actions
    for i in range(24):
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
    return ext


def get_prev_streets(table, street):
    pf = get_street_actions(table.PF)
    flop = get_street_actions(table.F)
    turn = get_street_actions(table.T)
    river = get_street_actions(table.R)
    board = table.board
    c1 = card_to_int(board[0])
    c2 = card_to_int(board[1])
    c3 = card_to_int(board[2])
    c4 = card_to_int(board[3])
    c5 = card_to_int(board[4])

    if street.name == 'PF':
        flop = turn = river = np.zeros(72)
        c1 = c2 = c3 = c4 = c5 = len(list(Card))
    elif street.name == 'F':
        turn = river = np.zeros(72)
        c4 = c5 = len(list(Card))
    elif street.name == 'T':
        river = np.zeros(72)
        c5 = len(list(Card))
    ext = np.hstack((pf, flop, turn, river, c1, c2, c3, c4, c5))
    # print(ext.shape)
    return ext


def to_vec(player, hand, street):
    """
    Transforms information about a player that went to Showdown into an Input vector that can be used in TF
    This key function is to be modified to add features that are going to be used in our Model input
    :param player: Player that Went to SD and Whose we want to guess the range
    :param hand: WinamaxHandHistory.
    :param street: Table Street we want to stop to.
    :return: Numpy Vector
    """
    timer = Timer()
    timer.start()
    # Get target from player combo
    yi = sparse_combo(player.combo)
    # Create a vector
    xi = np.array([])
    # print(vect.shape, "A l'initialisation")
    # define some parameters
    table = hand.table
    level = hand.level
    # Add the name of the player at stake and add it to vector
    pl_name = name_to_array(player.name)
    # print(pl_name)
    xi = np.hstack((xi, pl_name))
    # print(vect.shape, "Après ajout du nom")
    # Get heros combo
    combo = get_heros_combo(table)
    xi = np.hstack((xi, combo_to_int(combo)))
    # print(vect.shape, "Après ajout du combo du héros")
    # Get the number of players involved
    xi = np.hstack((xi, table.max_players, len(table.players)))
    # print(vect.shape, "Après ajout du nombre de joueurs max et présents")
    # Get players information
    xi = np.hstack((xi, get_table_players(hand)))
    # print(vect.shape, "Après ajout des joueurs")
    # Get level information
    xi = np.hstack((xi, level.nb, level.ante, level.sb, level.bb))
    # print(vect.shape, "Après ajout des infos du niveau")
    # Get streets information
    xi = np.hstack((xi, get_prev_streets(table, street)))
    # print(vect.shape, "Après ajout des streets")

    return xi, yi


def multi_to_vec(player, hand):
    """

    :param player:player whose we want to predict hand
    :param hand:
    :return:
    """
    # print(type(to_vec(player, hand, hand.table.PF)))
    (pf_xi, pf_yi) = to_vec(player, hand, hand.table.PF)
    # print(pf_array.shape)
    (f_xi, f_yi) = to_vec(player, hand, hand.table.F)
    # print(f_array.shape)
    (t_xi, t_yi) = to_vec(player, hand, hand.table.T)
    # print(t_array.shape)
    (r_xi, r_yi) = to_vec(player, hand, hand.table.R)
    # print(r_array.shape)
    array_xi = np.vstack((pf_xi, f_xi, t_xi, r_xi))
    array_yi = np.vstack((pf_yi, f_yi, t_yi, r_yi))
    return array_xi, array_yi


def hand_to_vecs(hand):
    """

    :param hand:
    :return:
    """
    # timer=Timer()
    # timer.start()
    x, y = np.array([]), np.array([])
    players = hand.table.SD.active_players
    for player in players:
        if player.has_combo():
            (a, b) = multi_to_vec(player, hand)
            try:
                x, y = np.vstack((x, a)), np.vstack((y, b))
            except:
                x, y = a, b
    # print(vecs.shape, targets.shape)
    # timer.stop()
    return x, y


def vectorize(rep_name="history"):
    timer = Timer()

    finished_hands = parse_finished_hands(rep_name)
    timer.start()
    features = target = np.array([])
    for hand in finished_hands:
        if features.shape[0]<6000:
            a, b = hand_to_vecs(hand)
            if a.shape != (0, ):
                try:
                    features, target = np.vstack((features, a)), np.vstack((target, b))
                except:
                    features, target = a, b
            # print(features.shape, target.shape)
    timer.stop()
    return features, target


# vecs, targets = vectorize("history")
# print(vecs.shape, targets.shape)
