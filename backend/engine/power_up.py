from math import sqrt

def pair_impair(nb_o):
    if nb_o%2==0:
        return "pair"
    else:
        return "impair"

def nb_premier(nb_o):
    r = int(sqrt(nb_o))
    for x in range(2,nb_o):
        if nb_o%x==0:
            return "pas premier"
    return "premier"

def nb_narcissique(nb_o):
    nb_l = [int(e) for e in str(nb_o)]
    som = 0
    for i in nb_l:
        som +=i**len(nb_l)
    if som == nb_o:
        return "narcissique"
    else:
        return "pas narcissique"
    
def nb_parfait(nb_o):
    l_d = []
    for x in range(1,nb_o):
        if nb_o%x==0:
            l_d.append(x)
    if sum(l_d)==nb_o:
        return "parfait"
    else:
        return "pas parfait"