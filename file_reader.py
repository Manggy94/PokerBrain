from winamax import  *
from API.Table import *
from API.card import *
from API.hand import *




"""
Modes d'ouverture:
r (lecture seule)
w(écriture avec remplacement)
a (écriture avec ajout en fin de fichier)
x (lecture et écriture)
r+ (lecture/écriture dans un même fichier)
On utilisera svt que les 2 premiers modes

Lecture d'un fichier:
read(), readline(), readlines()
"""
import os
import re

#route="C:\\Users\hp\Desktop\Poker\PokerBrain\history"
#files=os.listdir("history")


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
_table_re = re.compile(r"Table\:\s+\'(?P<tournament_name>[\w\s\']+)\((?P<tournament_id>\d+)\)\#(?P<table_id>\d+)\'\s+(?P<max_seat>\d+)\-max\s+\((?P<money_type>[a-z]+)\s+money\)\s+Seat\s+\#(?P<button>\d)\s+is\s+the\s+button")
_seat_re = re.compile(
    """Seat\s+(?P<seat>\d+)\:\s+                                        #Seat
    (?P<player_name>[\w\s-]{6,12})\s+                                              #Player_name
    \((?P<stack>\d+)\)                                                  #Stack
    """,
    re.VERBOSE
)
_pot_re = re.compile(r"Total\s+pot\s+(?P<total_pot>\d+)")
_ante_re=re.compile(r"(?P<player_name>[\w\s\-]{3,12})\s+posts\sante\s+(?P<amount>\d+)")
_board_re=re.compile(r"Board\:\s+\[(?P<board>[0-9AJKQshdc ]+)\]")
_action_re=re.compile(r"(?P<player_name>[\w\s\-]{6,12})\s+(?P<move>shows|checks|calls|folds|bets|raises)\s+(?P<value>\d+||\s+)")
_showdown_action_re=re.compile(r"(?P<player_name>[\w\s\-]{6,12})\s+(?P<move>shows|mucks)\s+\[(?P<card1>[AJKQ2-9shdc]{2})\s+(?P<card2>[AJKQ2-9shdc]{2})\]")
_flop_re=re.compile(r"\*\*\*\s+FLOP\s+\*\*\*\s+\[(?P<flop_card_1>[AJKQT2-9hscd]{2})\s+(?P<flop_card_2>[AJKQT2-9hscd]{2})\s+(?P<flop_card_3>[AJKQT2-9hscd]{2})\]")
_hero_cards_re=re.compile(r"Dealt\s+to\s+(?P<hero_name>[\w\s-]+)\s+\[(?P<card1>[AJKQT2-9hscd]{2})\s+(?P<card2>[AJKQT2-9hscd]{2})\]")
_turn_re=re.compile(r"\*\*\*\s+TURN\s+\*\*\*\s+\[.+\]\[(?P<turn_card>[AJKQT2-9hscd]{2})\]")
_river_re=re.compile(r"\*\*\*\s+RIVER\s+\*\*\*\s+\[.+\]\[(?P<river_card>[AJKQT2-9hscd]{2})\]")
_showdown_re=re.compile(r"\*\*\*\s+SHOW\s+DOWN\s+\*\*\*")
_summary_re=re.compile(r"\*\*\*\s+SUMMARY\s+\*\*\*")
_winner_re=re.compile(r"(?P<player_name>[\w\s\-]{6,12})\s+collected\s+(?P<amount>\d+)\s+")
_sb_re=re.compile(r"(?P<player_name>[\w\s\_]{3,12})\s+posts\s+small\s+blind\s+(?P<sb>\d+)")
_bb_re=re.compile(r"(?P<player_name>[\w\s\_]{3,12})\s+posts\s+big\s+blind\s+(?P<bb>\d+)")

#File opening
file=open("historyexample.txt", "r")

#File reading line by line until its end
content=file.readlines()
length=(len(content))
i=0
index=0
hands=[]
while i < length:
    #collecting different hand histories:


    #if a header pattern is found on a new line, create a new handhistory and parse header informations in first line
    if re.match(_header_re, content[i]):
        header=header = re.match(_header_re, content[i])
        hh=WinamaxHandHistory(content[i])
        i+=1
        # find table pattern and parse its information with a new Table object with Tournaent information
        hh.parse_table(content[i])
        hh.set_table()
        hh.set_tournament()

        print("New Hand: %s\nTournament Id: %s\n%s-max"%(hh.ident,hh.table.tournament.id, hh.table.max_players))
        #print("\nTournament ID: %s, Table ID: %s. On joue en %s-max en %s money. Le siège n° %s est Btn" %(hh.table.tournament.id, hh.table.id, hh.table.max_players, hh.table.tournament.money_type, hh.button_seat))
        i+=1
        #Step :Looking for players on seats, and adding Player objects to the table for every player found
        while(re.search(_seat_re, content[i])):
            hh.parse_player(content[i])
            i+=1

        #Step : Analysing Ante and blinds
        i+=1
        #for player in hh.table.players:
            #print("%s Occupe le siège n°%s avec un stack de %s" %(player.name, player.seat, player.stack))
        antes=[]
        while(re.search(_ante_re, content[i])):
            #print("\n", content[i])
            hh.parse_ante(content[i])
            i+=1
        #On identifie les sb et bb
        if (re.search(_sb_re, content[i])):
            hh.parse_sb(content[i])
            i+=1
        if (re.search(_bb_re, content[i])):
            hh.parse_bb(content[i])
            i+=1
        print("Pot:", hh.table.pot, "Highest Bet:", hh.table.highest_bet)

        if (re.search(_hero_cards_re, content[i])):
            hh.parse_hero(content[i])
            i+=1
        #finding active players for PF (it's all of them)
        hh.table.find_active_players(hh.table.PF)
        #PF Actions
        print("\n", content[i])
        i+=1
        #PF Actions are parsed into PF street, and added to the table
        #Tant qu'on a des patterns d'actions:
        while (re.search(_action_re, content[i])):
            #On trouve le pattern d'action et on affecte ses groupes dans un objet action, qu'on ajoute à la liste des actions. On pourra ensuite la trier.
            hh.parse_action(content[i], hh.table.PF)
            i+=1
        print("Pot:", hh.table.pot, "Highest Bet:", hh.table.highest_bet)
        #If we have a flop pattern,  we parse it
        flop = re.search(_flop_re, content[i])
        # Si il y a un flop, on passe au flop
        if flop:
            hh.table.make_flop()
            print(hh.table.F.active_players)
            hh.parse_flop_cards(content[i])
            print("\n", content[i])
            flop_card_1=flop.group("flop_card_1")
            flop_card_2=flop.group("flop_card_2")
            flop_card_3=flop.group("flop_card_3")
            print("Cartes du flop: %s, %s, %s" %(flop_card_1, flop_card_2, flop_card_3))
            #On passe à la suite du flop
            i+=1
            #print(flop.groups())
            #Si on a des patterns d'actions:
            actions_F=[]
            #print(content[i])
            while (re.search(_action_re, content[i])):
                action = re.search(_action_re, content[i])
                player_name = action.group("player_name")
                print(player_name)
                for player in hh.table.players:
                    if player.name==player_name:
                        action_player = player
                print (action_player)
                move = action.group("move")
                value = action.group("value")
                #action = Action(player, move, value)
                #print("Nouvelle action de %s qui %s %s" %(action.player, action.move, action.value))
                #actions_F.append(action)
                i+=1
            print (actions_F)
            #On recherche un pattern de turn
            turn = re.search(_turn_re, content[i])
            if turn:
                print("\n", content[i])
                turn_card=turn.group("turn_card")
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
                print(actions_T)
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
                print (actions_R)
                # On recherche un pattern de showdown
                showdown = re.search(_showdown_re, content[i])
                #En cas de Showdown
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
                        action=SDAction(player, move, SD_card_1, SD_card_2)

                        print("\n", action.player, action.move, action.card1, " and ", action.card2)
                        actions_SD.append(action)
                        i += 1
        winners=[]
        while (re.search(_winner_re, content[i])):
            winner=re.search(_winner_re, content[i])
            player = winner.group("player_name")
            amount = winner.group("amount")
            print("\n %s wins %s" %(player, amount))
            i+=1

        #print("Ligne %s: %s" % (i, content[i]))
    i+=1

file.close()