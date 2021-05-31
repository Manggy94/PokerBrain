from API.hand import *
import numpy as np
import random
all_combos=[]
all_hands=list(Hand)
combos=list(hand.to_combos() for hand in list(Hand))
for i in range(0,len(combos)):
    for j in range(0,len(combos[i])):
        all_combos.append(combos[i][j])
nb_combos=len(all_combos)

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

range4=[]
for i in all_combos:
    range4.append(i)

ranges=[]
ranges.append(random_range(10))
ranges.append(random_range(1))
ranges.append(random_range(1326))
ranges.append(range4)


tab=[]
for i in range(0,len(ranges)):
    tab.append(ranges[i][0])

print (len(ranges))
print(tab)

for c in tab:
    print(c)
    for r in ranges:
        print(len(r))
        print(erreur(r,c))


