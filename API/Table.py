from API.constants import *
import API.constants as cst
from API.hand import *
from API.card import *
import random
import numpy as np
import itertools
from cached_property import cached_property

all_combos = np.hstack([hand.to_combos() for hand in list(Hand)])


class PositionError(Exception):
    pass


class TableEvaluationError(Exception):
    pass


class Street:
    """Class initiating a Street with its players and actions"""

    def __init__(self, name):
        # print(f"\nNew Street: {name}")
        self.name = name
        self.cards = []
        self.active_players = []
        self.actions = []
        self.street_pot = 0
        self.highest_bet = 0
        self.index = 0
        self.it = None
        self.init_pl = None
        self.current_pl = None

    def add_action(self, action):
        self.actions.append(action)
        player = action.player
        player.set_to_call(self)
        player.set_pot_odds(self)
        if action.move in ("fold", "folds"):
            player.fold()
        elif action.move in ("call", "calls", "checks", "check"):
            self.call(player)
        elif action.move in ("bet", "bets"):
            self.bet(player, action.value)
        elif action.move in ("raise", "raises"):
            self.bet(player, player.to_call+action.value)

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

    def get_action(self, i):
        try:
            return self.actions[i]
        except IndexError:
            return None

    def get_action_info(self, i):
        try:
            action = self.actions[i]
            return action.player.seat, action.move, action.value
        except IndexError:
            return None, None, None

    def get_actions_infos(self, n: int = 24):
        return np.hstack([self.get_action_info(i) for i in range(n)])

    @property
    def remaining_players(self):
        return [pl for pl in self.active_players if not pl.folded]

    @property
    def not_all_in_players(self):
        return [pl for pl in self.remaining_players if not pl.is_all_in]

    def reset_bets(self):
        self.highest_bet = 0
        for player in self.active_players:
            player.current_bet = 0

    def update_table(self):
        for i in range(len(self.active_players)):
            pl = self.active_players[i]
            if pl.folded:
                print(f"{pl.name} folded and is off this hand")
                self.active_players.remove(pl)

    def next_player(self):
        try:
            pl = next(self.it)
            # print("on passe direct au suivant")
            return pl
        except StopIteration:
            self.it = iter(self.remaining_players)
            # print("On est au bout de la liste, on renouvelle l'itérateur au début")
            return next(self.it)
        except TypeError:
            self.it = iter(self.remaining_players)
            # print("On doit créér l'itérateur")
            return next(self.it)


class Action:
    """Classe qui définit les différentes actions possibles d'un joueur pendant une main"""
    def __init__(self, player, move: cst.Action, value):
        self.player = player
        self.move = move
        if value:
            self.value = value
        else:
            self.value = 0

    def __str__(self):
        return f"{self.player.name} {self.move} for {self.value}"


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
    def __init__(self, ident: str = 'x', name: str = 'Kill The Fish', buyin: float = 5.0,
                 money_type: str = 'real'):
        self._id = ident
        self._name = name
        self._buyin = buyin
        self._money_type = money_type

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id_txt: str):
        self._id = id_txt

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name_txt):
        self._name = name_txt

    @property
    def buyin(self):
        return self._buyin

    @buyin.setter
    def buyin(self, amount):
        try:
            self._buyin = float(amount)
        except TypeError:
            pass

    @property
    def money_type(self):
        return self._money_type

    @money_type.setter
    def money_type(self, money_type):
        self._money_type = money_type

    def __str__(self):
        return f"Name: {self.name}\nId: {self.id}\nBuy-in: {self.buyin}\nMoney: {self.money_type}"


class Level:
    """Level of the tournament"""
    def __init__(self, level: int = 0,  bb: float = 0.0, ante: float = 0.0):
        self._level = level
        self._sb = bb/2
        self._bb = bb
        self._ante = ante

    def __str__(self):
        return f"Current level: {self.level}\nAnte={self.ante}\nSB={self.sb}\nBB={self.bb}"

    @property
    def bb(self):
        return self._bb

    @bb.setter
    def bb(self, bb):
        if bb < 0:
            raise ValueError("BB Value must be positive")
        else:
            self._bb = bb
            self._sb = bb/2

    @property
    def sb(self):
        return self._sb

    @property
    def ante(self):
        return self._ante

    @ante.setter
    def ante(self, ante):
        if ante < 0:
            raise ValueError("Ante must be positive")
        else:
            self._ante = ante

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        self._level = level


class Player:
    """"""
    def __init__(self, name: str = None, seat: int = None, stack: float = None):
        self._name = name
        self._seat = seat
        self._stack = stack
        self.init_stack = stack
        self._combo = None
        self.folded = False
        self._hero = False
        self.current_bet = 0
        # self._to_call = None
        self._position = None
        self.actions = []
        self.played = False

    def __str__(self):
        return f"Name: {self.name}\nSeat: {self.seat}\nStack: {self.stack}\nHero: {self.is_hero}\nCombo: {self.combo}"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        if len(name) > 12:
            raise ValueError
        else:
            self._name = name

    @property
    def seat(self):
        try:
            return self._seat
        except AttributeError:
            return None

    @seat.setter
    def seat(self, seat: int):
        if seat < 0 or seat > 10:
            raise ValueError
        else:
            self._seat = seat

    @property
    def stack(self):
        return self._stack

    @stack.setter
    def stack(self, stack):
        if stack < 0:
            self._stack = 0
        else:
            self._stack = stack

    @property
    def combo(self):
        return self._combo

    @combo.setter
    def combo(self, combo: Combo):
        self._combo = combo

    @property
    def has_combo(self) -> bool:
        return self._combo is not None

    @property
    def is_hero(self) -> bool:
        return self._hero

    @is_hero.setter
    def is_hero(self, is_hero):
        self._hero = is_hero

    def shows(self, combo):
        self._combo = combo

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._position = position

    @property
    def is_all_in(self):
        return self.stack == 0

    def fold(self):
        self.folded = True

    def reset(self):
        self.folded = False

    def reset_street_status(self):
        self.played = False

    def to_call(self, table):
        return table.highest_bet-self.current_bet

    def can_play(self, table):
        return not (self.is_all_in or (self.to_call(table) == 0 and self.played))

    def pot_odds(self, table):
        to_call = self.to_call(table)
        if to_call != 0:
            pot_odds = table.pot/to_call
        else:
            pot_odds = float("inf")
        return pot_odds

    def req_equity(self, table):
        return 1/(1+self.pot_odds(table))


class Players:
    """"""
    preflop_starter = "BB"
    postflop_starter = "BTN"

    def __init__(self):
        self.pl_list = []
        self.name_dict = {}
        self.seat_dict = {}
        self.positions = {}

    def append(self, player):
        self.pl_list.append(player)
        self.name_dict[player.name] = player
        self.seat_dict[player.seat] = player

    def __getitem__(self, item):
        try:
            if type(item) == str:
                return self.name_dict[item]
            elif type(item) == int:
                return self.seat_dict[item]
        except KeyError:
            raise KeyError

    def __len__(self):
        return self.name_dict.__len__()

    def __contains__(self, item):
        return self.pl_list.__contains__(item)

    def __iter__(self):
        return self.pl_list.__iter__()

    def find(self, name: str):
        try:
            return self.name_dict[name]
        except KeyError:
            print(f"{name} is not currently on this table")


class Table:
    """"""
    def __init__(self, ident="No Id", max_players: int = 6):
        self.ident = ident
        self._max_players = max_players
        self.board = []
        self.players = Players()
        self.highest_bet = 0
        self.streets = [Street('PreFlop')]
        self._hero = None
        self._pot = 0
        self.progression = 0
        self.current_street = self.streets[0]
        self.deck = list(Card)
        random.shuffle(self.deck)

    def __str__(self):
        return f"Table n° {self.ident} of {self.max_players} players max"

    @property
    def max_players(self):
        return self._max_players

    @max_players.setter
    def max_players(self, max_value):
        if max_value < 0 or max_value > 10:
            raise ValueError
        else:
            self._max_players = max_value

    @property
    def pot(self):
        return self._pot

    @pot.setter
    def pot(self, pot):
        self._pot = pot

    def add_action(self, street: Street, action: Action):
        street.actions.append(action)
        player = action.player
        player.played = True
        player.actions.append({"street": street.name, "move": action.move, "value": action.value})
        if action.move == cst.Action("fold"):
            player.fold()
        elif action.move in [cst.Action("call"), cst.Action("check")]:
            self.call(player)
            if street.init_pl is None:
                street.init_pl = player
        elif action.move == cst.Action("bet"):
            self.bet(player, action.value)
            street.init_pl = player
        elif action.move == cst.Action("raise"):
            self.bet(player, player.to_call(self)+action.value)
            street.init_pl = player

    def add_player(self, player):
        self.players.append(player)
        player.init_stack = player.stack

    def bet(self, player, amount):
        self.pot = self.pot + amount
        player.stack -= amount
        player.current_bet += amount
        if player.current_bet > self.highest_bet:
            self.highest_bet = player.current_bet

    def call(self, player):
        if player.stack < player.to_call(self):
            self.bet(player, player.stack)
        else:
            self.bet(player, player.to_call(self))

    def distribute_cards(self, player):
        player.combo = Combo(f"{self.draw_card()}{self.draw_card()}")

    def distribute_positions(self):
        a = len(self.players)
        bb = self.players.positions["BB"]
        player = self.players[bb]
        if a < 6:
            positions = list(Position)[10-a:]
        else:
            positions = list(Position)[0:a-5]
            positions.extend(list(Position)[5:])
        keys = sorted(self.players.seat_dict)
        cut = keys.index(player.seat)
        idx = np.hstack((keys[cut+1:], keys[:cut], player.seat))
        for (i, j) in zip(idx, positions):
            self.players.seat_dict[i].position = j
            self.players.positions[str(j)] = self.players.seat_dict[i]

    def draw_card(self, string: str = None):
        if string:
            card = Card(string)
            idx = self.deck.index(card)
            self.deck.pop(idx)
        else:
            card = self.deck.pop()
        return card

    def find_active_players(self, street):
        i = street.index
        keys = sorted(self.players.seat_dict)
        try:
            btn = self.players.positions["BTN"]
        except KeyError:
            copy = self.players.positions.copy()
            if copy:
                pl = copy.popitem()
                btn = pl[1]
            else:
                raise PositionError
        try:
            bb = self.players.positions["BB"]
        except KeyError:
            raise PositionError
        if i == 0:
            player = bb
        else:
            player = btn
        cut = keys.index(player.seat)
        idx = np.hstack((keys[cut + 1:], keys[:cut], player.seat))
        active_players = [self.players.seat_dict[k] for k in idx]
        for pl in active_players:
            if not pl.folded:
                self.streets[i].active_players.append(pl)

    @property
    def flop_card_1(self):
        try:
            return str(self.board[0])
        except IndexError:
            return None

    @property
    def flop_card_2(self):
        try:
            return str(self.board[1])
        except IndexError:
            return None

    @property
    def flop_card_3(self):
        try:
            return str(self.board[2])
        except IndexError:
            return None

    @cached_property
    def flop_combinations(self):
        try:
            return [x for x in itertools.combinations(self.board[:3], 2)]
        except IndexError:
            return None

    def _get_differences(self):
        return (
            Rank.difference(first.rank, second.rank)
            for first, second in self.flop_combinations
        )

    @cached_property
    def is_rainbow(self):
        if len(self.board) == 0:
            return None
        return all(
            first.suit != second.suit for first, second in self.flop_combinations
        )

    @cached_property
    def is_monotone(self):
        if len(self.board) == 0:
            return None
        return all(
            first.suit == second.suit for first, second in self.flop_combinations
        )

    @cached_property
    def is_triplet(self):
        if len(self.board) == 0:
            return None
        return all(
            first.rank == second.rank for first, second in self.flop_combinations
        )

    @cached_property
    def has_pair(self):
        if len(self.board) == 0:
            return None
        return any(
            first.rank == second.rank for first, second in self.flop_combinations
        )

    @cached_property
    def has_straightdraw(self):
        if len(self.board) == 0:
            return None
        return any(1 <= diff <= 3 for diff in self._get_differences())

    @cached_property
    def has_gutshot(self):
        if len(self.board) == 0:
            return None
        return any(1 <= diff <= 4 for diff in self._get_differences())

    @cached_property
    def has_flushdraw(self):
        if len(self.board) == 0:
            return None
        return any(
            first.suit == second.suit for first, second in self.flop_combinations
        )

    @property
    def turn_card(self):
        try:
            return str(self.board[3])
        except IndexError:
            return None

    @property
    def river_card(self):
        try:
            return str(self.board[4])
        except IndexError:
            return None

    def get_card(self, i):
        try:
            return str(self.board[i])
        except IndexError:
            return None

    def get_total_board(self):
        return np.array([self.get_card(i) for i in range(5)])

    def get_partial_board(self, progress: int):
        if progress == 0:
            return np.array([None]*5)
        else:
            return np.hstack(([self.get_card(i) for i in range(progress + 2)], [None] * (3 - progress)))

    def get_player(self, i: int):
        try:
            return self.players[i]
        except IndexError:
            return None

    def get_player_infos(self, i):
        try:
            player = self.players[i]
            return player.name, player.seat, player.stack, str(player.position), str(player.combo), bool(player.hero)
        except IndexError:
            return None, None, None, None, None, None

    def get_all_players_info(self):
        return np.hstack([self.get_player_infos(i) for i in range(9)])

    def get_street(self, i):
        try:
            return self.streets[i]
        except IndexError:
            return Street("")

    def get_table_action_info(self, n: int = 24):
        streets = [self.get_street(i) for i in range(4)]
        return np.hstack([street.get_actions_infos(n) for street in streets])

    def get_consecutive_actions(self):
        k = 0
        actions = self.get_table_action_info()
        all_actions = self.get_table_action_info().reshape(1, 288)
        prog = 3
        progress = [prog]
        all_boards = self.get_partial_board(prog)
        while k < 96:
            i = 287-3*k
            prog = i // 72
            # print(actions[i],actions[:i+1].shape, actions[i+1:].shape, 287-i)
            if actions[i]:
                progress.append(prog)
                part_actions = np.hstack((actions[:i+1], [None]*(287-i)))
                all_actions = np.vstack((all_actions, part_actions))
                all_boards = np.vstack((all_boards, self.get_partial_board(prog)))
            k += 1
        return all_actions, np.array(progress), all_boards

    @cached_property
    def has_flop(self):
        return len(self.streets) >= 2

    @property
    def has_hero(self):
        return self.hero is not None

    @property
    def has_river(self):
        return len(self.streets) >= 4

    @property
    def has_showdown(self):
        return len(self.streets) >= 5

    @property
    def has_turn(self):
        return len(self.streets) >= 3

    def make_flop(self):
        flop = Street('Flop')
        self.streets.append(flop)
        flop.index = 1
        self.find_active_players(flop)
        self.reset_bets()
        self.progression += 1
        self.current_street = flop

    def make_river(self):
        river = Street('River')
        self.streets.append(river)
        river.index = 3
        self.find_active_players(river)
        self.reset_bets()
        self.progression += 1
        self.current_street = river

    def make_showdown(self):
        showdown = Street('ShowDown')
        self.streets.append(showdown)
        self.progression += 1
        showdown.index = self.progression
        self.find_active_players(showdown)
        self.reset_bets()
        self.current_street = showdown

    def make_turn(self):
        turn = Street('Turn')
        self.streets.append(turn)
        turn.index = 2
        self.find_active_players(turn)
        self.reset_bets()
        self.progression += 1
        self.current_street = turn

    def post_ante(self, player, amount):
        self.pot += amount
        player.stack -= amount

    def reset_bets(self):
        self.reset_played()
        pass
        # self.highest_bet = 0
        # for player in self.players:
        # player.current_bet = 0

    def reset_played(self):
        for pl in self.current_street.active_players:
            pl.played = False

    @property
    def hero(self):
        try:
            return self._hero
        except AttributeError:
            self._hero = Player("no_hero")
            return self._hero

    @hero.setter
    def hero(self, hero: Player):
        self._hero = hero

    def win(self, player, amount):
        self.pot -= amount
        player.stack += amount


class HandHistory:
    """Winamax specific parsing."""

    def __init__(self):
        self.hand_id = None
        self.pk_type = None
        self._tournament = None
        self._table = None
        self._money_type = None
        self._button_seat = None
        self._level = None
        self._ante = 0
        self._sb = 0
        self._bb = 0
        self._ante = 0

    def __str__(self):
        return f"Hand_id: {self.hand_id}\n\nTournament\n{self.tournament}\n\nLevel\n{self.level}\n\n" \
               f"Button\n{self.button}\n\nTable\n{self.table}\n\n"

    @property
    def tournament(self):
        return self._tournament

    @tournament.setter
    def tournament(self, tournament: Tournament):
        self._tournament = tournament

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level: Level):
        self._level = level
        self._sb = level.sb
        self._bb = level.bb
        self._ante = level.ante

    @property
    def button(self):
        return self._button_seat

    @button.setter
    def button(self, seat: int):
        if seat < 1 or seat > 10:
            raise ValueError
        else:
            self._button_seat = seat

    @property
    def table(self):
        return self._table

    @table.setter
    def table(self, table: Table):
        self._table = table

    def get_hand_info(self):
        return self.tournament.id, self.table.ident, self.level.nb, self.level.bb, self.level.ante, \
               self.table.max_players, self.button, self.tournament.buyin, self.table.hero.seat, self.table.hero.combo

    def get_board_card(self, i):
        return self.table.get_card(i)

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

    def get_table_action_info(self, n: int = 24):
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
            i = 287 - 3 * k
            prog = i // 72
            # print(actions[i],actions[:i+1].shape, actions[i+1:].shape, 287-i)
            if actions[i]:
                progress.append(prog)
                part_actions = np.hstack((actions[:i + 1], [None] * (287 - i)))
                all_actions = np.vstack((all_actions, part_actions))
                all_boards = np.vstack((all_boards, self.get_partial_board(prog)))
                info = np.vstack((info, self.get_hand_info()))
                pl_info = np.vstack((pl_info, self.get_all_players_info()))
            k += 1
        n = all_actions.shape[0]
        idents = [self.hand_id] * n
        return all_actions, np.array(progress), all_boards, idents, info, pl_info
