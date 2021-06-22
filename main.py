import API.Table
import file_reader as reader
import numpy as np

hands = reader.parse_file("historyexample2.txt")
#print(hands)

for hand in hands:
    keys=[]
    items=[]

    for key, item in vars(hand).items():
        if type(item) in [str, int, float]:
            keys.append(key)
            items.append(item)
        elif type(item)==API.Table.Level:
            level = item
            for key, item in vars(level).items():
                keys.append(key)
                items.append(item)
        elif type(item) == API.Table.Table:
            print(vars(item))
            table=item
            keys.append("advancement")
            items.append(table.progression)
            for key, item in vars(table).items():
                if key == "ident":
                    keys.append("table_ident")
                    items.append(item)

                elif key == "max_players":
                    keys.append(key)
                    items.append(item)
                elif key == "board":
                    for i in range(5):
                        keys.append("card%s" % str(i+1))
                        try:
                            items.append(str(item[i]))
                        except:
                            items.append("")
                elif key == "players":
                    players = item
                    for i in range(len(players)):
                        keys.append("p%s_name" % i)
                        keys.append("p%s_seat" %i)
                        keys.append("p%s_position" % i)
                        keys.append("p%s_stack" % i)
                        keys.append("p%s_is_hero" % i)
                        keys.append("p%s_combo" % i)
                        try:
                            player = players[i]
                            # print(player.name, player.hero, player.has_combo(), player.combo)
                            items.append(player.name)
                            items.append(player.seat)
                            items.append(player.position)
                            items.append(player.init_stack)
                            items.append(player.hero)
                            items.append(player.combo)
                        except:
                            items.extend(["",0,"",0])
                elif key in ["progression", "pot", "highest_bet"]:
                    pass
                elif type(item)==API.Table.Street:
                    street = item
                    # print("street:", street.name)
                    for i in range (len(street.actions)):
                        action=street.actions[i]
                        if type(action)==API.Table.Action:
                            keys.append("%s_action_%s_seat"%(street.name, i))
                            items.append(action.player.seat)
                            keys.append("%s_action_%s_move" % (street.name, i))
                            items.append(action.move)
                            keys.append("%s_action_%s_amount" % (street.name, i))
                            items.append(action.value)

                else:
                    print(key, item)
            #keys.append(key)
            #items.append(item)
    #key=item
    print(len(keys), keys)
    print(items)
#print(vars(hand))

poker_type=hand.poker_type
#print(poker_type)


