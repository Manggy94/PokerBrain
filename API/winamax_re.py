import re

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