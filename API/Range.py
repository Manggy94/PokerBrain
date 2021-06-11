from API.hand import *
import numpy as np
import random
# from API.timer import Timer

all_combos = np.array([], dtype=np.str)
all_hands=np.array(list(Hand), dtype=np.object)

for hand in all_hands:
    all_combos=np.hstack((all_combos,hand.to_combos()))

def random_range(m):
    combos=all_combos
    n=random.randint(1,m)
    print(n)
    card_range=[]
    for i in range(0,n):
        combo=random.choice(combos)
        combos.remove(combo)
        card_range.append(combo)
    return(card_range)

def erreur(range,combo):
    err_in=1-(combo in range)
    n=len(range)
    precision=(1326-n)/1325
    err_prec=1-precision
    err=(err_in+err_prec)**2
    return (err_in, err_prec, err)

