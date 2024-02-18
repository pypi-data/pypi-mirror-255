# 🚀 programmering.no | 🤓 matematikk.as
# vekstfaktor() regner ut vekstfaktoren (Matematikk AS)
# Andre navn: vekst_faktor()

def vekstfaktor(fortegn = str(),
                p       = float(),
                rund    = -1):
    
    # Vekstfaktor er definert som V = 1 ± p / 100, p: prosentvis vekst [%]
    v = 0.0
    if fortegn == "+": v = 1 + p / 100 # "+": Øker
    if fortegn == "-": v = 1 - p / 100 # "-": Minker
    
    # Runder av svaret
    if rund != 1: v = round(v, rund)
    
    return v

v = vekstfaktor(fortegn = "+",
                p       = 3.1,
                rund    = 2)

print(v) # 1.03
