# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 3 a) Sparekonto - Finn innskuddet til Per 
# - Løser oppgaven med CAS i Python
# - Prosentvis vekst er en eksponentialfunksjon som kan skrives på formen
#   - f(x) = a * b^x, f(0) = a (startverdi), b > 0 (vekstfaktor)

from sympy import Eq, Reals, solveset, Symbol

# Konstanter og CAS-variabler (symbol)
B                  = Symbol("B")       # Beløp etter p år
B_30000            = 30000             # 30 000,- spart
I                  = Symbol("I")       # Innskuddet (startbeløpet inn på konto)
V                  = Symbol("V")       # Vekstfaktor
p_rente_3                = 3                 # Årlig rente i banken
n                  = Symbol("n")       # Antall år med sparing
n_8                = 8                 # Periode på 8 år
_blokk             = 1                 # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker

# Definerer funksjoner
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

def los_sett(variabel = Symbol(""),
             vs       = Symbol(""),
             hs       = Symbol(""),
             rund     = None):

    # Lager likningen med Eq(vs, hs) 
    likning = Eq(vs, hs)

    # Løser likningen for aktuell variabel med solveset() og får løsnings-settet på formen {1234.56789}
    losning_set = solveset(likning, variabel, domain = Reals) # Løsnings-domene i ℝ (Reals)

    # Henter elementet i fra løsnings-settet, f.eks. 1234.56789
    losning = losning_set.args[0] # [0] er første element (det eneste her)

    # Runder av f.eks. 1234.56789 -> 1234.6
    losning = round(losning, rund)

    return losning

# a) Finn innskuddet til Per
if _blokk == 1:

    # Definerer uttrykket for vekstfaktoren, v = 1 + p / 100
    V = vekstfaktor(p_rente_3, "+")

    # Definerer uttrykket for B
    B = I * V**n # B = I * 1.03**n (en ukjente, I og n)

    # Setter n = 8 inn i B og definerer det nye uttrykket som B_8 
    B_8 = B.subs(n, n_8) # B_8 = I * 1.03**8

    # Løser likningen 30000 = I * 1.03**8 for I
    I = los_sett(variabel = I,
                 vs       = B_30000,
                 hs       = B_8,
                 rund     = None) # I = 23682

    # Svar-setninger
    svar_a_liste = list()
    svar_a_liste.append(f"")
    svar_a_liste.append(f"Oppg a)")
    svar_a_liste.append(f"")
    svar_a_liste.append(f"- Dersom Per skal ha kr {B_30000} på kontoen sin etter {n_8} år,")
    svar_a_liste.append(f"  så må han ha et innskudd på ca. kr {I}")
    # Print svar-setninger
    for svar in svar_a_liste: print(svar)
