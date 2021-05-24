import os
import re
import io
import itertools
from datetime import datetime
import attr
import pytz
from zope.interface import Interface, Attribute
from cached_property import cached_property
from API.card import Rank
from API import handhistory as hh
from zope.interface import implementer



_split_re = re.compile(r"\*\*\*\s+\n?|\n\n+")
_header_re = re.compile(
    r"""
    Winamax\s+Poker\s+\-\s+                                             #Winamax Poker
    (?P<poker_type>Tournament)\s+                                       #Poker Type
    \"(?P<tournament_name>.+)\"\s+                                      #Tournament Name
    buyIn\:\s+(?P<buyin>[0-9.,]+)â..\s+                                  #Buy In
    \+\s+(?P<rake>[0-9.,]+)â..\s+                                        #Rake
    level:\s+(?P<level>\d+)\s+                                          #level
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
    """
    Table:\s+\'(?P<tournament_name>[a-zA-Z0-9]+)\(                      #Tournament Name
    (?P<tournament_id>\d+)\)                                            #Tournament Id
    \#(?P<table_id>\d+)\'\s+                                            #Table Id
    (?P<max_seat>\d+)\-max\s+                                           #Max Seats
    \((?P<money_type>[a-z]+)\s+money\)\s+                               #Money Type
    Seat\s+\#(?P<button>\d)\s+is\s+the\s+button                         #Button
    """,
    re.VERBOSE
)
_seat_re = re.compile(
    """Seat\s+(?P<seat>\d+)\:\s+                                        #Seat
    (?P<player_name>[\w\s-]+)\s+                                              #Player_name
    \((?P<stack>\d+)\)                                                  #Stack
    """,
    re.VERBOSE
)
_pot_re = re.compile(r"Total\s+pot\s+(?P<total_pot>\d+)")
_winner_re = re.compile(r"(?P<player_name>.+)\s+collected\s+(?P<amount>\d+)\s+from\s+(?P<pot_type>.+)")
_showdown_re = re.compile(r"(?P<player_name>.+)\s+shows\s+\[(..) (..)\]\s+")
_ante_re = re.compile(r"(?P<player_name>.+)posts ante (\d+(?:\.\d+)?)")
_board_re=re.compile(r"Board\:\s+\[(?P<board>[0-9AJKQshdc ]+)\]")
_action_re=re.compile(r"(?P<player_name>[\w\s-]+)\s+(?P<move>folds|checks|calls|bets|raises)\s+(?P<value>[0-9]+||[s+])")
_showdown_action_re=re.compile(r"(?P<player_name>[\w\s-]+)\s+(?P<move>shows|mucks)\s+\[(?P<card1>[AJKQT2-9hscd]{2})\s+(?P<card2>[AJKQT2-9hscd]{2})\]")
_flop_re=re.compile(r"\*\*\*\s+FLOP\s+\*\*\*\s+\[(?P<flop_card_1>[AJKQT2-9hscd]{2})\s+(?P<flop_card_2>[AJKQT2-9hscd]{2})\s+(?P<flop_card_3>[AJKQT2-9hscd]{2})\]")
_hero_cards_re=re.compile(r"Dealt\s+to\s+(?P<hero_name>[\w\s-]+)\s+\[(?P<card1>[AJKQT2-9hscd]{2})\s+(?P<card2>[AJKQT2-9hscd]{2})\]")
_turn_re=re.compile(r"\*\*\*\s+TURN\s+\*\*\*\s+\[.+\]\[(?P<turn_card>[AJKQT2-9hscd]{2})\]")
_river_re=re.compile(r"\*\*\*\s+RIVER\s+\*\*\*\s+\[.+\]\[(?P<river_card>[AJKQT2-9hscd]{2})\]")
_showdown_re=re.compile(r"\*\*\*\s+SHOW\s+DOWN\s+\*\*\*")



class WinamaxHandHistory(hh._BaseHandHistory, hh.IHandHistory):
    """Parses Winamax Tournament hands."""

    table_parsed = Attribute("Shows wheter table is parsed already or not.")


    @classmethod
    def lines_from_file(cls, filename):
        with io.open(filename, "rt", encoding="utf-8-sig") as file:
            return cls(file.readLines())


    def parse_file(self):

        i = 0
        # Tant qu'on est pas arrivé au bout du document
        while i < self.lines:

            # Si on trouve le pattern d'une nouvelle main:
            if re.match(_header_re, self[i]):
                # On génère une nouvelle Game

                # On récupère les infos de la nouvelle main dans des variables
                # Il s'agira ensuite de rentrer ces variables dans un objet Game qui représente la main.
                self.header_re = re.match(_header_re, self[i])
                self.parse_header()
                # On passe à la ligne suivante pour l'analyse de la table
                i += 1
                # On lit le pattern de la table pour y trouver les infos complémentaires.
                # print ("Analyse de la table ligne %s :" %(i))
                self.table_re = re.search(_table_re, content[i])
                table=self.table_re
                self.tournament_ident = table.group("tournament_id")
                self.table_id = table.group("table_id")
                self.max_players = table.group("max_seat")
                self.money_type = table.group("money_type")
                button_seat = table.group("button")
                print("\nTournament ID: %s, Table ID: %s. On joue en %s-max en %s money. Le siège n° %s est Btn" % (
                tournament_id, table_id, max_seat, money_type, button_seat))
                # print(table.groups())
                # On passe à la ligne suivante.
                i += 1
                # print("Recherche des sièges occupés à partir de la ligne %s" %(i))
                # On analyse les sièges à la table.
                # On crée une liste des sièges
                seats = []
                # Tant qu'on a des patterns de sièges:
                while (re.search(_seat_re, content[i])):
                    # On récupère les infos des sièges et on les insère dans un objet du type Seat, puis onn ajoute l'objet à la liste.
                    seat = re.search(_seat_re, content[i])
                    number = seat.group("seat")
                    player = seat.group("player_name")
                    stack = seat.group("stack")
                    seat = Seat(number, player, stack)
                    print("\n%s Occupe le siège n°%s avec un stack de %s" % (seat.player, seat.number, seat.stack))
                    seats.append(seat)
                    # print (seats)
                    i += 1
                # On passe aux Ante/Blindes

                # Il faudrait ici avoir une fonction de classe Game qui permet d'attribuer les positions en fonction des sièges
                print("\n", content[i])
                print("On peut choisir ou non d'afficher les Ante et blindes, mais ici, on ne le fait pas.")
                i += 1
                # print( re.search(_split_re, content[i]))

                # On recherche la 1ère séparation, correspondant aux actions pré-flop
                while not (re.search(_split_re, content[i])):
                    i += 1
                # On passe aux actions pré-flop
                print("\n", content[i])
                i += 1
                # On définit un tableau de l'ensemble des actions (à l'avenir, on affectera ça à la main
                actions_PF = []
                # Tant qu'on a des patterns d'actions:
                while (re.search(_action_re, content[i])):
                    # On trouve le pattern d'action et on affecte ses groupes dans un objet action, qu'on ajoute à la liste des actions. On pourra ensuite la trier.
                    action = re.search(_action_re, content[i])
                    player = action.group("player_name")
                    move = action.group("move")
                    value = action.group("value")
                    action = Action(player, move, value)
                    print(action.player, action.move, action.value)
                    actions_PF.append(action)
                    i += 1
                # On recherche un pattern de flop
                flop = re.search(_flop_re, content[i])
                # Si il y a un flop, on passe au flop
                if flop:
                    print("\n", content[i])
                    flop_card_1 = flop.group("flop_card_1")
                    flop_card_2 = flop.group("flop_card_2")
                    flop_card_3 = flop.group("flop_card_3")
                    # On passe à la suite du flop
                    i += 1
                    # print(flop.groups())
                    # Si on a des patterns d'actions:
                    actions_F = []
                    while (re.search(_action_re, content[i])):
                        action = re.search(_action_re, content[i])
                        player = action.group("player_name")
                        move = action.group("move")
                        value = action.group("value")
                        action = Action(player, move, value)
                        print(action.player, action.move, action.value)
                        actions_F.append(action)
                        i += 1
                    # On recherche un pattern de turn
                    turn = re.search(_turn_re, content[i])
                    if turn:
                        print("\n", content[i])
                        turn_card = turn.group("turn_card")
                        # On passe à la suite du turn
                        i += 1
                        # Si on a des patterns d'actions:
                        actions_T = []
                        while (re.search(_action_re, content[i])):
                            action = re.search(_action_re, content[i])
                            player = action.group("player_name")
                            move = action.group("move")
                            value = action.group("value")
                            action = Action(player, move, value)
                            print(action.player, action.move, action.value)
                            actions_T.append(action)
                            i += 1
                    # On recherche un pattern de river
                    river = re.search(_river_re, content[i])
                    if river:
                        print("\n", content[i])
                        river_card = river.group("river_card")
                        # On passe à la suite du river
                        i += 1
                        # Si on a des patterns d'actions:
                        actions_R = []
                        while (re.search(_action_re, content[i])):
                            action = re.search(_action_re, content[i])
                            player = action.group("player_name")
                            move = action.group("move")
                            value = action.group("value")
                            action = Action(player, move, value)
                            print(action.player, action.move, action.value)
                            actions_R.append(action)
                            i += 1
                    # On recherche un pattern de showdown
                    showdown = re.search(_showdown_re, content[i])
                    # En cas de Showdown
                    if showdown:
                        print("\n", content[i])
                        # On observe les actions du showdown
                        i += 1
                        # Si on a des patterns d'actions:
                        actions_SD = []
                        while (re.search(_showdown_action_re, content[i])):
                            action = re.search(_showdown_action_re, content[i])
                            player = action.group("player_name")
                            move = action.group("move")
                            SD_card_1 = action.group("card1")
                            SD_card_2 = action.group("card2")
                            action = SDAction(player, move, SD_card_1, SD_card_2)

                            print("\n", action.player, action.move, action.card1, " and ", action.card2)
                            actions_SD.append(action)
                            i += 1
                        winners = []
                        while (re.search(_winner_re, content[i])):
                            winner = re.search(_winner_re, content[i])
                            player = winner.group("player_name")
                            amount = winner.group("amount")
                            pot_type = winner.group("pot_type")
                            print("\n %s wins %s from %s" % (player, amount, pot_type))
                            i += 1

                # print("Ligne %s: %s" % (i, content[i]))

            i += 1

    def parse_header(self):
        header = self.header_re
        self.game_type = header.group("poker_type")
        self.tournament_name = header.group("tournament_name")
        self.buyin = header.group("buyin")
        self.rake = header.group("rake")
        self.tournament_level = header.group("level")
        self.ident = header.group("Hand_id")
        self.game = header.group("Variant")
        self.ante = header.group("ante")
        self.sb = header.group("small_blind")
        self.bb = header.group("big_blind")
        self.date = header.group("date")
        self.currency = "EUR"
        #self.limit = header.group("limit")
        self.header_parsed = True