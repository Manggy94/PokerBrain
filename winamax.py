import re

import numpy as np

from API.Table import *
from API.hand import *
from API.card import *

_split_re = re.compile(r"\*\*\*\s+\n?|\n\n+")
_header_re = re.compile(
    r"""
    Winamax\s+Poker\s+-\s+                                             #Winamax Poker
    (?P<poker_type>Tournament)\s+                                       #Poker Type
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


def floatify(txt: str):
    return float(txt.replace(",", "."))


class WinamaxHandHistory:
    """Winamax specific parsing."""

    def __init__(self):
        self.header_parsed = False
        self.tournament_id = None
        self.table_id = None
        self.money_type = None
        self.button_seat = None
        self.max_seat = None
        self.table = None

    def parse_header(self, header_txt):
        header = re.match(_header_re, header_txt)
        self.poker_type = header.group("poker_type")
        self.tournament_name = header.group("tournament_name")
        self.buyIn = floatify(header.group("buyin"))
        self.rake = floatify(header.group("rake"))
        level_nb = int(header.group("level"))
        self.ident = header.group("Hand_id")
        self.variant = header.group("Variant")
        ante = floatify(header.group("ante"))
        SB = floatify(header.group("small_blind"))
        BB = floatify(header.group("big_blind"))
        self.date = header.group("date")
        self.header_parsed = True
        self.level = Level(int(level_nb), float(SB), float(BB), float(ante))

    def parse_table(self, table_txt):
        match = re.search(_table_re, table_txt)
        self.tournament_id = int(match.group("tournament_id"))
        self.table_id = int(match.group("table_id"))
        self.max_seat = int(match.group("max_seat"))
        self.money_type = match.group("money_type")
        self.button_seat = int(match.group("button"))

    def parse_player(self, player_txt):
        match = re.search(_seat_re, player_txt)
        seat = int(match.group("seat"))
        player_name = match.group("player_name")
        stack = floatify(match.group("stack"))
        player = Player(player_name, seat, stack)
        self.table.add_player(player)

    def set_tournament(self):
        self.table.tournament = Tournament(self.tournament_id, "Winamax", self.tournament_name, self.buyIn, self.rake,
                                           self.money_type)

    def set_table(self):
        self.table = Table(self.table_id, self.max_seat)

    def parse_ante(self, ante_txt):
        match = re.search(_ante_re, ante_txt)
        player_name = match.group("player_name")
        amount = floatify(match.group("amount"))
        for player in self.table.players:
            if player_name == player.name:
                self.table.post_ante(player, amount)
                # print("%s pose %s pour ante" %(player.name, amount))

    def parse_sb(self, sb_text):
        match = re.search(_sb_re, sb_text)
        player_name = match.group("player_name")
        sb = floatify(match.group("sb"))
        for player in self.table.players:
            if player_name == player.name:
                self.table.bet(player, sb)
                break
                # print("%s pose  %s en tant que SB" %(player.name, sb))

    def parse_bb(self, bb_text):
        match = re.search(_bb_re, bb_text)
        player_name = match.group("player_name")
        bb = floatify(match.group("bb"))
        for player in self.table.players:
            if player_name == player.name:
                self.table.bet(player, bb)
                player.position = Position('BB')
                break
        self.table.distribute_positions()
        # print("%s pose  %s en tant que BB" %(player.name, bb))

    def parse_hero(self, hero_txt):
        match = re.search(_hero_cards_re, hero_txt)
        hero_name = match.group("hero_name")
        c1 = match.group("card1")
        c2 = match.group("card2")
        combo = Combo(c1+c2)
        for player in self.table.players:
            if hero_name == player.name:
                player.is_hero(combo)
                self.table.hero = player
                break

    def parse_action(self, action_txt, street):
        match = re.search(_action_re, action_txt)
        player_name = match.group("player_name")
        move = match.group("move")
        value = floatify("0"+match.group("value"))
        for player in self.table.players:
            if player.name == player_name:
                action_player = player
                action = Action(action_player, move, value)
                self.table.add_action(street, action)
                break

    def parse_sd_action(self, sd_txt, street):
        match = re.search(_showdown_action_re, sd_txt)
        player_name = match.group("player_name")
        move = match.group("move")
        SDC1 = match.group("card1")
        SDC2 = match.group("card2")
        for player in self.table.players:
            if player.name == player_name:
                action_player = player
                action = SDAction(action_player, move, SDC1, SDC2)
                street.actions.append(action)
                player.shows(Combo(SDC1+SDC2))
                break
                # print(player.name, player.combo)

    def parse_flop_cards(self, flop_txt):
        flop = self.table.streets[1]
        match = re.search(_flop_re, flop_txt)
        fc1 = Card(match.group("flop_card_1"))
        fc2 = Card(match.group("flop_card_2"))
        fc3 = Card(match.group("flop_card_3"))
        cards = flop.cards
        cards.append(fc1)
        cards.append(fc2)
        cards.append(fc3)
        self.table.board.extend(cards)
        # print("Board",self.table.board)

    def parse_turn_card(self, turn_txt):
        turn = self.table.streets[2]
        match = re.search(_turn_re, turn_txt)
        tc = Card(match.group("turn_card"))
        cards = turn.cards
        cards.append(tc)
        self.table.board.extend(cards)
        # print("Board",self.table.board)

    def parse_river_card(self, river_txt):
        river = self.table.streets[3]
        match = re.search(_river_re, river_txt)
        rc = Card(match.group("river_card"))
        cards = river.cards
        cards.append(rc)
        self.table.board.extend(cards)
        # print("Board",self.table.board)

    def parse_winner(self, winner_txt):
        match = re.search(_winner_re, winner_txt)
        player_name = match.group("player_name")
        amount = floatify(match.group("amount"))
        for player in self.table.players:
            if player.name == player_name:
                self.table.win(player, amount)
                break
                # print(player.name,"gagne", amount, " et a maintenant un stack de ", player.stack)

    def get_hand_info(self):
        return self.tournament_id, self.table_id, self.level.nb, self.level.bb, self.level.ante, \
               self.table.max_players, self.button_seat, self.buyIn

    def get_board_card(self, i):
        return self.table.get_board_card(i)

    def get_total_board(self):
        return self.table.get_total_board()

    def get_partial_board(self, progress: int):
        return self.table.get_partial_board(progress)

    def get_player(self, i: int):
        return self.table.get_player(i)

    def get_player_infos(self, i: int):
        return self.table.get_player_infos(i)

    def get_all_players_info(self):
        return self.table.get_all_players_info()

    def get_street(self, i):
        return self.table.get_street(i)

    def get_table_action_info(self,n: int = 24):
        return self.table.get_table_action_info(n)

    def get_consecutive_actions(self):
        k = 0
        actions = self.get_table_action_info()
        all_actions = self.get_table_action_info().reshape(1, 288)
        prog = 3
        progress = [prog]
        all_boards = self.get_partial_board(prog)
        info = np.array(self.get_hand_info())
        pl_info = self.get_all_players_info()
        while k < 96:
            i = 287-3*k
            prog = i // 72
            # print(actions[i],actions[:i+1].shape, actions[i+1:].shape, 287-i)
            if actions[i]:
                progress.append(prog)
                part_actions = np.hstack((actions[:i+1], [None]*(287-i)))
                all_actions = np.vstack((all_actions, part_actions))
                all_boards = np.vstack((all_boards, self.get_partial_board(prog)))
                info = np.vstack((info, self.get_hand_info()))
                pl_info = np.vstack((pl_info, self.get_all_players_info()))
            k += 1
        n = all_actions.shape[0]
        idents = [self.ident]*n
        return all_actions, np.array(progress), all_boards, idents, info, pl_info
