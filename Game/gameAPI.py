from API.Table import *
from preprocessor import Preprocessor

all_combos = np.array([], dtype=np.str)
all_hands = np.array(list(Hand), dtype=np.object)

for hand in all_hands:
    all_combos = np.hstack((all_combos, hand.to_combos()))


class Game:
    def __init__(self):
        print("New Game")
        self.hand = None
        self.hand_df_line = None
        self.level = None
        self.hero = None
        self.table = Table()
        self.temporary_history = np.array([])
        self.pp = Preprocessor()
        self.history = None

    def input_amount(self, msg: str = "How many chips?\n"):
        try:
            amount = float(input(msg))
            if amount < 0:
                raise ValueError
            return amount
        except ValueError:
            print("Choose a positive numeric value")
            return self.input_amount()

    def input_level(self):
        try:
            nb = int(input("Level Number\n"))
            try:
                bb = float(input("Level Big Blind\n"))
                try:
                    ante = float(input("Level ante\n"))
                    if ante > 0.3 * bb or ante < 0:
                        raise ValueError
                    level = Level(level=nb, ante=ante, bb=bb)
                    self.set_level(level=level)
                    print(level)
                except ValueError:
                    ante = 0.125 * bb
                    level = Level(level=nb, ante=ante, bb=bb)
                    self.set_level(level=level)
                    print("Without a correct ante, it's 1/8th of BB")
                    print(level)
            except ValueError:
                print("Big blind must be a float. Try again")
                self.input_level()
        except ValueError:
            print("Level must be an int. Try again")
            self.input_level()

    def input_new_player(self):
        table = self.hand.table
        name = input("Player Name?\n")
        occupied_seats = [player.seat for player in table.players]
        free_seats = [k for k in range(1, table.max_players + 1) if k not in occupied_seats]
        try:
            seat = int(input("Seat?\n"))
            if seat not in free_seats:
                raise ValueError
            stack = self.input_amount("Stack?\n")
            player = Player(name=name, seat=seat, stack=stack)
            self.hand.table.add_player(player=player)
            print("New Player:", player.name)
        except ValueError:
            print(f"Choose a seat between 1 and {table.max_players}, and a positive numeric stack.")
            self.input_new_player()

    def input_hero(self):
        try:
            seat = int(input("Choose Hero's Seat\n"))
            if seat not in range(1, self.table.max_players+1):
                raise ValueError
            stack = float(input("What's your stack?\n"))
            if stack < 0:
                raise ValueError
            hero = Player(name="Manggy94", seat=seat, stack=stack)
            hero.is_hero = True
            self.hand.table.add_player(player=hero)
            self.hero = hero
            print(f"You're at seat n°{hero.seat} with {hero.stack} chips")
        except ValueError:
            print(f"Choissez un siège comprise entre 1 et {self.table.max_players}, et un stack numérique positif.")
            self.input_hero()

    def input_players(self):
        table = self.hand.table
        self.input_hero()
        choice = None
        while choice != 0 and len(table.players) < table.max_players:
            try:
                choice = int(input("Voulez vous ajouter un autre joueur? \n0:Non\n1:Oui\n"))
                if choice not in range(2):
                    raise ValueError
            except ValueError:
                print("Mauvaise saisie, complétion par défaut")
                choice = 0
            if choice:
                self.input_new_player()
            else:
                try:
                    choice2 = int(input("Voulez vous compléter la table? \n0:Non\n1:Oui\n"))
                    if choice2 not in range(2):
                        raise ValueError
                except ValueError:
                    print("Mauvaise saisie, complétion par défaut")
                    choice2 = 1
                if choice2:
                    self.complete_table()
        print("Liste des joueurs à la table:")
        s_dict = table.players.seat_dict
        print([s_dict[i].name for i in sorted(s_dict)])

    def complete_table(self):
        table = self.hand.table
        occupied_seats = table.players.seat_dict
        new_seats = [k for k in range(1, table.max_players+1) if k not in occupied_seats]
        for seat in new_seats:
            player = Player(name=f"Villain {seat}", seat=seat, stack=20000.0)
            table.add_player(player)

    def input_max_players(self):
        try:
            max_players = int('0'+input("Combien de joueurs max à cette table?\n"))
            if max_players in range(2, 10):
                self.hand.table.max_players = max_players
                print(f"Nombre Maximum de joueurs à la table: {self.hand.table.max_players}\n")
            else:
                raise ValueError
        except ValueError:
            print("Vous devez choisir un entier entre 2 et 10")
            self.input_max_players()

    def input_tournament(self):
        table = self.hand.table
        try:
            choice = int(input("Voulez-vous changer le format du tournoi? \n0:Non\n1:Oui\n"))
            if choice not in [0, 1]:
                raise ValueError
        except ValueError:
            print("Vous devez choisir entre 0 pour Non et 1 pour Oui")
            return self.input_tournament()
        if choice:
            name = input("Nom du tournoi\n")
            buyin = self.input_buyin()
            tournament = Tournament(name=name, buyin=buyin)
            hand.tournament = tournament
        print(f"Touroi {table.tournament.name}\nBuy-in {table.tournament.buyin}€")

    def new_game(self):
        try:
            choice = int(input("Voulez-vous créér une nouvelle table ou changer l'actuelle? \n0:Non\n1:Oui\n"))
            if choice not in [0, 1]:
                raise ValueError
        except ValueError:
            print("Vous devez choisir entre 0 pour Non et 1 pour Oui")
            return self.new_game()
        if choice:
            self.hand = None
            self.hand = HandHistory()
            self.hand.table = self.table
            self.input_max_players()
            self.hand.table.tournament = Tournament()
            self.input_tournament()
            self.input_level()
            self.input_players()

    def set_level(self, level: Level):
        self.hand.level = level
        self.level = level

    def input_buyin(self):
        try:
            buyin = float(input("Buy-in (en €)\n"))
            return buyin
        except ValueError:
            print("Vous devez insérer un Buy-In numérique")
            return self.input_buyin()

    def choose_bb(self):
        bb_seat = int(input("Choisissez le siège de la BB\n"))
        bb_pl = self.hand.table.players.seat_dict[bb_seat]
        bb_pl.position = Position("BB")
        self.hand.table.players.positions[str(bb_pl.position)] = bb_pl.seat
        self.hand.table.distribute_positions()
        self.hand.button = self.hand.table.players.positions["BTN"].seat
        s_dict = self.hand.table.players.seat_dict
        print(f"Résumé des positions: {[(s_dict[i].seat, s_dict[i].name, s_dict[i].position) for i in sorted(s_dict)]}")

    def pregame_posting(self):
        for pl in self.hand.table.players:
            self.hand.table.post_ante(pl, self.hand.level.ante)
            print(f"{pl.name} posts ante {self.hand.level.ante}")
            if pl.position == Position("SB"):
                self.hand.table.bet(pl, self.hand.level.sb)
            elif pl.position == Position("BB"):
                self.hand.table.bet(pl, self.hand.level.bb)

    def input_hero_combo(self):
        try:
            combo = Combo(input("Entrez vos 2 cartes\n"))
            self.hand.table.draw_card(combo.first)
            self.hand.table.draw_card(combo.second)
            self.hero.combo = combo
            print(f"On vous a distribué:{combo}")
        except ValueError:
            print("Il faut 2 cartes style 'AdKd'")
            return self.input_hero_combo()

    def play_hand(self):
        self.hand.table.find_active_players(self.hand.table.current_street)
        self.input_street_actions()
        print(self.hand.table.current_street.remaining_players)
        if len(self.hand.table.current_street.remaining_players) > 1:
            self.hand.table.make_flop()
            self.input_flop()
            if len(self.hand.table.current_street.remaining_players) > 1:
                self.hand.table.make_turn()
                self.input_turn()
                if len(self.hand.table.current_street.remaining_players) > 1:
                    self.hand.table.make_river()
                    self.input_river()
                    if len(self.hand.table.current_street.remaining_players) > 1:
                        self.hand.table.make_showdown()
                        self.input_showdown()

        else:
            raise TableEvaluationError

    def input_action(self, pl: Player, street: Street):
        phr = ""
        to_call = pl.to_call(self.hand.table)
        odds = pl.pot_odds(self.hand.table)
        req_eq = pl.req_equity(self.hand.table)
        print(f"{pl.name} ({pl.position}) plays with {pl.stack} chips. Pot: {self.hand.table.pot}, {to_call} to call, "
              f"Odds:{odds} vs 1.\nRequired Equity: {req_eq}\n")
        ch = ["Fold", "Check", "Call", "Bet", "Raise"]
        if to_call != 0:
            ch.remove("Check")
            ch.remove("Bet")
        else:
            ch.remove("Call")
            ch.remove("Raise")
        if to_call >= pl.stack:
            ch.remove("Raise")
        for x in ch:
            phr += f"{ch.index(x)}:{x} "
        try:
            choice = int(input(f"{phr}"))
            if choice not in range(len(ch)):
                raise ValueError
            else:
                action = None
                move = ch[choice]
                if move in cst.Action("fold").value:
                    action = Action(player=pl, move=cst.Action("fold"), value=0.0)
                elif move in cst.Action("check").value:
                    action = Action(player=pl, move=cst.Action("check"), value=0.0)
                elif move in cst.Action("call").value:
                    action = Action(player=pl, move=cst.Action("calls"), value=to_call)
                elif move in cst.Action("bet").value:
                    amount = self.input_amount()
                    action = Action(player=pl, move=cst.Action("bets"), value=amount)
                elif move in cst.Action("raise").value:
                    amount = self.input_amount()
                    action = Action(player=pl, move=cst.Action("raises"), value=amount-to_call)
                print(action)
                self.hand.table.add_action(street=street, action=action)
        except ValueError:
            print("Choisissez une action entre 0 et 4")
            self.input_action(pl, street)

    def input_sd_action(self, pl: Player):
        try:
            combo = Combo(input(f"{pl.name} shows:"))
            pl.shows(combo=combo)
        except ValueError:
            print("Il faut 2 cartes style 'AdKd'")
            return self.input_sd_action(pl=pl)

    def input_street_actions(self):
        street = self.hand.table.current_street
        current_pl = street.next_player()
        street.current_pl = current_pl
        while (street.init_pl is not street.current_pl) and len(street.remaining_players) > 1:
            if street.current_pl.can_play(self.hand.table):
                self.input_action(pl=street.current_pl, street=street)
            else:
                print(f"{street.current_pl.is_all_in}, {street.current_pl.played}, "
                      f"{street.current_pl.to_call(self.hand.table)}")
            next_pl = street.next_player()
            if street.current_pl == next_pl:
                break
            street.current_pl = next_pl
        print(f"End of {street.name}")

    def input_flop(self):
        fc1 = Card(input("First flop card?"))
        fc2 = Card(input("Second flop card?"))
        fc3 = Card(input("Third flop card?"))
        self.table.draw_flop(fc1, fc2, fc3)
        self.input_street_actions()

    def input_turn(self):
        tc = Card(input("Turn card?"))
        self.table.draw_turn(tc)
        self.input_street_actions()

    def input_river(self):
        rc = Card(input("River card?"))
        self.table.draw_river(rc)
        self.input_street_actions()

    def input_showdown(self):
        pass

    def new_hand(self):
        self.new_game()
        self.choose_bb()
        self.input_hero_combo()
        self.pregame_posting()
        self.play_hand()
