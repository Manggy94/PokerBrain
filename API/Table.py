import API.hand
from API.constants import *
from API.hand import *
from API.card import *
import random
import numpy as np


class Street:
    """Class initiating a Street with its players and actions ses joueurs et les actions"""

    def __init__(self, name):
        self.name = name
        self.cards=[]
        self.active_players = []
        self.actions = []
        self.street_pot = 0
        self.highest_bet = 0
        self.index=0

    def add_action(self, action):
        self.actions.append(action)
        player=action.player
        player.set_to_call(self)
        player.set_pot_odds(self)
        #print("%s doit miser %s pour suivre. \nOdds= %s : 1\nReq.Equity= %s%%" %(player.name, player.to_call, round(player.pot_odds, 1),round(player.req_equity*100)))
        if action.move in ("fold", "folds"):
            player.fold()
        elif action.move in ("call", "calls", "checks", "check"):
            self.call(player)
        elif action.move in ("bet", "bets"):
            self.bet(player, action.value)
        elif action.move in ("raise", "raises"):
            self.bet(player, player.to_call+action.value)
        #print("Décision: %s %s %s" % (player.name, action.move, action.value))

    def bet(self, player, amount):
        self.street_pot += amount
        player.stack -= amount
        player.current_bet += amount
        if player.current_bet > self.highest_bet:
            self.highest_bet = player.current_bet

    def call(self, player):
        if player.stack < player.get_to_call():
            self.bet(player, player.stack)
        else:
            self.bet(player, player.get_to_call())

    def reset_bets(self):
        self.highest_bet = 0
        for player in self.active_players:
            player.current_bet = 0



class Action:
    """Classe qui définit les différentes actions possibles d'un joueur pendant une main"""
    def __init__(self, player, move, value):
        self.player = player
        self.move = move
        if value:
            self.value = value
        else:
            self.value = 0


class SDAction:
    """Classe qui définit les différentes actions possibles d'un joueur pendant une main"""
    def __init__(self, player, move, card1, card2):
        self.player = player
        self.move = move
        if card1:
            self.card1 = card1
            if card2:
                self.card2 = card2


class Tournament:
    """Class for played tournaments"""
    def __init__(self, ident, platform, name, buyin, rake, money_type):
        self.id = ident
        self.platform = platform
        self.name = name
        self.buyin = buyin
        self.rake = rake
        self.money_type = money_type


class Level:
    """Level of the tournament"""
    def __init__(self, number, sb, bb, ante):
        self.nb = number
        self.sb = sb
        self.bb = bb
        self.ante = ante


class Player:

    # position = None

    def __init__(self, name, seat, stack):
        self.name = name
        self.seat = seat
        self.stack = stack
        self.ingame = True
        self.combo = None
        self.folded = False
        self.hero = False
        self.current_bet = 0
        self.to_call = 0

    def is_hero(self, combo: API.hand.Combo):
        self.hero = True
        self.combo = combo

    def has_combo(self):
        return self.combo !=None

    def shows(self, combo):
        self.combo = combo

    def set_position(self, position):
        self.position = position


    def fold(self):
        self.folded = True

    def reset(self):
        self.folded = False

    def set_to_call(self, table):
        self.to_call = table.highest_bet-self.current_bet

    def get_to_call(self):
        return self.to_call

    def set_pot_odds(self, table):
        if self.to_call!=0:
            self.pot_odds=table.pot/self.to_call
        else:
            self.pot_odds=float("inf")

        self.req_equity=1/(1+self.pot_odds)

    def get_pot_odds(self):
        return(self.pot_odds)


class Table:
    pot = 0
    progression = 0

    def __init__(self, ident=None, max_players: int=6):
        self.ident = ident
        self.max_players = max_players
        self.board = []
        self.players = []
        self.highest_bet = 0
        self.streets = [Street('PF')]
        self.hero = None
        self.PF = Street('PF')

    def add_action(self, street, action):
        street.actions.append(action)
        player=action.player
        player.set_to_call(self)
        player.set_pot_odds(self)
        #print("%s doit miser %s pour suivre. \nOdds= %s : 1\nReq.Equity= %s%%" %(player.name, player.to_call, round(player.pot_odds, 1),round(player.req_equity*100)))
        if action.move in ("fold", "folds"):
            player.fold()
        elif action.move in ("call", "calls", "checks", "check"):
            self.call(player)
        elif action.move in ("bet", "bets"):
            self.bet(player, action.value)
        elif action.move in ("raise", "raises"):
            self.bet(player, player.to_call+action.value)
        #print("Décision: %s %s %s" % (player.name, action.move, action.value))

    def add_player(self, player):
        self.players.append(player)
        player.init_stack=player.stack

    def bet(self, player, amount):
        self.pot += amount
        player.stack -= amount
        player.current_bet += amount
        if player.current_bet > self.highest_bet:
            self.highest_bet = player.current_bet

    def call(self, player):
        if player.stack < player.get_to_call():
            self.bet(player, player.stack)
        else:
            self.bet(player, player.get_to_call())

    def distribute_cards(self, player):
        player.combo = Combo().from_cards(self.draw_card(), self.draw_card())


    def distribute_positions(self):
        a = len(self.players)
        b = len(list(Position))
        pl_table = []
        #print("Nombre de joueurs:%s" % (a))
        if a<6:
            positions = list(Position)[b-a:]
        else:
            positions = list(Position)[0:a-5]
            positions.extend(list(Position)[b-a+1:])
        for player in self.players:
            try:
                player.position == Position("BB")
                cut = self.players.index(player)
                #print("Le joueur n° %s a la BB et on coupe le tableau des joueurs à l'index %s" % (player.seat, cut))
                #print(cut)
                end = self.players[:cut]
                start = self.players[cut+1:]
                bb = self.players[cut]
                pl_table.extend(start)
                pl_table.extend(end)
                pl_table.append(bb)
            except:
                pass
        for i in range(0,len(pl_table)):
            pl_table[i].set_position(positions[i])

    def draw_card(self):
        self.deck.pop()

    def find_active_players(self, street):
        i=street.index
        if i == 0:
            self.streets[i].active_players = self.players
        else:
            for player in self.streets[i-1].active_players:
                if player.ingame and not player.folded:
                    self.streets[i].active_players.append(player)


    def has_flop(self):
        return len(self.streets) >=2


    def has_river(self):
        return len(self.streets) >= 4

    def has_showdown(self):
        return len(self.streets) >= 5

    def has_turn(self):
        return len(self.streets) >= 3

    def make_deck(self):
        self.deck = list(Card)
        random.shuffle(self.deck)

    def make_flop(self):
        flop=Street('F')
        self.streets.append(flop)
        flop.index = 1
        self.find_active_players(flop)
        self.reset_bets()
        self.progression += 1


    def make_river(self):
        river = Street('R')
        self.streets.append(river)
        river.index = 3
        self.find_active_players(river)
        self.reset_bets()
        self.progression += 1

    def make_showdown(self):
        SD = Street('SD')
        self.streets.append(SD)
        SD.index = 4
        self.find_active_players(SD)
        self.reset_bets()
        self.progression += 1

    def make_turn(self):
        turn = Street('T')
        self.streets.append(turn)
        turn.index = 2
        self.find_active_players(turn)
        self.reset_bets()
        self.progression += 1

    def post_ante(self, player, amount):
        self.pot += amount
        player.stack -= amount

    def reset_bets(self):
        self.highest_bet = 0
        for player in self.players:
            player.current_bet = 0

    def set_tournament(self, tournament):
        self.tournament=tournament

    def set_level(self, level):
        self.level = level
        self.sb = level.sb
        self.bb = level.bb
        self.ante = level.ante

    def win(self, player, amount):
        self.pot -= amount
        player.stack += amount
