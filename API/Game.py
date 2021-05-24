from zope.interface import Interface, Attribute

class Game:
    """
    Classe définissant un tour de mains joué et toutes ses informations
    """

    #Attributs de la main
    game_id = Attribute("ID unique référençant la main jouée dans n'importe quelle base de données")
    game_type = Attribute("Tournoi /Cash Game/ SnG etc...")
    game_name = Attribute("Nom du tournoi ou du Cash Game")
    buy_in = Attribute("Coût d'entrée dans le tournoi/dans la partie de Cash Game")
    rake = Attribute("Rake Only")
    ante = Attribute("Ante size")
    sb = Attribute("Small blind")
    bb = Attribute("Big blind")
    level = Attribute ("Tournament level")
    variant = Attribute("Omaha, Hold'em, etc...")
    limit = Attribute("Limit/No limit / Pot limit")
    date = Attribute("Hand start Date and time")

    # Street informations
    preflop = Attribute("_Street instance for preflop actions.")
    flop = Attribute("_Street instance for flop actions.")
    turn = Attribute("_Street instance for turn actions.")
    river = Attribute("_Street instance for river actions.")
    show_down = Attribute("_Street instance for showdown.")

    # Player informations
    table_name = Attribute("Name of")
    max_players = Attribute("Maximum number of players can sit on the table.")
    players = Attribute("Tuple of player instances.")
    hero = Attribute("_Player instance with hero data.")
    button = Attribute("_Player instance of button.")
    winners = Attribute("Tuple of _Player instances with winners.")





    def __init__(self, game_id):
        self.id=game_id



