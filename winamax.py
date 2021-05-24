import re
from API.Table import *
from API.hand import *
from API.card import *

_split_re = re.compile(r"\*\*\*\s+\n?|\n\n+")
_header_re = re.compile(
    r"""
    Winamax\s+Poker\s+\-\s+                                             #Winamax Poker
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
_seat_re = re.compile(
    """Seat\s+(?P<seat>\d+)\:\s+                                        #Seat
    (?P<player_name>[\w\s-]{6,12})\s+                                              #Player_name
    \((?P<stack>\d+)\)                                                  #Stack
    """,
    re.VERBOSE
)
_pot_re = re.compile(r"Total\s+pot\s+(?P<total_pot>\d+)")
_ante_re = re.compile(r"(?P<player_name>[\w\s\-]{3,12})\s+posts\sante\s+(?P<amount>\d+)")
_board_re = re.compile(r"Board\:\s+\[(?P<board>[0-9AJKQshdc ]+)\]")
_action_re = re.compile(
    r"(?P<player_name>[\w\s\-]{6,12})\s+(?P<move>shows|checks|calls|folds|bets|raises)\s+(?P<value>\d+||\s+)")
_showdown_action_re = re.compile(
    r"(?P<player_name>[\w\s\-]{6,12})\s+(?P<move>shows|mucks)\s+\[(?P<card1>[AJKQ2-9shdc]{2})\s+(?P<card2>[AJKQ2-9shdc]{2})\]")
_flop_re = re.compile(
    r"\*\*\*\s+FLOP\s+\*\*\*\s+\[(?P<flop_card_1>[AJKQT2-9hscd]{2})\s+(?P<flop_card_2>[AJKQT2-9hscd]{2})\s+(?P<flop_card_3>[AJKQT2-9hscd]{2})\]")
_hero_cards_re = re.compile(
    r"Dealt\s+to\s+(?P<hero_name>[\w\s-]+)\s+\[(?P<card1>[AJKQT2-9hscd]{2})\s+(?P<card2>[AJKQT2-9hscd]{2})\]")
_turn_re = re.compile(r"\*\*\*\s+TURN\s+\*\*\*\s+\[.+\]\[(?P<turn_card>[AJKQT2-9hscd]{2})\]")
_river_re = re.compile(r"\*\*\*\s+RIVER\s+\*\*\*\s+\[.+\]\[(?P<river_card>[AJKQT2-9hscd]{2})\]")
_showdown_re = re.compile(r"\*\*\*\s+SHOW\s+DOWN\s+\*\*\*")
_summary_re = re.compile(r"\*\*\*\s+SUMMARY\s+\*\*\*")
_winner_re = re.compile(r"(?P<player_name>[\w\s\-]{6,12})\s+collected\s+(?P<amount>\d+)\s+")
_sb_re = re.compile(r"(?P<player_name>[\w\s\_]{3,12})\s+posts\s+small\s+blind\s+(?P<sb>\d+)")
_bb_re = re.compile(r"(?P<player_name>[\w\s\_]{3,12})\s+posts\s+big\s+blind\s+(?P<bb>\d+)")

class WinamaxHandHistory:
    """Winamax specific parsing."""

    def __init__(self, header_txt):
        header = re.match(_header_re, header_txt)
        self.poker_type = header.group("poker_type")
        self.tournament_name = header.group("tournament_name")
        self.buyIn = header.group("buyin")
        self.rake = header.group("rake")
        level_nb = header.group("level")
        self.ident = header.group("Hand_id")
        self.variant = header.group("Variant")
        ante = header.group("ante")
        SB = header.group("small_blind")
        BB = header.group("big_blind")
        self.date = header.group("date")
        self.header_parsed=True
        self.level=Level(int(level_nb), float(SB), float(BB), float(ante))

    def set_table(self, table):
        self.table=table

    def parse_table(self, table_txt):
        match = re.search(_table_re, table_txt)
        self.tournament_id = match.group("tournament_id")
        self.table_id = match.group("table_id")
        self.max_seat = match.group("max_seat")
        self.money_type = match.group("money_type")
        self.button_seat = match.group("button")

    def parse_player(self, player_txt):
        match = re.search(_seat_re, player_txt)
        seat = match.group("seat")
        player_name = match.group("player_name")
        stack = match.group("stack")
        player = Player(player_name, int(seat), float(stack))
        self.table.add_player(player)


    def set_tournament(self):
        self.table.tournament = Tournament(self.tournament_id, "Winamax", self.tournament_name, self.buyIn, self.rake, self.money_type)

    def set_table(self):
        self.table = Table(self.table_id, self.max_seat)

    def parse_ante(self, ante_txt):
        match = re.search(_ante_re, ante_txt)
        player_name=match.group("player_name")
        amount=float(match.group("amount"))
        for player in self.table.players:
            if player_name==player.name:
                self.table.post_ante(player, amount)
                print("%s pose %s pour ante" %(player.name, amount))

    def parse_sb(self, sb_text):
        match = re.search(_sb_re, sb_text)
        player_name=match.group("player_name")
        sb=float(match.group("sb"))
        for player in self.table.players:
            if player_name==player.name:
                self.table.bet(player, sb)
                print("%s pose  %s en tant que SB" %(player.name, sb))

    def parse_bb(self, bb_text):
        match = re.search(_bb_re, bb_text)
        player_name=match.group("player_name")
        bb=float(match.group("bb"))
        for player in self.table.players:
            if player_name==player.name:
                self.table.bet(player, bb)
                print("%s pose  %s en tant que BB" %(player.name, bb))

    def parse_hero(self, hero_txt):
        match = re.search(_hero_cards_re, hero_txt)
        hero_name = match.group("hero_name")
        c1 = match.group("card1")
        c2 = match.group("card2")
        combo=Combo(c1+c2)
        for player in self.table.players:
            if hero_name==player.name:
                player.is_hero(combo)
                print("Le héros est %s, avec en main %s et %s." % (hero_name, combo.first, combo.second))

    def parse_action(self, action_txt, street):
        match = re.search(_action_re, action_txt)
        player_name = match.group("player_name")
        move = match.group("move")
        value = float("0"+match.group("value"))
        for player in self.table.players:
            if player.name == player_name:
                action_player = player
                action = Action(action_player, move, value)
                self.table.add_action(street, action)

    def parse_flop_cards(self, flop_txt):
        match = re.search(_flop_re, flop_txt)
        fc1 = Card(match.group("flop_card_1"))
        fc2 = Card(match.group("flop_card_2"))
        fc3 = Card(match.group("flop_card_3"))
        cards=self.table.F.cards
        cards.append(fc1)
        cards.append(fc2)
        cards.append(fc3)
        print(cards)



