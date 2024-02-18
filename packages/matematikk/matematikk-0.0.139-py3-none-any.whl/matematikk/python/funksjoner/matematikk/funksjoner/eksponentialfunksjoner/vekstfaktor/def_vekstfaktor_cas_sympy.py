# 🚀 programmering.no | 🤓 matematikk.as
# vekstfaktor_cas() regner ut vekstfaktoren for CAS (Matematikk AS)
# Andre navn: vekst_faktor_cas()

from sympy import Symbol

def vekstfaktor_cas(fortegn = str(), p = Symbol("")):
    
    # Vekstfaktor er definert som V = 1 ± p / 100, p: prosentvis vekst [%]
    v = Symbol("v")
    if fortegn == "+": v = 1 + p / 100 # "+": Øker
    if fortegn == "-": v = 1 - p / 100 # "-": Minker
    
    return v

v = vekstfaktor_cas(fortegn = "+", p = Symbol("p"))

print(v) # p/100 + 1
