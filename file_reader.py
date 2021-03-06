from API.card import Card
from API.Table import Action, Combo, HandHistory, Level, Player, PositionError, Table, Tournament
import API.constants as cst
import numpy as np
import pandas as pd
import os
import re
# route="C:\\Users\hp\Desktop\Poker\PokerBrain\history


class ParsingError(Exception):
    pass


class CashGameError(Exception):
    pass


class EmptyTableError(Exception):
    pass


class HeaderError(Exception):
    pass


class FileReader:
    """
    Class that can read a handhistory .txt file
    """
    def __init__(self):
        """
        New Poker File Reader
        """
        self.root = f"{os.getcwd()}"
        self._split_re = re.compile(r"\*\*\*\s+\n?|\n\n+")
        self._winamax_new_hand_re = re.compile(r"Winamax\s+Poker")
        self._date_re = re.compile(r"-\s+(?P<date>.+)")
        self._pk_type = re.compile(r"(?P<poker_type>Tournament|CashGame)")
        self._tournament_name_re = re.compile(r"\"(?P<tournament_name>.+)\"\s+")
        self._buyin_txt_re = re.compile(r"buyIn:\s+(?P<buyin>[0-9.,]+)â..\s+")
        self._freeroll_re = re.compile(r"buyIn:\s+(?P<buyin>Free)\s+")
        self._level_re = re.compile(r"level:\s+(?P<level>[\d#]+)\s+")
        self._hand_id_re = re.compile(r"-\s+HandId:\s+#(?P<hand_id>[0-9-]+)\s+-\s+(?P<Variant>[A-Za-z ]+)\s+")
        self._blinds_re = re.compile(r"\((?P<ante>\d+)/(?P<sb>\d+)/(?P<bb>\d+)\)\s+|\((?P<sblind>\d+)/(?P<bblind>\d+)\)")
        self._CG_blinds_re = re.compile(r"\((?P<sb>[\d.,]+)â../(?P<bb>[\d.,]+)â..\)")
        self._table_re = re.compile(r"Table:\s+'(?P<tournament_name>.+)\((?P<tournament_id>\d+)\)#(?P<table_id>\d+)'\s+(?P<max_seat>\d+)-max\s+\((?P<money_type>[a-z]+)\s+money\)\s+Seat\s+#(?P<button>\d)\s+is\s+the\s+button")
        self._CG_table_re = re.compile(r"Table:\s+'(?P<CG_name>.+)\s+(?P<table_id>\d+)'\s+(?P<max_seat>\d+)-max\s+\((?P<money_type>[a-z]+)\s+money\)\s+Seat\s+#(?P<button>\d)\s+is\s+the\s+button")
        self._seat_re = re.compile(r"Seat\s+(?P<seat>\d+):\s+(?P<pl_name>[\w\s\-&.]{3,12})\s\((?P<stack>\d+)\)")
        self._KO_seat_re = re.compile(r"Seat\s+(?P<seat>\d+):\s+(?P<pl_name>[\w\s\-&.]{3,12})\s+\((?P<stack>\d+),\s+(?P<bounty>[\d.,]+)")
        self._CG_seat_re = re.compile(r"Seat\s+(?P<seat>\d+):\s+(?P<pl_name>[\w\s\-&.]{3,12})\s\((?P<stack>[\d.,]+)â..\)")
        self._pot_re = re.compile(r"Total\s+pot\s+(?P<total_pot>\d+)")
        self._ante_re = re.compile(r"(?P<pl_name>[\w\s\-&.]{3,12})\s+posts\sante\s+(?P<amount>[\d.,]+)")
        self._board_re = re.compile(r"Board:\s+\[(?P<board>[\w ]+)]")
        self._action_re = re.compile(r"(?P<pl_name>[\w\s\-&.]{6,12})\s+(?P<move>calls|bets|raises)\s+(?P<value>\d+|\s+)")
        self._action_2_re = re.compile(r"(?P<pl_name>[\w\s\-&.]{6,12})\s+(?P<move>folds|checks)")
        self._sd_action_re = re.compile(r"(?P<pl_name>[\w\s\-&.]{6,12})\s+(?P<move>shows|mucks)\s+\[(?P<c1>\w{2})\s+(?P<c2>\w{2})]")
        self._flop_re = re.compile(r"\*\*\*\s+FLOP\s+\*\*\*\s+\[(?P<fc1>\w{2})\s+(?P<fc2>\w{2})\s+(?P<fc3>\w{2})]")
        self._hero_re = re.compile(r"Dealt\s+to\s+(?P<hero_name>[\w\s\-&.]+)\s+\[(?P<c1>\w{2})\s+(?P<c2>\w{2})]")
        self._turn_re = re.compile(r"\*\*\*\s+TURN\s+\*\*\*\s+\[.+]\[(?P<tc>\w{2})]")
        self._river_re = re.compile(r"\*\*\*\s+RIVER\s+\*\*\*\s+\[.+]\[(?P<rc>\w{2})]")
        self._showdown_re = re.compile(r"\*\*\*\s+SHOW\s+DOWN\s+\*\*\*")
        self._summary_re = re.compile(r"\*\*\*\s+SUMMARY\s+\*\*\*")
        self._winner_re = re.compile(r"(?P<pl_name>[\w\s\-&.]{6,12})\s+collected\s+(?P<amount>[\d.,]+)\s+")
        self._CG_winner_re = re.compile(r"(?P<pl_name>[\w\s\-&.]{6,12})\s+collected\s+(?P<amount>[\d.,]+)")
        self._sb_re = re.compile(r"(?P<pl_name>[\w\s\-&.]{3,12})\s+posts\s+small\s+blind\s+(?P<sb>[\d.,]+)")
        self._bb_re = re.compile(r"(?P<pl_name>[\w\s\-&.]{3,12})\s+posts\s+big\s+blind\s+(?P<bb>[\d.,]+)")
        self._tour_name_re = re.compile(r"Winamax\s+Poker\s+-\s+Tournament\s+summary\s+:\s+(?P<tournament_name>.+)\((?P<tournament_id>\d+)\)")
        self._total_players_re = re.compile(r"Registered\s+players\s+:\s+(?P<total_players>\d+)")
        self._prizepool_re = re.compile(r"Prizepool\s+:\s+(?P<prizepool>[\d.]+)")
        self._game_mode_re = re.compile(r"Mode\s+.+\s+:\s+(?P<game_mode>.+)")
        self._ttype_re = re.compile(r"Type\s+:\s+(?P<game_mode>.+)")
        self._speed_re = re.compile(r"Speed\s+:\s+(?P<speed>.+)")
        self._buyin_re = re.compile(r"Buy-In\s+:\s+(?P<buyin>[\d.]+)")
        self._levels_re = re.compile(r"Levels\s+:\s+\[(?P<levels>.+)]")

    def split_raw_file(self, hh_text: str) -> np.ndarray:
        """
        Splits a raw history file into an array of raw hands
        :param hh_text: raw text for entire tournament/session
        :return: array of different hands played
        """
        raw_hands = re.split(self._winamax_new_hand_re, hh_text)
        raw_hands.pop(0)
        return np.array(raw_hands)

    @staticmethod
    def split_raw_hand(raw_hand: str) -> np.ndarray:
        """
        Splits a raw hand into an array of lines
        :param raw_hand: raw text for a poker hand
        :return: array of text lines
        """
        return np.array(raw_hand.splitlines())

    @staticmethod
    def floatify(txt_num: str) -> float:
        """
        Transforms any written str number into a float
        :param txt_num: number to transform
        :return: float number
        """
        try:
            return float(txt_num.replace(",", "."))
        except TypeError:
            return float(0)
        except AttributeError:
            return float(0)


class FileParser(FileReader):
    """
    This class can understand a handhistory.txt file and parse its information to create HandHistory objects
    """
    def __init__(self):
        """
        New poker file Parser
        """
        FileReader.__init__(self)

    def parse_pk_type(self, text: str):
        """
        Reads poker type regex and parses it
        :param text: hand text line
        :return: poker type as string
        """
        r = re.search(pattern=self._pk_type, string=text)
        if r:
            poker_type = r.group("poker_type")
            return poker_type.strip()
        else:
            raise HeaderError("Poker Type Problem")

    def parse_tournament_name(self, text: str):
        """
        Reads tournament name regex and parses it
        :param text: hand text line
        :return: tournament name
        """
        r = re.search(pattern=self._tournament_name_re, string=text)
        if r:
            tournament_name = r.group("tournament_name")
        else:
            tournament_name = "Cash Game"
        return tournament_name.strip()

    def parse_buyin(self, text: str) -> float:
        """
        Reads buy-in regex and parses it
        :param text: hand text line
        :return: tournament's buyin as float
        """
        try:
            buyin = self.floatify(re.search(pattern=self._buyin_txt_re, string=text).group("buyin"))
            return buyin
        except AttributeError:
            print("Buyin Problem")
            print(text)

    def parse_freeroll_buyin(self, text: str) -> float:
        """
        Reads freeroll buy-in regex and parses it
        :param text: hand text line
        :return: tournament's buyin as float
        """
        freeroll_buyin = re.search(pattern=self._freeroll_re, string=text).group("buyin")
        return float(0)

    def parse_entry(self, text: str) -> float:
        """
        Reads entry cost (freeroll or normal tournament) and parses it
        :param text: hand text line
        :return: tournament's buyin as float
        """
        if re.search(pattern=self._buyin_txt_re, string=text):
            return self.parse_buyin(text)
        elif re.search(pattern=self._freeroll_re, string=text):
            return self.parse_freeroll_buyin(text)

    def parse_level(self, text: str) -> int:
        """
        Reads level regex and parses it
        :param text: hand text line
        :return: level as int
        """
        r = re.search(pattern=self._level_re, string=text)
        if r:
            level = int(r.group("level"))
        else:
            level = 0
        return level

    def parse_hand_id(self, text: str) -> str:
        """
        Reads hand_id regex and parses it
        :param text: hand text line
        :return: hand_id as a string
        """
        if text == " ":
            return "None"
        else:
            r = re.search(pattern=self._hand_id_re, string=text)
        if r:
            hand_id = r.group("hand_id")
            return hand_id.strip()

    def parse_blinds(self, text: str):
        """
        Reads blinds regex and parses its info into a dict
        :param text: hand text line
        :return: blinds informations as a dict
        """
        s = re.search(pattern=self._blinds_re, string=text)
        r = re.search(pattern=self._CG_blinds_re, string=text)
        if s:
            ante, sb, bb = s.group("ante"), s.group("sb") or s.group("sblind"), s.group("bb") or s.group("bblind")
            return {"ante": self.floatify(ante), "sb": self.floatify(sb), "bb": self.floatify(bb)}
        elif r:
            ante, sb, bb = 0.0, r.group("sb"), r.group("bb")
            return {"ante": ante, "sb": self.floatify(sb), "bb": self.floatify(bb)}

    def parse_date(self, text: str):
        """
        Reads date regex and parses it as a string
        :param text: hand text line
        :return: Date as a string
        """
        date = re.search(pattern=self._date_re, string=text).group("date")
        return date

    def parse_table(self, text: str):
        """
        Reads table info regex and parses its info into a dict
        :param text: hand text line
        :return: table info as a divt
        """
        s = re.search(pattern=self._table_re, string=text)
        r = re.search(pattern=self._CG_table_re, string=text)
        if s:
            tour_id = s.group("tournament_id")
            table_id = s.group("table_id")
            max_seat = int(s.group("max_seat"))
            money_type = s.group("money_type").strip()
            btn = int(s.group("button"))
        elif r:
            tour_id = r.group("CG_name")
            table_id = r.group("table_id")
            max_seat = int(r.group("max_seat"))
            money_type = r.group("money_type").strip()
            btn = int(r.group("button"))
        else:
            raise ParsingError
        return {"tour_id": tour_id.strip(), "table_id": table_id.strip(), "max_seat": max_seat,
                "money_type": money_type, "btn": btn}

    def parse_seat(self, text: str):
        """
        Reads seat info regex and parses its info into a dict
        :param text: hand text line
        :return: seat info as a dict
        """
        bounty=0
        s = re.search(pattern=self._seat_re, string=text)
        r = re.search(pattern=self._CG_seat_re, string=text)
        ko = re.search(pattern=self._KO_seat_re, string=text)
        if s:
            seat, pl_name, stack = int(s.group("seat")), s.group("pl_name").strip(), self.floatify(s.group("stack"))
        elif ko:
            seat = int(ko.group("seat"))
            pl_name = ko.group("pl_name").strip()
            stack = self.floatify(ko.group("stack"))
            bounty = self.floatify(ko.group("bounty"))
        else:
            seat, pl_name, stack = int(r.group("seat")), r.group("pl_name").strip(), self.floatify(r.group("stack"))
        return {"seat": seat, "pl_name": pl_name, "stack": stack, "bounty": bounty}

    def parse_pot(self, text: str) -> float:
        """
        Reads pot regex and parses it as a float
        :param text: hand text line
        :return: pot as a float
        """
        pot = re.search(pattern=self._pot_re, string=text).group("total_pot")
        return self.floatify(pot)

    def parse_ante(self, text: str):
        """
        Reads ante regex and parses its info into a dict
        :param text: hand text line
        :return:ante info as a dict
        """
        s = re.search(pattern=self._ante_re, string=text)
        if s:
            pl_name, amount = s.group("pl_name").strip(), self.floatify(s.group("amount"))
            return {"pl_name": pl_name, "amount": amount}

    def parse_action(self, text: str):
        """
        Reads action regex and parses its info into a dict
        :param text: hand text line
        :return: action info as a dict
        """
        if re.search(pattern=self._action_re, string=text):
            s = re.search(pattern=self._action_re, string=text)
            pl_name, move, value = s.group("pl_name").strip(), s.group("move").strip(), self.floatify(s.group("value"))
        else:
            s = re.search(pattern=self._action_2_re, string=text)
            pl_name, move, value = s.group("pl_name").strip(), s.group("move").strip(), 0.0
        return {"pl_name": pl_name, "move": cst.Action(move), "value": value}

    def parse_sd_action(self, text: str):
        """
        Reads Showdown action regex and parses its info into a dict
        :param text: hand text line
        :return: Showdown action info as a dict
        """
        s = re.search(pattern=self._sd_action_re, string=text)
        pl_name, move = s.group("pl_name").strip(), s.group("move").strip()
        c1, c2 = Card(s.group("c1")), Card(s.group("c2"))
        return {"pl_name": pl_name, "move": move, "c1": c1, "c2": c2}

    def parse_hero(self, text: str):
        """
        Reads hero regex and parses its info into a dict
        :param text: hand text line
        :return: hero info as a dict
        """
        s = re.search(pattern=self._hero_re, string=text)
        name, c1, c2 = s.group("hero_name").strip(), Card(s.group("c1")), Card(s.group("c2"))
        return {"name": name, "c1": c1, "c2": c2}

    def parse_flop(self, text: str):
        """
        Reads flop regex and parses its cards
        :param text: hand text line
        :return: flop cards as a dict
        """
        s = re.search(pattern=self._flop_re, string=text)
        c1, c2, c3 = Card(s.group("fc1")), Card(s.group("fc2")), Card(s.group("fc3"))
        return {"c1": c1, "c2": c2, "c3": c3}

    def parse_turn(self, text: str):
        """
        Reads turn regex and parses its card
        :param text: hand text line
        :return: turn card
        """
        tc = re.search(pattern=self._turn_re, string=text).group("tc")
        return Card(tc)

    def parse_river(self, text: str):
        """
        Reads river regex and parses its card
        :param text: hand text line
        :return: river card
        """
        rc = re.search(pattern=self._river_re, string=text).group("rc")
        return Card(rc)

    def parse_sb(self, text: str):
        """
        Reads small blind posting regex and parses its info into a dict
        :param text: hand text line
        :return: small blind info as a dict
        """
        s = re.search(pattern=self._sb_re, string=text)
        pl_name, sb = s.group("pl_name").strip(), self.floatify(s.group("sb"))
        return {"pl_name": pl_name, "sb": sb}

    def parse_bb(self, text: str):
        """
        Reads big blind posting regex and parses its info into a dict
        :param text: hand text line
        :return: big blind info as a dict
        """
        s = re.search(pattern=self._bb_re, string=text)
        pl_name, bb = s.group("pl_name").strip(), self.floatify(s.group("bb"))
        return {"pl_name": pl_name, "bb": bb}

    def parse_winner(self, text: str):
        """
        Reads winner regex and parses its info into a dict
        :param text: hand text line
        :return: winner(s) info as a dict
        """
        s = re.search(pattern=self._winner_re, string=text)
        r = re.search(pattern=self._CG_winner_re, string=text)
        if s:
            pl_name, amount = s.group("pl_name").strip(), self.floatify(s.group("amount"))
        else:
            pl_name, amount = r.group("pl_name").strip(), self.floatify(r.group("amount"))
        return {"pl_name": pl_name, "amount": amount}

    def parse_header(self, header_txt: str):
        """
        Reads header lines different regex) (tournament info, hand_id, blinds etc... and parses it
        :param header_txt: hand text line
        :return: header info as a dict (on hand and table)
        """
        pk_type = self.parse_pk_type(header_txt)
        if pk_type == "Tournament":
            tour_name = self.parse_tournament_name(header_txt)
            buyin = self.parse_entry(header_txt)
            lvl = self.parse_level(header_txt)
            hand_id = self.parse_hand_id(header_txt)
            blinds = self.parse_blinds(header_txt)
            try:
                ante = blinds["ante"]
                bb = blinds["bb"]
            except TypeError:
                raise HeaderError
        else:
            raise CashGameError
            tour_name = "CashGame"
            buyin = 0
            lvl = None
            hand_id = self.parse_hand_id(header_txt)
            blinds = self.parse_blinds(header_txt)
            ante = blinds["ante"]
            bb = blinds["bb"]
        return {"pk_type": pk_type, "tour_name": tour_name, "buyin": buyin, "lvl": lvl, "hand_id": hand_id,
                "ante": ante, "bb": bb}

    @staticmethod
    def create_tournament(header_info: dict, table_info: dict) -> Tournament:
        """
        Creates a new tournament from parsed info
        :param header_info: header_info as a dict
        :param table_info: tournament info as a dict
        :return: Tournament object
        """
        tournament = Tournament()
        tournament.id = table_info["tour_id"]
        tournament.money_type = table_info["money_type"]
        tournament.name = header_info["tour_name"]
        tournament.buyin = header_info["buyin"]
        return tournament

    @staticmethod
    def create_level(header_info: dict) -> Level:
        """
        Creates a new level from parsed info
        :param header_info: header info as a dict
        :return: Level object
        """
        level = Level()
        level.bb = header_info["bb"]
        level.ante = header_info["ante"]
        level.level = header_info["lvl"]
        return level

    @staticmethod
    def create_table(table_info: dict) -> Table:
        """
        Creates a new table from parsed info
        :param table_info: table info as a dict
        :return: Table object
        """
        table = Table(ident=table_info["table_id"], max_players=table_info["max_seat"])
        return table

    def create_player(self, seat_txt: str) -> Player:
        """
        Reads player Seat regex and parses its info to create a new player.
        :param seat_txt: hand text line
        :return: Player object
        """
        seat_info = self.parse_seat(seat_txt)
        player = Player(name=seat_info["pl_name"], seat=seat_info["seat"], stack=seat_info["stack"])
        player.bounty = seat_info["bounty"]
        return player

    def parse_pregame_info(self, text: np.ndarray, hh: HandHistory) -> HandHistory:
        """
        Reads pregame regex and parses its info into HandHistory object
        :param text: hand text line
        :param hh: HandHistory object for the hand at stake
        :return: modified HandHistory object for the hand at stake
        """
        try:
            header_info = self.parse_header(text[0])
        except IndexError:
            raise ParsingError("Text header is too short")
        hh.hand_id = header_info["hand_id"]
        table_info = self.parse_table(text[1])
        tournament = self.create_tournament(header_info=header_info, table_info=table_info)
        hh.tournament = tournament
        level = self.create_level(header_info=header_info)
        hh.level = level
        table = self.create_table(table_info=table_info)
        hh.table = table
        hh.button = table_info["btn"]
        return hh

    def parse_post_ante(self, text_line: str, hh: HandHistory):
        """
        Reads ante posting regex and parses its info into HandHistory object
        :param text_line: hand text line
        :param hh: HandHistory object for the hand at stake
        :return:
        """
        ante_info = self.parse_ante(text_line)
        pl_name, ante = ante_info["pl_name"], ante_info["amount"]
        player = hh.table.players[pl_name]
        hh.table.bet(player=player, amount=ante)
        #except KeyError:
        #    if len(hh.table.players.pl_list) == 0:
         #       raise EmptyTableError


    def parse_post_sb(self, text_line: str, hh: HandHistory):
        """
        Reads small blind posting regex and parses its info into HandHistory object
        :param text_line: hand text line
        :param hh: HandHistory object for the hand at stake
        :return:
        """
        pl_name, sb = self.parse_sb(text_line)["pl_name"], self.parse_sb(text_line)["sb"]
        try:
            player = hh.table.players[pl_name]
            hh.table.bet(player=player, amount=sb)
        except KeyError:
            raise ParsingError

    def parse_post_bb(self, text_line: str, hh: HandHistory):
        """
        Reads big blind posting regex and parses its info into HandHistory object
        :param text_line: hand text line
        :param hh: HandHistory object for the hand at stake
        :return:
        """
        pl_name, bb = self.parse_bb(text_line)["pl_name"], self.parse_bb(text_line)["bb"]
        try:
            player = hh.table.players[pl_name]
            player.position = cst.Position("BB")
            hh.table.bet(player=player, amount=bb)
            hh.table.players.positions[f"{player.position}"] = player.seat
            hh.table.distribute_positions()
        except KeyError:
            # print(hh.table.players)
            raise ParsingError

    def parse_hero_combo(self, text_line: str, hh: HandHistory):
        """
        Reads hero's combo regex and parses its info into HandHistory object
        :param text_line: hand text line
        :param hh: HandHistory object for the hand at stake
        :return:
        """
        hero_info = self.parse_hero(text_line)
        name, c1, c2 = hero_info["name"], hero_info["c1"], hero_info["c2"]
        hh.table.draw_card(f"{c1}")
        hh.table.draw_card(f"{c2}")
        combo = Combo(f"{c1}{c2}")
        try:
            player = hh.table.players[name]
            player.is_hero = True
            player.combo = combo
            hh.table.hero = player
        except KeyError:
            raise ParsingError

    def parse_new_action(self, text_line: str, hh: HandHistory):
        """
        Reads action regex and parses its info into HandHistory object
        :param text_line: hand text line
        :param hh: HandHistory object for the hand at stake
        :return:
        """
        action_info = self.parse_action(text_line)
        pl_name, move, value = action_info["pl_name"], action_info["move"], action_info["value"]
        try:
            player = hh.table.players[pl_name]
            action = Action(player=player, move=move, value=value)
            hh.table.add_action(street=hh.table.current_street, action=action)
        except KeyError:
            raise ParsingError

    def parse_new_sd_action(self, text_line: str, hh: HandHistory):
        """
        Reads showdown action regex and parses its info into HandHistory object
        :param text_line: hand text line
        :param hh: HandHistory object for the hand at stake
        :return:
        """
        sd_info = self.parse_sd_action(text_line)
        if not hh.table.has_showdown:
            hh.table.make_showdown()
            hh.table.current_street = hh.table.streets[hh.table.progression]
        pl_name, move, c1, c2 = sd_info["pl_name"], sd_info["move"], sd_info["c1"], sd_info["c2"]
        player = hh.table.players[pl_name]
        combo = Combo(f"{c1}{c2}")
        player.shows(combo)

    def parse_new_flop(self, text_line: str, hh: HandHistory):
        """
        Reads flop regex and parses its info into HandHistory object
        :param text_line: hand text line
        :param hh: HandHistory object for the hand at stake
        :return:
        """
        flop_info = self.parse_flop(text_line)
        hh.table.make_flop()
        hh.table.current_street = hh.table.streets[1]
        fc1, fc2, fc3 = flop_info["c1"], flop_info["c2"], flop_info["c3"]
        hh.table.draw_flop(fc1, fc2, fc3)

    def parse_new_turn(self, text_line: str, hh: HandHistory):
        """
        Reads turn regex and parses its info into HandHistory object
        :param text_line: hand text line
        :param hh: HandHistory object for the hand at stake
        :return:
        """
        hh.table.make_turn()
        tc = self.parse_turn(text_line)
        hh.table.current_street = hh.table.streets[2]
        hh.table.draw_turn(tc)

    def parse_new_river(self, text_line: str, hh: HandHistory):
        """
        Reads river regex and parses its info into HandHistory object
        :param text_line: hand text line
        :param hh: HandHistory object for the hand at stake
        :return:
        """
        hh.table.make_river()
        rc = self.parse_river(text_line)
        hh.table.current_street = hh.table.streets[3]
        hh.table.draw_river(rc)

    def parse_table_winner(self, text_line: str, hh: HandHistory):
        """
        Reads table winner regex and parses its info into HandHistory object
        :param text_line: hand text line
        :param hh: HandHistory object for the hand at stake
        :return:
        """
        winner_info = self.parse_winner(text_line)
        pl_name, amount = winner_info["pl_name"], winner_info["amount"]
        player = hh.table.players[pl_name]
        hh.table.win(player=player, amount=amount)

    def parse_hand(self, text: np.ndarray):
        """
        Reads a whole hand splitted text and transforms it into a HandHistory object
        :param text: ndarray of splitted lines for this hand
        :return: HandHistory object for the hand at stake
        """
        try:
            hh = HandHistory()
            hh = self.parse_pregame_info(text=text, hh=hh)
            i = 2
            length = text.shape[0]
            while i < length:
                if re.search(self._seat_re, text[i]) or re.search(self._KO_seat_re, text[i]) or re.search(self._CG_seat_re, text[i]):
                    player = self.create_player(text[i])
                    hh.table.players.append(player)
                elif re.search(self._ante_re, text[i]):
                    self.parse_post_ante(text_line=text[i], hh=hh)
                elif re.search(self._sb_re, text[i]):
                    self.parse_post_sb(text_line=text[i], hh=hh)
                elif re.search(self._bb_re, text[i]):
                    self.parse_post_bb(text_line=text[i], hh=hh)
                elif re.search(self._hero_re, text[i]):
                    self.parse_hero_combo(text_line=text[i], hh=hh)
                    hh.table.find_active_players(hh.table.streets[0])
                elif re.search(self._flop_re, text[i]):
                    self.parse_new_flop(text_line=text[i], hh=hh)
                elif re.search(self._turn_re, text[i]):
                    self.parse_new_turn(text_line=text[i], hh=hh)
                elif re.search(self._river_re, text[i]):
                    self.parse_new_river(text_line=text[i], hh=hh)
                elif re.search(self._sd_action_re, text[i]):
                    self.parse_new_sd_action(text_line=text[i], hh=hh)
                elif re.search(self._action_re, text[i]) or re.search(self._action_2_re, text[i]):
                    self.parse_new_action(text_line=text[i], hh=hh)
                elif re.search(self._winner_re, text[i]):
                    self.parse_table_winner(text_line=text[i], hh=hh)
                i += 1
            return hh
        #except EmptyTableError as e:
            #print(text)
            #raise EmptyTableError (e)
        #except ParsingError as e:
         #   print(e)
          #  print(text)
          #  exit()
        except CashGameError:
            return None
        except HeaderError:
            return None

    def parse_file(self, file_name: str, dir_name: str = "history"):
        """
        Takes a Winamax txt file  and parses its hands
        :param file_name: Name of the file in folder
        :param dir_name: Name of the folder containing txt files
        :return: HandHistories ndarray
        """
        # File opening
        file = open(f"{self.root}/{dir_name}/{file_name}", "r")
        try:
            hand_txt = file.read()
            file.close()
            hands_array = self.split_raw_file(hand_txt)
            splitted_hands = np.array([self.split_raw_hand(hand) for hand in hands_array], dtype=object)
            hands = np.hstack([self.parse_hand(hand) for hand in splitted_hands])
            return hands
        except UnicodeError:
            file.close()

    def parse_tour_folder(self, dir_name: str = "history"):
        """
        Parses summary files of a directory into a dataframe
        :param dir_name: name of the file in folder
        :return: DataFrame of tournament info
        """
        summaries = self.get_holdem_summary_files(dir_name=dir_name)
        columns = np.array(["name", "tournament_id", "prizepool", "nb_players", "mode", "speed", "buyin"])
        data = np.vstack([(self.parse_summary(file)) for file in summaries])
        df = pd.DataFrame(columns=columns, data=data)
        return df

    def parse_summary(self, file_name: str) -> np.ndarray:
        """
        Reads a summary file and parses it
        :param file_name: name of the file in folder
        :return:
        """
        file = open("history/%s" % file_name, "r")
        content = file.read()
        match1 = re.search(self._tour_name_re, content)
        match2 = re.search(self._total_players_re, content)
        match3 = re.search(self._ttype_re, content)
        match4 = re.search(self._prizepool_re, content)
        match5 = re.search(self._speed_re, content)
        match6 = re.search(self._buyin_re, content)
        # match7 = re.search(self._levels_re, content)
        tour_name, tour_id = match1.group("tournament_name"), int(match1.group("tournament_id"))
        tot_players = int(match2.group("total_players"))
        game_mode = match3.group("game_mode")
        prizepool = self.floatify(match4.group("prizepool"))
        speed = match5.group("speed")
        buyin = self.floatify(match6.group("buyin"))
        # levels_string = (match7.group("levels"))
        # levels = re.split(":holdem-no-limit,", levels_string)
        # level = re.split("[\-:]", levels[0])
        return np.array([tour_name, tour_id, prizepool, tot_players, game_mode, speed, buyin])

    def parse_directory(self, dir_name: str = "history", ignore_previous: bool = False):
        """
        Parses files of a directory into a list of hand_histories
        :param dir_name: directory name in the project as a string
        :param ignore_previous: Indicates if we have to take into account previous files parsing
        :return: HandHistory list
        """
        files = self.get_holdem_game_files(dir_name)
        collection = np.hstack([self.parse_file(file_name=file_name, dir_name=dir_name) for file_name in files[:100]])
        return collection

    def parse_finished_hands(self, dir_name: str = "history"):
        """
        Parses files of a directory to find hands that went to ShowDown
        :param dir_name: directory name in the project as a string
        :return: HandHistory list
        """
        finished_hands = np.array([hand for hand in self.parse_directory(dir_name) if hand.table.has_showdown()])
        return finished_hands

    def get_holdem_game_files(self, dir_name: str = "history"):
        """
        Crawls a folder and returns the name of tournament game files as an array
        :param dir_name: directory name in the project as a sring
        :return: names of tournament game files as an array
        """
        return np.array([x for x in os.listdir(f"{self.root}/{dir_name}") if "summary" not in x and "holdem" in x and
                         "real" in x and "Sit" not in x])

    def get_holdem_summary_files(self, dir_name: str = "history") -> np.ndarray:
        """
        Crawls a folder and returns the name of tournament summary files as an array
        :param dir_name: directory name in the project as a sring
        :return: names of tournament summary files as an array
        """
        return np.array([x for x in os.listdir(f"{self.root}/{dir_name}") if "summary" in x and "holdem" in x and
                         "real" in x and "Sit" not in x])
