from winamax import  *
from API.Table import *
from API.card import *
from API.hand import *
from API.winamax_re import *
import os
import re




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
files=os.listdir('history')

#route="C:\\Users\hp\Desktop\Poker\PokerBrain\history"
#files=os.listdir("history")

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


def parse_file(file_name):
    """Takes a file for a tournament (Winamax) and parses its hands """
    #File opening
    file=open("history/%s"%(file_name), "r")

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
            #print(index)
            header=header = re.match(_header_re, content[i])
            hh=WinamaxHandHistory(content[i])
            i+=1
            # find table pattern and parse its information with a new Table object with Tournaent information
            hh.parse_table(content[i])
            hh.set_table()
            hh.set_tournament()

            #print("New Hand: %s\nTournament Id: %s\n%s-max"%(hh.ident,hh.table.tournament.id, hh.table.max_players))
            #print("\nTournament ID: %s, Table ID: %s. On joue en %s-max en %s money. Le siège n° %s est Btn" %(hh.table.tournament.id, hh.table.id, hh.table.max_players, hh.table.tournament.money_type, hh.button_seat))
            i+=1
            #Step :Looking for players on seats, and adding Player objects to the table for every player found
            while(re.search(_seat_re, content[i])):
                hh.parse_player(content[i])
                i+=1

            #Step : Analysing Ante and blinds
            i+=1
            #for player in hh.table.players:
             #   print("%s Occupe le siège n°%s avec un stack de %s" %(player.name, player.seat, player.stack))
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
            #print("Pot:", hh.table.pot, "Highest Bet:", hh.table.highest_bet)

            if (re.search(_hero_cards_re, content[i])):
                hh.parse_hero(content[i])
                i+=1
            #finding active players for PF (it's all of them)
            hh.table.find_active_players(hh.table.PF)
            #PF Actions
            #print("\n", content[i])
            i+=1
            #PF Actions are parsed into PF street, and added to the table
            #Tant qu'on a des patterns d'actions:
            while (re.search(_action_re, content[i])):
                #On trouve le pattern d'action et on affecte ses groupes dans un objet action, qu'on ajoute à la liste des actions. On pourra ensuite la trier.
                hh.parse_action(content[i], hh.table.PF)
                i+=1
            #print("Pot:", hh.table.pot, "Highest Bet:", hh.table.highest_bet)
            #print("\n", content[i])
            #If we have a flop pattern,  we parse its cards
            flop = re.search(_flop_re, content[i])
            if flop:
                hh.table.make_flop()
                hh.parse_flop_cards(content[i])
                i+=1
                #Next step of flop: parsing actions
                while (re.search(_action_re, content[i])):
                    hh.parse_action(content[i], hh.table.F)
                    i+=1
                #print("Pot:", hh.table.pot, "\nHighest Bet:", hh.table.highest_bet)
                #If we find a turn pattern, we parse its card
                turn = re.search(_turn_re, content[i])
                #print("\n",content[i])
                if turn:
                    hh.table.make_turn()
                    hh.parse_turn_card(content[i])
                    i += 1
                    #Next step of turn parsing actions:
                    while (re.search(_action_re, content[i])):
                        hh.parse_action(content[i], hh.table.T)
                        i += 1
                #print("Pot:", hh.table.pot, "\nHighest Bet:", hh.table.highest_bet)
                #If we find a river pattern, we parse its card
                river = re.search(_river_re, content[i])
                #print("\n", content[i])
                if river:
                    hh.table.make_river()
                    hh.parse_river_card(content[i])
                    i += 1
                    #Next step of river is parsing actions:
                    while (re.search(_action_re, content[i])):
                        hh.parse_action(content[i], hh.table.R)
                        i += 1
                    # Looking for a showdown pattern
                    showdown = re.search(_showdown_re, content[i])
                    if showdown:
                        hh.table.make_showdown()
                        #print("\n", content[i])
                        i += 1
                        #Parsing SD actions
                        while (re.search(_showdown_action_re, content[i])):
                            hh.parse_sd_action(content[i], hh.table.SD)
                            i += 1
            while (re.search(_winner_re, content[i])):
                hh.parse_winner(content[i])
                i+=1
            hands.append(hh)
            index += 1
        i+=1
    file.close()
    return hands

def parse_directory(dir_name):
    hands=[]
    files=os.listdir(dir_name)
    for file_name in files:
        hands.extend(parse_file(file_name))
    return hands

hands=parse_directory('history')
try:
    hands[0].table.R
    print(1)
except:
    print(0)
