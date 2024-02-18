# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 3 b) Sparekonto - Påstand: Dobbelt så lang tid 
# - Løser oppgaven med CAS i Python
# - Prosentvis vekst er en eksponentialfunksjon som kan skrives på formen
#   - f(x) = a * b^x, f(0) = a (startverdi), b > 0 (vekstfaktor)

from sympy import Eq, Reals, solveset, Symbol

# Konstanter og CAS-variabler (symbol)
B_P                = Symbol("B_P")     # Beløp etter n år (Per)
B_K                = Symbol("B_K")     # Beløp etter n år (Kåre)
B_30000            = 30000             # 30 000,- spart
I                  = Symbol("I")       # Innskuddet (startbeløpet inn på konto)
V_P                = Symbol("V_P")     # Vekstfaktor (Per)
V_K                = Symbol("V_K")     # Vekstfaktor (Kåre)
p_rente_p                = 3                 # Årlig rente i banken (Per)
p_rente_k                = 6                 # Årlig rente i banken (Per)
n                  = Symbol("n")       # Antall år med sparing
n_8                = 8                 # Periode på 8 år
n_dobbelt_p        = float()           # År med sparing (Per)
n_dobbelt_k        = float()           # År med sparing (Kåre)
n_forhold          = float()           # Forholdet n_dobbelt_p / n_dobbelt_k
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

# Definerer uttrykket for vekstfaktoren, v = 1 + p / 100
V_P = vekstfaktor(p_rente_p, "+")
V_K = vekstfaktor(p_rente_k, "+")

# a) Finn innskuddet til Per
if _blokk == 1:

    # Definerer uttrykket for B
    B = I * V_P**n # B = I * 1.03**n (en ukjente, I og n)

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

# b) Påstand: Dobbelt så lang tid
if _blokk == 1:

    # Definerer uttrykkene for B_P og B_K
    B_P = I * V_P**n
    B_K = I * V_K**n

    # Løser likningen 2 * 23682 = 23682 * 1.03**n for n
    n_dobbelt_p = los_sett(variabel = n,
                           vs       = 2 * I,
                           hs       = B_P,
                           rund     = 2)

    # Løser likningen 2 * 23682 = 23682 * 1.06**n for n
    n_dobbelt_k = los_sett(variabel = n,
                           vs       = 2 * I,
                           hs       = B_K,
                           rund     = 2)

    # Regner ut forholdet n = 23.45 / 11.90 = 1.97 
    n_forhold = n_dobbelt_p / n_dobbelt_k

    # Runder av svaret
    n_forhold = round(n_forhold, 2)

    # Svar-setninger
    svar_b_liste = list()
    svar_b_liste.append(f"")
    svar_b_liste.append(f"Oppg b)")
    svar_b_liste.append(f"")
    svar_b_liste.append(f"- Nei, det vil ikke gå nøyaktig dobbelt så lang tid, men ca.")
    svar_b_liste.append(f"  {n_dobbelt_p} år / {n_dobbelt_k} år = {n_forhold} ganger så lang tid")
    svar_b_liste.append(f"- Vi kan også vise at likningen ikke kan løses")
    svar_b_liste.append(f"     2 * B_P = 2 * B_K | 1 / 2")
    svar_b_liste.append(f"     B_P = B_K")
    svar_b_liste.append(f"     I * 1.03^(2n) = I * 1.06^n | 1 / I")
    svar_b_liste.append(f"     1.03^(2n) = 1.06^n")
    svar_b_liste.append(f"     (1.03^2)^n = 1.06^n, a^(nm) = (a^n)^m")
    svar_b_liste.append(f"     1.0609^n ≠ 1.06^n")
    svar_b_liste.append(f"")
    svar_b_liste.append(f"- Påstanden er derfor ikke riktig")
    # Print svar-setninger
    for svar in svar_b_liste: print(svar)
