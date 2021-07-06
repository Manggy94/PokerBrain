from winamax import *
from API.timer import Timer
import numpy as np
import pandas as pd
import os
import re

# route="C:\\Users\hp\Desktop\Poker\PokerBrain\history"


_split_re = re.compile(r"\*\*\*\s+\n?|\n\n+")
_header_re = re.compile(
    r"""
    Winamax\s+Poker\s+-\s+                                              #Winamax Poker
    (?P<poker_type>Tournament|CashGame)\s+                              #Poker Type
    \"(?P<tournament_name>.+)\"\s+                                      #Tournament Name
    buyIn\:\s+(?P<buyin>[0-9.,]+)â..\s+                                 #Buy In
    \+\s+(?P<rake>[0-9.,]+)â..\s+                                       #Rake
    level:\s+(?P<level>[\d\#]+)\s+                                      #level
    \-\s+HandId\:\s+                                                    
    \#(?P<Hand_id>[0-9-]+)\s+\-\s+                                      #Hand Id
    (?P<Variant>[A-Za-z ]+)\s+                                          #Variant
    \((?P<ante>\d+)\/                                                   #Ante
    (?P<small_blind>\d+)\/                                              #SB
    (?P<big_blind>\d+)\)\s+                                             #BB
    \-\s+(?P<date>.+)                                                   #Date
    """,
    re.VERBOSE,
)
_table_re = re.compile(
    r"Table\:\s+\'(?P<tournament_name>[\w\s\']+)\((?P<tournament_id>\d+)\)\#(?P<table_id>\d+)\'\s+(?P<max_seat>\d+)\-max\s+\((?P<money_type>[a-z]+)\s+money\)\s+Seat\s+\#(?P<button>\d)\s+is\s+the\s+button")
_seat_re = re.compile(r"Seat\s+(?P<seat>\d+)\:\s+(?P<player_name>[\w\s\-.]{3,12})\s\((?P<stack>\d+)\)")
_pot_re = re.compile(r"Total\s+pot\s+(?P<total_pot>\d+)")
_ante_re = re.compile(r"(?P<player_name>[\w\s\-.]{3,12})\s+posts\sante\s+(?P<amount>\d+)")
_board_re = re.compile(r"Board\:\s+\[(?P<board>[0-9AJKQshdc ]+)\]")
_action_re = re.compile(
    r"(?P<player_name>[\w\s\-.]{6,12})\s+(?P<move>shows|checks|calls|folds|bets|raises)\s+(?P<value>\d+||\s+)")
_showdown_action_re = re.compile(
    r"(?P<player_name>[\w\s\-.]{6,12})\s+(?P<move>shows|mucks)\s+\[(?P<card1>[AJKQ2-9shdc]{2})\s+(?P<card2>[AJKQ2-9shdc]{2})\]")
_flop_re = re.compile(
    r"\*\*\*\s+FLOP\s+\*\*\*\s+\[(?P<flop_card_1>[AJKQT2-9hscd]{2})\s+(?P<flop_card_2>[AJKQT2-9hscd]{2})\s+(?P<flop_card_3>[AJKQT2-9hscd]{2})\]")
_hero_cards_re = re.compile(
    r"Dealt\s+to\s+(?P<hero_name>[\w\s\-.]+)\s+\[(?P<card1>[AJKQT2-9hscd]{2})\s+(?P<card2>[AJKQT2-9hscd]{2})\]")
_turn_re = re.compile(r"\*\*\*\s+TURN\s+\*\*\*\s+\[.+\]\[(?P<turn_card>[AJKQT2-9hscd]{2})\]")
_river_re = re.compile(r"\*\*\*\s+RIVER\s+\*\*\*\s+\[.+\]\[(?P<river_card>[AJKQT2-9hscd]{2})\]")
_showdown_re = re.compile(r"\*\*\*\s+SHOW\s+DOWN\s+\*\*\*")
_summary_re = re.compile(r"\*\*\*\s+SUMMARY\s+\*\*\*")
_winner_re = re.compile(r"(?P<player_name>[\w\s\-.]{6,12})\s+collected\s+(?P<amount>\d+)\s+")
_sb_re = re.compile(r"(?P<player_name>[\w\s\-.]{3,12})\s+posts\s+small\s+blind\s+(?P<sb>\d+)")
_bb_re = re.compile(r"(?P<player_name>[\w\s\-.]{3,12})\s+posts\s+big\s+blind\s+(?P<bb>\d+)")
_tour_name_re = re.compile(r"Winamax\s+Poker\s+-\s+Tournament\s+summary\s+\:\s+"
                           r"(?P<tournament_name>.+)\((?P<tournament_id>\d+)\)")
_total_players_re = re.compile(r"Registered\s+players\s+\:\s+(?P<total_players>\d+)")
_prizepool_re = re.compile(r"Prizepool\s+\:\s+(?P<prizepool>[\d.]+)")
_game_mode_re = re.compile(r"Mode\s+.+\s+\:\s+(?P<game_mode>.+)")
_ttype_re = re.compile(r"Type\s+\:\s+(?P<game_mode>.+)")
_speed_re = re.compile(r"Speed\s+\:\s+(?P<speed>.+)")
_buyin_re = re.compile(r"Buy-In\s+\:\s+(?P<buyin>[\d.]+)")
_levels_re = re.compile(r"Levels\s+\:\s+\[(?P<levels>.+)\]")

def parse_summary(file_name: str):
    file = open("history/%s" % file_name, "r")
    content = file.read()
    #print(content)
    match1 = re.search(_tour_name_re, content)
    match2 = re.search(_total_players_re, content)
    match3 = re.search(_ttype_re, content)
    match4 = re.search(_prizepool_re, content)
    match5 = re.search(_speed_re, content)
    match6 = re.search(_buyin_re, content)
    match7 = re.search(_levels_re, content)
    tour_name, tour_id = match1.group("tournament_name"), int(match1.group("tournament_id"))
    tot_players = int(match2.group("total_players"))
    game_mode = match3.group("game_mode")
    prizepool = floatify(match4.group("prizepool"))
    speed = match5.group("speed")
    buyin = floatify(match6.group("buyin"))
    levels_string = (match7.group("levels"))
    levels = re.split(":holdem-no-limit,", levels_string)
    level = re.split("[\-\:]", levels[0])
    return np.array([tour_name, tour_id, prizepool, tot_players, game_mode, speed, buyin])

def parse_tour_folder(dir_name: str = "history"):
    summaries = find_tournament_summaries(dir_name=dir_name)
    columns = np.array(["name", "tournament_id", "prizepool", "nb_players", "mode", "speed", "buyin"])
    data = np.vstack([(parse_summary(file)) for file in summaries])
    df = pd.DataFrame(columns=columns, data=data)
    return df

def find_tournament_summaries(dir_name="history"):
    return [x for x in os.listdir(dir_name) if "summary" in x]

def parse_file(file_name):
    """
    Takes a file for a tournament (Winamax) and parses its hands
    :param file_name: String
    :return: WinamaxHandHistory list
    """
    # File opening
    file = open("history/%s" % file_name, "r")

    # File reading line by line until its end
    content = file.readlines()
    length = len(content)
    i = 0
    index = 0
    hands = np.array([])
    while i < length:
        # collecting different hand histories:
        # If a header pattern is found on a new line, create a new handhistory and parse header informations
        if re.match(_header_re, content[i]):

            header = re.match(_header_re, content[i])
            hh = WinamaxHandHistory()
            hh.parse_header(content[i])
            i += 1
            # find table pattern and parse its information with a new Table object with Tournaent information

            hh.parse_table(content[i])
            hh.set_table()
            table = hh.table
            preflop = table.streets[0]
            hh.set_tournament()
            i +=1
            # Step :Looking for players on seats, and adding Player objects to the table for every player found
            while re.search(_seat_re, content[i]):
                hh.parse_player(content[i])
                i += 1

            # Step : Analysing Ante and blinds
            i += 1
            street_index = 0
            # for player in hh.table.players:
            while re.search(_ante_re, content[i]):
                # print("\n", content[i])
                hh.parse_ante(content[i])
                i += 1
            # Identify sb and bb
            if re.search(_sb_re, content[i]):
                hh.parse_sb(content[i])
                i += 1
            if re.search(_bb_re, content[i]):
                hh.parse_bb(content[i])
                i += 1

            if re.search(_hero_cards_re, content[i]):
                hh.parse_hero(content[i])
                i += 1
            # Finding active players for PF (it's all of them)
            table.find_active_players(preflop)


            # PF Actions
            i += 1
            # PF Actions are parsed into PF street, and added to the table
            # While Action patterns are found

            while (re.search(_action_re, content[i])):
                #On trouve le pattern d'action et on affecte ses groupes dans un objet action, qu'on ajoute à la liste des actions. On pourra ensuite la trier.
                hh.parse_action(content[i], preflop)
                i+=1
            #print("Pot:", hh.table.pot, "Highest Bet:", hh.table.highest_bet)
            #print("\n", content[i])
            #If we have a flop pattern,  we parse its cards
            has_flop = re.search(_flop_re, content[i])
            if has_flop:
                table.make_flop()
                flop = table.streets[table.progression]
                hh.parse_flop_cards(content[i])
                i+=1
                #Next step of flop: parsing actions
                while (re.search(_action_re, content[i])):
                    hh.parse_action(content[i], flop)
                    i+=1
                #print("Pot:", hh.table.pot, "\nHighest Bet:", hh.table.highest_bet)
                #If we find a turn pattern, we parse its card
                has_turn = re.search(_turn_re, content[i])
                #print("\n",content[i])
                if has_turn:
                    table.make_turn()
                    turn = table.streets[table.progression]
                    hh.parse_turn_card(content[i])
                    i += 1
                    #Next step of turn parsing actions:
                    while (re.search(_action_re, content[i])):
                        hh.parse_action(content[i], turn)
                        i += 1
                #print("Pot:", hh.table.pot, "\nHighest Bet:", hh.table.highest_bet)
                #If we find a river pattern, we parse its card
                has_river = re.search(_river_re, content[i])
                #print("\n", content[i])
                if has_river:
                    table.make_river()
                    river = table.streets[table.progression]
                    hh.parse_river_card(content[i])
                    i += 1
                    #Next step of river is parsing actions:
                    while (re.search(_action_re, content[i])):
                        hh.parse_action(content[i], river)
                        i += 1
                    # Looking for a showdown pattern
                    has_showdown = re.search(_showdown_re, content[i])
                    if has_showdown:
                        table.make_showdown()
                        showdown=table.streets[table.progression]
                        #print("\n", content[i])
                        i += 1
                        #Parsing SD actions
                        while (re.search(_showdown_action_re, content[i])):
                            hh.parse_sd_action(content[i], showdown)
                            i += 1
            while (re.search(_winner_re, content[i])):
                hh.parse_winner(content[i])
                i+=1
            hands=np.hstack((hands,hh))
            index += 1
        i+=1
    file.close()
    return hands

def parse_directory(dir_name="history"):
    """
    Parses files of a directory into a list of hand_histories
    :param dir_name: String
    :return: WinamaxHandHistory list
    """
    timer1=Timer()
    timer1.start()
    files=[x for x in os.listdir(dir_name) if "summary" not in x]
    collection=np.array([])
    #print([collection])
    for file_name in files:
        try:
            collection=np.hstack((collection,parse_file(file_name)))
        except:
            pass
    timer1.stop()
    #print(collection.shape)
    return collection

def parse_finished_hands(dir_name="history"):
    """
    Parses files of a directory to find hands that went to ShowDown
    :param dir_name: String
    :return: WinamaxHandHistory list
    """
    timer = Timer()
    timer.start()
    finished_hands = np.array([hand for hand in parse_directory(dir_name) if hand.table.has_showdown()])
    timer.stop()
    return finished_hands

class FileReader:
    def __init__(self):
        self._split_re = re.compile(r"\*\*\*\s+\n?|\n\n+")
        self._header_re = re.compile(
            r"""
            Winamax\s+Poker\s+-\s+                                              #Winamax Poker
            (?P<poker_type>Tournament|CashGame)\s+                              #Poker Type
            \"(?P<tournament_name>.+)\"\s+                                      #Tournament Name
            buyIn\:\s+(?P<buyin>[0-9.,]+)â..\s+                                 #Buy In
            \+\s+(?P<rake>[0-9.,]+)â..\s+                                       #Rake
            level:\s+(?P<level>[\d\#]+)\s+                                      #level
            \-\s+HandId\:\s+                                                    
            \#(?P<Hand_id>[0-9-]+)\s+\-\s+                                      #Hand Id
            (?P<Variant>[A-Za-z ]+)\s+                                          #Variant
            \((?P<ante>\d+)\/                                                   #Ante
            (?P<small_blind>\d+)\/                                              #SB
            (?P<big_blind>\d+)\)\s+                                             #BB
            \-\s+(?P<date>.+)                                                   #Date
            """,
            re.VERBOSE,
        )
        self._table_re = re.compile(
            r"Table\:\s+\'(?P<tournament_name>[\w\s\']+)\((?P<tournament_id>\d+)\)\#(?P<table_id>\d+)\'\s+(?P<max_seat>\d+)\-max\s+\((?P<money_type>[a-z]+)\s+money\)\s+Seat\s+\#(?P<button>\d)\s+is\s+the\s+button")
        self._seat_re = re.compile(r"Seat\s+(?P<seat>\d+)\:\s+(?P<player_name>[\w\s\-.]{3,12})\s\((?P<stack>\d+)\)")
        self._pot_re = re.compile(r"Total\s+pot\s+(?P<total_pot>\d+)")
        self._ante_re = re.compile(r"(?P<player_name>[\w\s\-.]{3,12})\s+posts\sante\s+(?P<amount>\d+)")
        self._board_re = re.compile(r"Board\:\s+\[(?P<board>[0-9AJKQshdc ]+)\]")
        self._action_re = re.compile(
            r"(?P<player_name>[\w\s\-.]{6,12})\s+(?P<move>shows|checks|calls|folds|bets|raises)\s+(?P<value>\d+||\s+)")
        self._showdown_action_re = re.compile(
            r"(?P<player_name>[\w\s\-.]{6,12})\s+(?P<move>shows|mucks)\s+\[(?P<card1>[AJKQ2-9shdc]{2})\s+(?P<card2>[AJKQ2-9shdc]{2})\]")
        self._flop_re = re.compile(
            r"\*\*\*\s+FLOP\s+\*\*\*\s+\[(?P<flop_card_1>[AJKQT2-9hscd]{2})\s+(?P<flop_card_2>[AJKQT2-9hscd]{2})\s+(?P<flop_card_3>[AJKQT2-9hscd]{2})\]")
        self._hero_cards_re = re.compile(
            r"Dealt\s+to\s+(?P<hero_name>[\w\s\-.]+)\s+\[(?P<card1>[AJKQT2-9hscd]{2})\s+(?P<card2>[AJKQT2-9hscd]{2})\]")
        self._turn_re = re.compile(r"\*\*\*\s+TURN\s+\*\*\*\s+\[.+\]\[(?P<turn_card>[AJKQT2-9hscd]{2})\]")
        self._river_re = re.compile(r"\*\*\*\s+RIVER\s+\*\*\*\s+\[.+\]\[(?P<river_card>[AJKQT2-9hscd]{2})\]")
        self._showdown_re = re.compile(r"\*\*\*\s+SHOW\s+DOWN\s+\*\*\*")
        self._summary_re = re.compile(r"\*\*\*\s+SUMMARY\s+\*\*\*")
        self._winner_re = re.compile(r"(?P<player_name>[\w\s\-.]{6,12})\s+collected\s+(?P<amount>\d+)\s+")
        self._sb_re = re.compile(r"(?P<player_name>[\w\s\-.]{3,12})\s+posts\s+small\s+blind\s+(?P<sb>\d+)")
        self._bb_re = re.compile(r"(?P<player_name>[\w\s\-.]{3,12})\s+posts\s+big\s+blind\s+(?P<bb>\d+)")
        self._tour_name_re = re.compile(r"Winamax\s+Poker\s+-\s+Tournament\s+summary\s+\:\s+"
                                   r"(?P<tournament_name>.+)\((?P<tournament_id>\d+)\)")
        self._total_players_re = re.compile(r"Registered\s+players\s+\:\s+(?P<total_players>\d+)")
        self._prizepool_re = re.compile(r"Prizepool\s+\:\s+(?P<prizepool>[\d.]+)")
        self._game_mode_re = re.compile(r"Mode\s+.+\s+\:\s+(?P<game_mode>.+)")
        self._ttype_re = re.compile(r"Type\s+\:\s+(?P<game_mode>.+)")
        self._speed_re = re.compile(r"Speed\s+\:\s+(?P<speed>.+)")
        self._buyin_re = re.compile(r"Buy-In\s+\:\s+(?P<buyin>[\d.]+)")
        self._levels_re = re.compile(r"Levels\s+\:\s+\[(?P<levels>.+)\]")
