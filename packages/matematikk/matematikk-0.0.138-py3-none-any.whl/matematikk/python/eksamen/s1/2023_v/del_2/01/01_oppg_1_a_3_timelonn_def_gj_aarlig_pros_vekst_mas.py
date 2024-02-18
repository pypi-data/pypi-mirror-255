# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Vår (Matematikk AS)
# Oppgave 2 b) Timelønnen til yrkesgruppe" - Eksponentialfunksjon (regresjon) 
# - Løser oppgaven med CAS i Python
# - Prosentvis vekst er en eksponentialfunksjon som kan skrives på formen
#   - f(x) = a * b^x, f(0) = a (startverdi), b > 0 (vekstfaktor)

from matematikk import Symbol, superløs, vekstfaktor_cas

# Konstanter og CAS-variabler (symbol)
G                  = Symbol("G")       # Timelønn x år etter 2008
G_0                = Symbol("G_0")     # Timelønnen i 2008
V                  = Symbol("V")       # Vekstfaktor
x                  = Symbol("x")       # Antall år med lønnsvekst
p                  = Symbol("p")       # Gjennomsnittlig årlige prosentvis vekst
_blokk             = 1                 # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker

# Tabell
x_liste            = [2008,   2010,   2013,   2015,   2019,   2022]   # Årstall
G_liste            = [272.55, 285.50, 307.30, 314.00, 327.60, 340.10] # Timelønn

def gjennomsnittlig_årlig_prosentvis_vekst(x_liste = list(), y_liste = list()):

    # Definerer uttrykket for vekstfaktoren, v = 1 + p / 100
    V = vekstfaktor_cas("+", Symbol("p"))

    # F_0 er startverdien i y_liste
    F_0 = y_liste[0]

    # Definerer uttrykket for årlig gjennomsnittlig vekst, f(x) = a * b^x
    F = F_0 * V**Symbol("x")

    # Regner ut antall år for perioden 2008–2022 
    x_periode = x_liste[-1] - x_liste[0]

    # Setter x = x_periode inn i G og definerer det nye uttrykket som G_periode 
    F_periode = F.subs(x, x_periode)

    # Regner ut p = 1.6 i V fra G_periode = 272.55 * V**14 
    p_periode = superløs(variabel = p,
                         vs       = F_periode,
                         hs       = y_liste[-1],
                         rund     = 1,
                         debug    = -1)[1]

    return p_periode

# a) Gjennomsnittlig årlige prosentvis vekst
if _blokk == 1:

    # Regner ut p = 1.6 i V fra G_periode = 272.55 * V**14 
    p_periode = gjennomsnittlig_årlig_prosentvis_vekst(x_liste, G_liste)

    svar_a_liste = list()
    svar_a_liste.append(f"")
    svar_a_liste.append(f"Oppg a)")
    svar_a_liste.append(f"")
    svar_a_liste.append(f"- I årene 2008-2022 var den gjennomsnittlige årlige")
    svar_a_liste.append(f"  prosentvise veksten ca. {p_periode} %")

    # Print svar-setninger
    for svar in svar_a_liste: print(svar)
