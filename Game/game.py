from tkinter import *
from tkinter.messagebox import *
from API.Table import *


class App(Frame):
    def __init__(self, window=Tk()):
        super().__init__(window)
        self.window = window
        self.pack()
        self.homepage()
        self.bg_col = "#ffcaaf"
        self.fg_col = "#04ab9f"
        self.window.title("Poker Brain")
        self.window.geometry("720x480")
        self.window.minsize(480, 360)
        self.window.iconbitmap("logo.ico")
        self.window.config(background=self.bg_col)
        self.table = None
        self.level = None
        self.current_player = None

    def homepage(self):
        # Create frame
        # Add text
        self.bg_col = "#ffcaaf"
        self.fg_col = "#04ab9f"
        self.frame = Frame(self.window, bg=self.bg_col)
        self.home_title = Label(self.frame, text="Bienvenue sur PokerBrain", font=("Courrier", 40), bg=self.bg_col, fg=self.fg_col)
        self.home_title.pack()
        # Add text
        self.label_subtitle = Label(self.frame, text="Le cerveau du Poker", font=("Courrier", 24), bg=self.bg_col, fg=self.fg_col)
        self.label_subtitle.pack()
        self.frame.pack(expand="YES")
        # Add a button for new table
        self.table_btn = Button(self.frame, text="Nouvelle Table", font=("Courrier", 24), command=self.input_table)
        self.table_btn.pack(fill=X, pady=20)

    def input_table(self):
        # showinfo("New Table Info", "Ouverture d'une nouvelle table")
        self.frame.pack_forget()
        self.home_title.pack_forget()
        self.frame = Frame(self.window, bg=self.bg_col)
        self.ask_label = Label(
            self.frame,
            text="Quel est le nombre max de joueurs à la table?",
            font=("Courrier", 24),
            bg=self.bg_col,
            fg="#04ab9f")
        self.ask_label.pack(expand="YES")
        self.ask_max_players = Spinbox(self.frame, from_=3, to=10, font=("Courrier", 24))
        self.ask_max_players.pack(fill=X)
        self.max_btn = Button(self.frame, text="OK", font=("Courrier", 24), command=self.get_max)
        self.max_btn.pack()
        self.frame.pack(expand="YES")
        self.max_players = 0

    def get_max(self):
        self.max_players = self.ask_max_players.get()
        # showinfo("Max players", "Max players = %s"%(self.max_players))
        self.frame.pack_forget()
        self.new_table()

    def new_table(self):
        self.frame.pack_forget()
        self.frame = Frame(self.window, bg=self.bg_col)
        self.frame.pack(expand="YES")
        self.table = Table(0, max_players=self.max_players)
        self.add_players_frame()
        self.table.villains = 0

    def add_players_frame(self):
        self.frame.pack_forget()
        self.frame = Frame(self.window, bg=self.bg_col)
        self.frame.pack(expand="YES")
        self.players_frame = Frame(self.frame, bd=2, bg=self.bg_col, padx=5, pady=5)
        self.players_frame.pack(side=LEFT)
        self.new_hand_frame = Frame(self.frame, bd=2, bg=self.bg_col, padx=5, pady=5)
        self.new_hand_frame.pack(side=RIGHT)
        self.add_player_btn = Button(
            self.players_frame,
            text="Add Player",
            font=("Courrier", 24),
            command=self.add_player,
        )
        self.add_hero_btn = Button(
            self.players_frame,
            text="Add Hero",
            font=("Courrier", 24),
            command=self.add_hero,
        )
        self.add_player_btn.pack(pady=5, expand="YES", fill=X)
        self.add_hero_btn.pack(pady=5, expand="YES", fill=X)
        self.players = []

        self.new_hand_btn = Button(
            self.new_hand_frame,
            text = "New Hand",
            font=("Courrier", 24),
            command=self.new_hand
        )

        self.set_level_btn = Button(
            self.new_hand_frame,
            text="Set Level",
            font=("Courrier", 24),
            command=self.level_entry
        )
        self.new_hand_btn.pack(pady=5, expand="YES", fill=X)
        self.set_level_btn.pack(pady=5, expand="YES", fill=X)

    def add_player(self):
        if len(self.table.players)< int(self.table.max_players):
            self.table.villains+=1
            player = Player(name="Villain %s"%self.table.villains, seat=len(self.table.players)+1, stack=20000)
            self.table.add_player(player)
            # showinfo("New player", player.name)
            player_label = Label(
                self.players_frame,
                text="Seat n°%s: %s"%(player.seat, player.name),
                font=("Courrier", 24),
                bg=self.bg_col,
                fg=self.fg_col)
            player_label.pack(expand="YES", fill=X)
        else:
            showinfo("Too many players", "Il y a déjà trop de joueurs à cette table")
        # print(self.table.players)

    def add_hero(self):
        if len(self.table.players) < int(self.table.max_players) and self.table.hero == None:
            player = Player(name="Manggy94", seat=len(self.table.players) + 1, stack=20000)
            self.table.add_player(player)
            self.table.hero = player
            self.add_hero_btn.pack_forget()
            # showinfo("New Hero", player.name)
            player_label = Label(
                self.players_frame,
                text="Seat n°%s: %s"%(player.seat, player.name),
                font=("Courrier", 24),
                bg=self.bg_col,
                fg=self.fg_col)
            player_label.pack(expand="YES", fill=X)
        else:
            showinfo("Too many players", "Il y a déjà trop de joueurs à cette table")
       #  print(self.table.players)

    def new_hand(self):
        self.frame.pack_forget()
        self.frame = Frame(self.window, bg=self.bg_col)
        self.frame.pack(expand="YES")
        self.hand = HandHistory()
        if self.level == None:
            # print("boucle de création de level")
            self.level_entry()
        else:
            #print("boucle d'affectation de Level au level existant")
            self.hand.level = self.level
            self.count_stacks = 0
            hand = self.hand
            hand.started = False
            hand.table = self.table
            Label(
                self.frame,
                text="Seat",
                borderwidth=2,
                bg=self.bg_col,
                fg="#000",
                font=("Courrier", 24)
            ).grid(row=0, column=0)
            Label(
                self.frame,
                text=" Player Name" ,
                borderwidth=2,
                bg=self.bg_col,
                fg="#000",
                font=("Courrier", 24)
            ).grid(row=0, column=1)
            Label(
                self.frame,
                text="Stack",
                borderwidth=2,
                bg=self.bg_col,
                fg="#000",
                font=("Courrier", 24)
            ).grid(row=0, column=2)
            if self.count_stacks < len(hand.table.players):
                self.change_stack()
            else:
                Button(master=self.frame, text="Next step", command=self.stacks_to_hand).grid()

    def change_stack(self):
        hand = self.hand
        if self.count_stacks < len(self.hand.table.players):
            player = hand.table.players[self.count_stacks]
            Label(
                self.frame,
                text=" %s" %player.seat,
                borderwidth=2,
                bg=self.bg_col,
                fg=self.fg_col,
                font=("Courrier",24)
            ).grid(row=self.count_stacks+1, column=0)
            Label(
                self.frame,
                text=" %s" % player.name,
                borderwidth=2,
                bg=self.bg_col,
                fg=self.fg_col,
                font=("Courrier", 24)
            ).grid(row=self.count_stacks+1, column=1)

            self.player_stack_label = Label(
                self.frame,
                text=" %s" % player.stack,
                borderwidth=2,
                bg=self.bg_col,
                fg=self.fg_col,
                font=("Courrier", 24)
            )
            self.player_stack_label.grid(row=self.count_stacks+1, column=2)
            self.new_stack = Entry(
                self.frame,
                borderwidth=2,
                bg=self.bg_col,
                fg=self.fg_col,
                font=("Courrier", 24)
            )
            self.new_stack.grid(row=self.count_stacks+1, column=3)
        self.stack_btn = Button(master=self.window, text="Next player", command=self.stacks_to_hand)
        self.stack_btn.pack()

    def stacks_to_hand(self):
        self.stack_btn.pack_forget()
        self.new_stack.grid_remove()
        # print(self.count_stacks, len(self.hand.table.players))
        if self.count_stacks < len(self.hand.table.players):
            player = self.hand.table.players[self.count_stacks]
            new_stack = self.new_stack.get()
            if new_stack=='':
                pass
            else:
                new_stack = float(new_stack)
                print(player.stack)
                player.stack = new_stack
            # print(player.name, player.stack)
            self.player_stack_label = Label(
                self.frame,
                text=" %s" % player.stack,
                borderwidth=2,
                bg=self.bg_col,
                fg=self.fg_col,
                font=("Courrier", 24)
            )
            self.player_stack_label.grid(row=self.count_stacks + 1, column=2)
            self.count_stacks += 1
            self.change_stack()
        else:
            self.stack_btn = Button(master=self.frame, text="Choose BB position", command=self.input_bb)
            self.stack_btn.grid()
        # print(self.count_stacks)

    def start_hand(self):
        hand = self.hand
        table = hand.table
        for player in table.players:
            table.post_ante(player, hand.level.ante)
            if player.position == Position("SB"):
                table.bet(player, hand.level.sb)
            elif player.position == Position("BB"):
                 table.bet(player, hand.level.bb)
            #print(player.name, player.stack, table.pot)
        first_player, i = self.find_starting_player()
        self.current_player, index = self.find_starting_player()
        pl = self.current_player
        pl.set_to_call(table)
        pl.set_pot_odds(table)

        self.action_entry()
        self.players_display()


    def choose_bb(self):
        table = self.hand.table
        for player in table.players:
            player.position = None
        bb_position = int(self.ask_bb.get())
        table.players[bb_position-1].position = Position("BB")
        # print(table.players)
        table.distribute_positions()
        # for player in table.players:
        #    print(player.name, player.position)
        self.start_hand()

    def input_bb(self):
        self.stack_btn.grid_forget()
        self.ask_bb = Spinbox(master=self.frame, from_=1, to=len(self.hand.table.players), font=("Courrier", 24))
        self.ask_bb.grid(column=1, columnspan=1)
        self.bb_btn = Button(master=self.frame, text="Start Hand", command=self.choose_bb)
        self.bb_btn.grid(column=1)

        # print(hand.table, self.hand.table)
        # print(self.hand)

    def level_entry(self):
        self.frame.pack_forget()
        self.frame = Frame(self.window, bg=self.bg_col)
        self.frame.pack()
        self.level_frame = Frame(self.frame, bg=self.bg_col)
        self.level_nb_label = Label(
            self.level_frame,
            text="Level Number",
            font=("Courrier", 24),
            bg=self.bg_col,
            fg=self.fg_col
        )
        self.level_nb_entry = Spinbox(
            self.level_frame,
            font=("Courrier", 24),
            from_=1,
            to=100)
        self.level_ante_label = Label(self.level_frame, text="Level Ante", font=("Courrier", 24), bg="#ffcaaf", fg="#04ab9f")
        self.level_ante_entry = Entry(self.level_frame, text="ante", font=("Courrier", 24))
        self.level_bb_label = Label(
            self.level_frame,
            text="Big Blind",
            font=("Courrier", 24),
            bg=self.bg_col,
            fg=self.fg_col
        )
        self.level_button = Button(self.level_frame, text="Next", font=("Courrier", 24), command=self.set_level)
        self.level_bb_entry = Entry(self.level_frame, font=("Courrier", 24))
        self.level_frame.pack(expand="YES", fill=X)
        self.level_nb_label.pack(expand="YES", fill=X)
        self.level_nb_entry.pack(expand="YES", fill=X)
        self.level_ante_label.pack(expand="YES", fill=X)
        self.level_ante_entry.pack(expand="YES", pady=5, fill=X)
        self.level_bb_label.pack()
        self.level_bb_entry.pack()
        self.level_button.pack()

    def set_level(self):
        nb = int(self.level_nb_entry.get())
        ante = float('0'+self.level_ante_entry.get())
        bb = float('0'+self.level_bb_entry.get())
        sb = bb/2
        self.level = Level(number=nb, ante=ante, sb=sb, bb=bb)
        self.new_hand()

    def find_starting_player(self):
        """
        Choisit un joueur par rapport à la situation de la partie
        :return:
        """
        table = self.hand.table
        street = table.streets[table.progression]
        table.find_active_players(street)
        players = street.active_players
        if table.progression < 1:
            ref_position = Position("BB")
        else:
            ref_position = Position("BTN")
        for i in range(len(players)):
            player = players[i]
            if player.position == ref_position:
                ref_seat = player.seat
                i_ref = i
        first_player, first_i = self.find_next_player(i_ref)
        return first_player, first_i

    def find_next_player(self, i):
        table = self.hand.table
        street = table.streets[table.progression]
        i += 1
        if i == len(street.active_players):
            i = 0
        player = street.active_players[i]
        while (player.ingame == False or player.folded):
            i += 1
            player = street.active_players[i]
        return player, i

    def next_action(self):
        pass

    def action_entry(self):
        self.frame.pack_forget()
        self.frame = Frame(self.window, bg=self.bg_col)
        self.frame.pack(expand="YES")
        hand = self.hand
        table = hand.table
        players = table.streets[table.progression].active_players
        for i in range(len(players)):
            player = players[i]
            player.set_to_call(table)
            player.set_pot_odds(table)
            print(player.name, player.to_call, player.pot_odds, player.req_equity)
        print(self.current_player.name)

    def players_display(self):
        hand = self.hand
        table = hand.table
        bb = self.level.bb
        for player in table.streets[table.progression].active_players:
            player.set_to_call(table)
            player.set_pot_odds(table)
            print(player.name, player.stack/table.bb, player.to_call, round(player.pot_odds,2), round(player.req_equity,3))
        print(self.current_player.name)

    def evaluate_range(self, player):
        pass


Game = App()
Game.mainloop()
