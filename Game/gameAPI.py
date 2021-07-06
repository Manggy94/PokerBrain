from API.Table import *
from API.Range import *
from winamax import WinamaxHandHistory as hh
import converter as conv


class Game:
    def __init__(self):
        self.hand = None
        self.level = None
        self.hero = None
        self.table = Table()
        print("New Game")

    def input_amount(self, msg: str = "Combien de jetons?\n"):
        try:
            amount = float(input(msg))
            if amount < 0:
                raise ValueError
            return amount
        except ValueError:
            print("Choisir un montant numérique positif")
            return self.input_amount()


    def input_level(self):
        try:
            nb = int(input("Level Number\n"))
            try:
                bb = float(input("Level Big Blind\n"))
                sb = bb / 2
                try:
                    ante = float(input("Level ante\n"))
                    if ante > 0.3 * bb or ante < 0:
                        raise ValueError
                    level = Level(number=nb, sb=sb, ante=ante, bb=bb)
                    self.set_level(level=level)
                    print("Niveau actuel: %s\nAnte=%s\nSmall Blind=%s\nBig Blind=%s" % (nb, ante, sb, bb))
                except ValueError:
                    ante = 0.125 * bb
                    level = Level(number=nb, sb=sb, ante=ante, bb=bb)
                    self.set_level(level=level)
                    print("En l'absence d'ante valide, le met à 1/8ème de la BB")
                    print("Niveau actuel: %s\nAnte=%s\nSmall Blind=%s\nBig Blind=%s" % (nb, ante, sb, bb))
            except ValueError:
                print("La grosse blinde doit être un nombre. Recommencez du début")
                self.input_level()
        except ValueError:
            print("Le niveau doit être un entier. Recommencez")
            self.input_level()

    def input_new_player(self):
        table = self.hand.table
        name = input("Nom du nouveau joueur?\n")
        occupied_seats = [player.seat for player in table.players]
        free_seats = [k for k in range(1, table.max_players + 1) if k not in occupied_seats]
        try:
            seat = int(input("Siège?\n"))
            if seat not in free_seats:
                raise ValueError
            stack = self.input_amount("Stack?\n")
            player = Player(name=name, seat=seat, stack=stack)
            self.hand.table.add_player(player=player)
            print("Nouveau joueur:", player.name)
        except ValueError:
            print("Choissez un siège comprise entre 1 et %s, et un stack numérique positif.")
            self.input_new_player()

    def input_hero(self):
        table = self.hand.table
        try:
            seat = int(input("Choisir le siège du héros\n"))
            if seat not in range(1, self.table.max_players+1):
                raise ValueError
            stack = float(input("Quel est votre stack?\n"))
            if stack < 0:
                raise ValueError
            hero = Player(name="Manggy94", seat=seat, stack=stack)
            hero.hero = True
            self.hand.table.add_player(player=hero)
            self.hero = hero
            print("Vous êtes assis au siège %s avec un stack de %s" % (hero.seat, hero.stack))
        except ValueError:
            print("Choissez un siège comprise entre 1 et %s, et un stack numérique positif." % self.table.max_players)
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
        def sorter(player: Player):
            return player.seat
        table.players.sort(key=sorter)

        print("Liste des joueurs à la table:")
        for player in table.players:
            print(player.name)

    def complete_table(self):
        table = self.hand.table
        occupied_seats = [player.seat for player in table.players]
        new_seats = [k for k in range(1, table.max_players+1) if k not in occupied_seats]
        for seat in new_seats:
            player = Player(name="Villain %s" % seat, seat=seat, stack=20000.0)
            table.add_player(player)

    def input_max_players(self):
        try:
            max_players = int('0'+input("Combien de joueurs max à cette table?\n"))
            if max_players in range(2, 10):
                self.hand.table.max_players = max_players
                print("Nombre Maximum de joueurs à la table: %s \n" % self.hand.table.max_players)
            else:
                raise ValueError
        except ValueError:
            print("Vous devez choisir un entier entre 2 et 10")
            self.input_max_players()

    def input_tournament(self):
        table = self.hand.table
        choice = None
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
            tournament = Tournament(name=name, buyin=buyin, rake=buyin/10)
            table.tournament = tournament
        print("Tournoi %s: %s\nBuy-in %s€" % (table.tournament.platform, table.tournament.name, table.tournament.buyin))

    def new_hand(self):
        self.hand = None
        self.hand = hh()
        self.hand.table = self.table
        self.input_max_players()
        self.hand.table.tournament = Tournament()
        self.input_tournament()
        self.input_level()
        self.input_players()
        self.choose_bb()
        self.input_hero_combo()

        # print(self.hand.table.tournament.buyin, "€")

    def set_level(self, level: Level):
        self.hand.level = level
        self.level = level


    def input_buyin(self):
        try:
            buyin = float(input("Buy-in (en  €)\n"))
            return buyin
        except ValueError:
            print("Vous devez insérer un Buy-In numérique")
            return self.input_buyin()

    def choose_bb(self):
        table = self.hand.table
        bb_seat = int(input("Choisissez le siège de la BB\n"))
        for player in table.players:
            player.position = None
            if player.seat == bb_seat:
                player.position = Position("BB")
        # print(table.players)
        table.distribute_positions()
        print("Résumé des positions:")
        for player in table.players:
            print(player.seat, player.name, player.position)
        # for player in table.players:
        #    print(player.name, player.position)

    def pregame_posting(self):
        hand = self.hand
        table = hand.table
        for player in table.players:
            table.post_ante(player, hand.level.ante)
            if player.position == Position("SB"):
                table.bet(player, hand.level.sb)
            elif player.position == Position("BB"):
                table.bet(player, hand.level.bb)

    def input_hero_combo(self):
        try:
            combo = Combo(input("Entrez vos 2 cartes\n"))
            self.hero.combo = combo
            print("On vous a distribué: %s" %combo)
        except ValueError:
            print("Il faut 2 cartes style 'AdKd'")
            return self.input_hero_combo()



game = Game()
game.new_hand()
hand = game.hand
player = hand.table.players[0]
a, b = conv.player_history_to_vec(player,hand)
print(a.shape, b.shape)
print(a)
print(b)

