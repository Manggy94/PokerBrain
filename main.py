#import winamax as wina
import os
import re
import sys

file=open ("historyexample.txt", "r")
text=file.read()
file.close()

#print ("Winamax" in file)
print(text)

_card_re="AJKQcdhs1-9"
_split_re = re.compile(
    r""
    r"\n\n\n"
    r""
)
_header_re=re.compile(
    r""
    r"Winamax Poker\s+- "                                   #PokerRoom Name
    r"Tournament\s+\"(?P<tournament_name>[A-Za-z\']+)\""    #Tournament Name
    r"\s+buyIn\:\s+(?P<buy_in>[\d\.]+)â.."                  #buyIn
    r"\s+\+\s+(?P<rake>[\d\.]+)â.."                          #rake
    r"\s+level\:\s+(?P<level>[\d]+)"                        #level
    r"\s+\W+HandId\:\W+(?P<hand_id>[\d\-]+)"                #handId
    r"\W+Holdem no limit"                                   #Game Type
    r"\s+\((?P<ante>\d+)"                                 #ante
    r"\/(?P<sb>[\d]+)"                                      #small blind
    r"\/(?P<bb>[\d]+)"                                      #big blind
    r"\W+(?P<date_time>[\d\/\:\s]+UTC)"                     #Date
    r""
    r""
    r""
    r"")

_table_re=re.compile(
    r""
    r"Table\:\W+(?P<table_id>[\w\'\(\)\#\d]+)\'"            #Table Id
    r"\s+(?P<max_seats>\d+)\-max\s+\([\w\s]+\)\s+"        #Max Seats
    r"Seat\s+\#(?P<button>\d+)"                           #button
    r"\s+is\s+the\s+button"
)

_seat_re=re.compile(r"Seat\s+(?P<seat>\d+)\:\s+(?P<name>[\w\s]{3,12})\s+\((?P<stack>\d+)\)")
_hero_re=re.compile(r"Dealt\s+to\s+(?P<hero_name>[\w\s\-]{3,12})\s+\[(?P<card1>[AJKQ2-9shdc]{2})\s(?P<card2>[AJKQ2-9shdc]{2})\]")
_ante_re=re.compile(r"(?P<player_name>[\w\s\-]{3,12})\s+posts\sante\s+(?P<amount>\d+)")
_pot_re=re.compile(r"Total\s+pot\s+(?P<total_pot>\d+)")
_board_re=re.compile(r"Board\:\s+\[(?P<board>[AJKQ2-9shdc\s]+)\]")
_action_re=re.compile(r"(?P<player_name>[\w\s\-]{6,12})\s+(?P<move>shows|checks|calls|folds|bets|raises)\s+(?P<value>\d+||\s+)")
_winner_re=re.compile(r"(?P<player_name>[\w\s\-]{6,12})\s+collected\s+(?P<amount>\d+)\s+")
_showdown_action_re=re.compile(r"(?P<player_name>[\w\s\-]{6,12})\s+(?P<move>shows|mucks)\s+\[(?P<card1>[AJKQ2-9shdc]{2})\s+(?P<card2>[AJKQ2-9shdc]{2})\]")
_flop_re=re.compile(r"\*\*\*\s+FLOP\s+\*\*\*\s+\[(?P<flop_card1>[AJKQ2-9shdc]{2})\s+(?P<flop_card2>[AJKQ2-9shdc]{2})\s+(?P<flop_card3>[AJKQ2-9shdc]{2})\]")
_turn_re=re.compile(r"\*\*\*\s+TURN\s+\*\*\*\s+\[.+\]\[(?P<turn_card>[AJKQ2-9shdc]{2})\]")
_river_re=re.compile(r"\*\*\*\s+RIVER\s+\*\*\*\s+\[.+\]\[(?P<river_card>[AJKQ2-9shdc]{2})\]")
_showdown_re=re.compile(r"\*\*\*\s+SHOW\s+DOWN\s+\*\*\*\s+")
_summary_re=re.compile(r"\*\*\*\s+SUMMARY\s+\*\*\*\s+")
_sb_re=re.compile(r"(?P<player_name>[\w\s\_]{3,12})\s+posts\s+small\s+blind\s+(?P<sb>\d+)")


result=_winner_re.search(text)
print (result)
if result:
    print(result.groups())
else:
    print("expression non trouvée")

#buyIn=result.group('buyIn')
#print(float(buyIn)/2)
#tournament_name=result.group('tournament_name')
#print(tournament_name)

#HandHistory=WinamaxHandHistory(text)


