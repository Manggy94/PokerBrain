import re

split_re = re.compile(r"\*\*\*\s+\n?|\n\n+")
winamax_new_hand_re = re.compile(r"Winamax\s+Poker")
date_re = re.compile(r"-\s+(?P<date>.+)")
pk_type = re.compile(r"(?P<poker_type>Tournament|CashGame)")
tournament_name_re = re.compile(r"\"(?P<tournament_name>.+)\"\s+")
buyin_txt_re = re.compile(r"buyIn:\s+(?P<buyin>[\d.,]+)â..\s+")
freeroll_re = re.compile(r"buyIn:\s+(?P<buyin>Free)\s+")
level_re = re.compile(r"level:\s+(?P<level>[\d#]+)\s+")
hand_id_re = re.compile(r"-\s+HandId:\s+#(?P<hand_id>[\d-]+)\s+-\s+(?P<Variant>[A-Za-z ]+)\s+")
blinds_re = re.compile(r"\((?P<ante>\d+)/(?P<sb>\d+)/(?P<bb>\d+)\)\s+|\((?P<sblind>\d+)/(?P<bblind>\d+)\)")
CG_blinds_re = re.compile(r"\((?P<sb>[\d.,]+)â../(?P<bb>[\d.,]+)â..\)")
table_re = re.compile(
    r"Table:\s+'(?P<tournament_name>.+)\((?P<tournament_id>\d+)\)#(?P<table_id>\d+)'\s+(?P<max_seat>\d+)-max\s+\("
    r"(?P<money_type>[a-z]+)\s+money\)\s+Seat\s+#(?P<button>\d)\s+is\s+the\s+button")
CG_table_re = re.compile(
    r"Table:\s+'(?P<CG_name>.+)\s+(?P<table_id>\d+)'"
    r"\s+(?P<max_seat>\d+)-max\s+\((?P<money_type>[a-z]+)\s+money\)\s+Seat\s+#(?P<button>\d)\s+is\s+the\s+button")
seat_re = re.compile(r"Seat\s+(?P<seat>\d+):\s+(?P<pl_name>[\w\s\-&.]{3,12})\s\((?P<stack>\d+)\)")
CG_seat_re = re.compile(r"Seat\s+(?P<seat>\d+):\s+(?P<pl_name>[\w\s\-&.]{3,12})\s\((?P<stack>[\d.,]+)â..\)")
pot_re = re.compile(r"Total\s+pot\s+(?P<total_pot>\d+)")
ante_re = re.compile(r"(?P<pl_name>[\w\s\-&.]{3,12})\s+posts\sante\s+(?P<amount>[\d.,]+)")
board_re = re.compile(r"Board:\s+\[(?P<board>[\w ]+)]")
action_re = re.compile(r"(?P<pl_name>[\w\s\-&.]{6,12})\s+(?P<move>calls|bets|raises)\s+(?P<value>\d+|\s+)")
action_2_re = re.compile(r"(?P<pl_name>[\w\s\-&.]{6,12})\s+(?P<move>folds|checks)")
sd_action_re = re.compile(
    r"(?P<pl_name>[\w\s\-&.]{6,12})\s+(?P<move>shows|mucks)\s+\[(?P<c1>\w{2})\s+(?P<c2>\w{2})]")
flop_re = re.compile(r"\*\*\*\s+FLOP\s+\*\*\*\s+\[(?P<fc1>\w{2})\s+(?P<fc2>\w{2})\s+(?P<fc3>\w{2})]")
hero_re = re.compile(r"Dealt\s+to\s+(?P<hero_name>[\w\s\-&.]+)\s+\[(?P<c1>\w{2})\s+(?P<c2>\w{2})]")
turn_re = re.compile(r"\*\*\*\s+TURN\s+\*\*\*\s+\[.+]\[(?P<tc>\w{2})]")
river_re = re.compile(r"\*\*\*\s+RIVER\s+\*\*\*\s+\[.+]\[(?P<rc>\w{2})]")
showdown_re = re.compile(r"\*\*\*\s+SHOW\s+DOWN\s+\*\*\*")
summary_re = re.compile(r"\*\*\*\s+SUMMARY\s+\*\*\*")
winner_re = re.compile(r"(?P<pl_name>[\w\s\-&.]{6,12})\s+collected\s+(?P<amount>[\d.,]+)\s+")
CG_winner_re = re.compile(r"(?P<pl_name>[\w\s\-&.]{6,12})\s+collected\s+(?P<amount>[\d.,]+)")
sb_re = re.compile(r"(?P<pl_name>[\w\s\-&.]{3,12})\s+posts\s+small\s+blind\s+(?P<sb>[\d.,]+)")
bb_re = re.compile(r"(?P<pl_name>[\w\s\-&.]{3,12})\s+posts\s+big\s+blind\s+(?P<bb>[\d.,]+)")
tour_name_re = re.compile(
    r"Winamax\s+Poker\s+-\s+Tournament\s+summary\s+:\s+(?P<tournament_name>.+)\((?P<tournament_id>\d+)\)")
total_players_re = re.compile(r"Registered\s+players\s+:\s+(?P<total_players>\d+)")
prizepool_re = re.compile(r"Prizepool\s+:\s+(?P<prizepool>[\d.]+)")
game_mode_re = re.compile(r"Mode\s+.+\s+:\s+(?P<game_mode>.+)")
ttype_re = re.compile(r"Type\s+:\s+(?P<game_mode>.+)")
speed_re = re.compile(r"Speed\s+:\s+(?P<speed>.+)")
buyin_re = re.compile(r"Buy-In\s+:\s+(?P<buyin>[\d.]+)")
levels_re = re.compile(r"Levels\s+:\s+\[(?P<levels>.+)]")
KO_seat_re = re.compile(
    r"Seat\s+(?P<seat>\d+):\s+(?P<pl_name>[\w\s\-&.]{3,12})\s+\((?P<stack>\d+),\s+(?P<bounty>[\d.,]+)")
