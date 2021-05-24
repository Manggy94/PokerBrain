from API.constants import  *
from API.hand import *
from API.card import *
import random

class Street:
    """Class initiating a Street with its players and actions ses joueurs et les actions"""
    def __init__(self, name):
        self.name=name
        self.active_players=[]
        self.actions=[]
        self.cards=[]

class Action:
    """Classe qui définit les différentes actions possibles d'un joueur pendant une main"""
    def __init__(self, player, move, value):
        self.player = player
        self.move = move
        if value:
            self.value = value
        else:
            self.value=0

class SDAction:
    """Classe qui définit les différentes actions possibles d'un joueur pendant une main"""
    def __init__(self, player, move, card1, card2 ):
        self.player = player
        self.move = move
        if card1:
            self.card1 = card1
            if card2:
                self.card2 = card2


class Tournament:
    """Class for played tournaments"""
    def __init__(self, id, platform, name, buyin, rake, money_type  ):
        self.id = id
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

    def __init__(self,name, seat, stack):
        self.name = name
        self.seat = seat
        self.stack = stack
        self.folded = False
        self.ingame = True
        self.hero = False
        self.current_bet = 0

    def is_hero(self, combo):
        self.hero=True
        self.combo=combo

    def set_position(self, position):
        self.position = position


    def fold(self):
        self.folded=True

    def reset(self):
        self.folded=False


    def set_to_call(self, table):
        self.to_call=table.highest_bet-self.current_bet

    def get_to_call(self):
        return(self.to_call)

    def set_pot_odds(self, table):
        if self.to_call!=0:
            self.pot_odds=table.pot/self.to_call
        else:
            self.pot_odds=float("inf")

        self.req_equity=1/(1+self.pot_odds)

    def get_pot_odds(self):
        return(self.pot_odds)


class Table:

    def __init__(self, id, max_players):
        self.id = id
        self.max_players = max_players
        self.board = []
        self.players = []
        self.pot = 0
        self.highest_bet=0
        self.PF=Street('PF')


    def find_active_players(self, street):
        if street.name=='PF':
            street.active_players=self.players
        elif street.name=='F':
            for player in self.PF.active_players:
                if player.ingame and not player.folded:
                    street.active_players.append(player)
        elif street.name=='T':
            for player in self.F.active_players:
                if player.ingame and not player.folded:
                    street.active_players.append(player)
        elif street.name=='R':
            for player in self.T.active_players:
                if player.ingame and not player.folded:
                    street.active_players.append(player)



    def set_level(self, level):
        self.level = level
        self.sb=level.sb
        self.bb=level.bb
        self.ante=level.ante


    def make_deck(self):
        self.deck=list(Card)
        random.shuffle(deck)

    def draw_card(self):
        deck.pop()

    def distribute_cards(self, player):
        player.combo=Combo().from_cards(self.draw_card(), self.draw_card())


    def add_player(self, player):
        self.players.append(player)


    def win(self, player, amount):
        self.pot-=amount
        player.stack+=amount

    def post_ante(self,player,amount):
        self.pot+=amount
        player.stack-=amount


    def bet(self,player,amount):
        self.pot+=amount
        player.stack-=amount
        player.current_bet+=amount
        if player.current_bet>self.highest_bet:
            self.highest_bet=player.current_bet

    def call(self, player):
        if player.stack<player.get_to_call():
            self.bet(player, player.stack)
        else:
            self.bet(player, player.get_to_call())

    def reset_bets(self):
        self.highest_bet=0
        for player in self.players:
            player.current_bet=0

    def make_flop(self):
        self.F=Street('F')
        self.find_active_players(self.F)
        self.reset_bets()

    def set_tournament(self, tournament):
        self.tournament=tournament

    def add_action(self, street, action):
        street.actions.append(action)
        player=action.player
        player.set_to_call(self)
        player.set_pot_odds(self)
        print("%s doit miser %s pour suivre. \nOdds= %s : 1\nReq.Equity= %s%%" %(player.name, player.to_call, round(player.pot_odds, 1),round(player.req_equity*100)))
        if action.move in ("fold", "folds"):
            player.fold()
        elif action.move in ("call", "calls", "checks", "check"):
            self.call(player)
        elif action.move in ("bet", "bets", "raise", "raises"):
            self.bet(player, action.value)
        #print("Décision: %s %s %s" % (player.name, action.move, action.value))
