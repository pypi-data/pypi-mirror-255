# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 1 c) Sofa-produksjon til møbelfabrikk - Minst salgspris 

from numpy import polyfit
from sympy import Eq, diff, Reals, solveset, Symbol

# Variabler
x              = Symbol("x")           # Produksjons-mengden x
x_max         = float()               # Produksjonsmengden som gir størst overskudd
x_liste        = [                     # Liste med x-verdier
    10,
    25,
    40,
    70,
    100,
    140,
    180]
y_liste        = [                     # Liste med y-verdier
    270,
    550,
    870,
    1500,
    2200,
    3300,
    4500]
K              = Symbol("K")           # Kostnads-funksjonen
grad           = 2                     # Polynomets grad
O              = Symbol("O")           # Overskudds-funksjonen
dO             = Symbol("dO")          # Den deriverte av overskudds-funksjonen
pris_ny        = Symbol("pris_ny")     # Ny salgspris
I              = Symbol("I")           # Inntekts-funksjonen
rund           = 2                     # -1: Ingen avrunding, 0: Eks: 123.0, n > 0: n siffer etter desimaltegnet, None: Heltall
_blokk         = 1                     # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker

# Definerer funksjoner
def reggis(variabel = Symbol(""),
           grad     = int(),
           x_liste  = list(),
           y_liste  = list(),
           rund     = -1):

    # - Lager polynom-funksjon av valgfri grad vha. regresjon (CAS)

    # Variabler
    _koeff_liste       = list()                # Liste med koeffesienter i fra polyfit()
    _koeff             = float()               # Polynomets koeffisienter
    _ledd              = Symbol("_ledd")       # Polynomets ledd
    _ledd_grad         = int()                 # Polynomets ledd inkludert grad
    _uttrykk           = Symbol("_uttrykk")    # Polynomets uttrykk (hs)

    # polyfit() returnerer en liste med regresjons-koeffesientene
    _koeff_liste = polyfit(x_liste, y_liste, grad)

    # Hver iterasjon lager det neste leddet i polynomet
    for i in range(len(_koeff_liste)):

        # - På 1. iterasjon må _uttrykk nulles ut slik at det ikke blir en
        #   egen variabel i uttrykket, f.eks. "_uttrykk + 0.04*x**2 + 17.05*x + 102.7"
        if i == 0: _uttrykk = 0

        # Runder av koeffesienten
        if rund == -1: _koeff = _koeff_liste[i]
        if rund != -1: _koeff = round(_koeff_liste[i], rund)

        # Lager leddene i fra størst til minst grad
        _ledd_grad = grad - i

        # Formaterer leddene
        if _ledd_grad >= 2: _ledd = _koeff * variabel**_ledd_grad
        if _ledd_grad == 1: _ledd = _koeff * variabel
        if _ledd_grad == 0: _ledd = _koeff

        # Legger det nye leddet til polynomet
        _uttrykk += _ledd

    return _uttrykk

# a) Finn O(x)
if _blokk == 1:

    # Lager polynom-funksjon av valgfri grad vha. regresjon (CAS)
    K = reggis(variabel = x,
                  grad     = grad,
                  x_liste  = x_liste,
                  y_liste  = y_liste,
                  rund     = rund)

    # Svar-setninger
    svar_a_liste = list()
    svar_a_liste.append(f"")
    svar_a_liste.append(f"Oppg a)")
    svar_a_liste.append(f"")
    svar_a_liste.append(f"- Med regresjon fra numpy (polyfit) ser vi at hvis bedriften")
    svar_a_liste.append(f"  produserer x enheter, så vil")
    svar_a_liste.append(f"")
    svar_a_liste.append(f"    {K}")
    svar_a_liste.append(f"")
    svar_a_liste.append(f"  være en god model for det måntlige overskuffet (i tusen kroner)")

    # Print svar-setninger
    for svar in svar_a_liste: print(svar)

# b) Størst overskudd
if _blokk == 1:

    # Definerer uttrykket for overskudds-funksjonen, O
    O = -0.041*x**2 + 11*x - 103

    # Deriverer O mhp. x og får dO = 11 - 0.082*x
    dO = diff(O, x) # O'(x)

    # Lager likningen dO = 0 med Eq(vs, hs) 
    likning = Eq(dO, 0)

    # Løser likningen for x med solveset() og får løsnings-settet {134.146341463415}
    x_topp_set = solveset(likning, x, domain=Reals) # Løsnings-domene i ℝ (Reals)

    # Henter elementet i fra løsnings-settet, 134.146341463415
    x_max = x_topp_set.args[0]

    # Runder av 134.146341463415 -> 134
    x_max = round(x_max, None)

    # Svar-setninger
    svar_b_liste = list()
    svar_b_liste.append(f"")
    svar_b_liste.append(f"Oppg b)")
    svar_b_liste.append(f"")
    svar_b_liste.append(f"- Negativ a-koeffisient gir et toppunkt på O")
    svar_b_liste.append(f"- Produksjonsmengden x = {x_max} gir størst overskudd")

    # Print svar-setninger
    for svar in svar_b_liste: print(svar)

# c) Minst salgspris
if _blokk == 1:

    # Definerer uttrykkene for kostnads- og inntekts-funksjonen, K og I
    K = 0.041*x**2 + 17*x + 103
    I = pris_ny*x

    # Definerer uttrykket for overskudds-funksjonen, O = pris_ny*x - 0.041*x**2 - 17*x - 103
    O = I - K # Neg. a-koeff (-0.041) -> 'sur graf' -> Toppunkt

    # Deriverer O mhp. x og får dO = pris_ny - 0.082*x - 17
    dO = diff(O, x)

    # Lager likningen dO = 0 med Eq(vs, hs) 
    likning = Eq(dO, 0)

    # Løser likningen for x med solveset() og får løsnings-settet Intersection({12.19*pris_ny - 207.31}, Reals)
    x_topp_set = solveset(likning, x, domain=Reals)

    # Henter elementet i fra løsnings-settet, 12.195*pris_ny - 207.317
    x_max = x_topp_set.args[1].args[0] # x_topp = 12.2*pris_ny - 207 gir topp-punktet på O 

    # Setter x_max = 12.195*pris_ny - 207.317 inn i O og definerer det nye uttrykket som O_topp 
    O_topp = O.subs(x, x_max)

    # Lager likningen O_topp = 1000 med Eq(vs, hs) 
    likning = Eq(O_topp, 1000) # kr 1 000 000 "i antall tusen kr" er 1000

    # Løser likningen for pris_ny med solveset() og får løsnings-settet (3.55039034023664, 30.4496096597634)
    pris_ny_set = solveset(likning, pris_ny, domain=Reals)

    # Henter elementene i fra løsnings-settet, 3.5503, 30.4496
    pris_ny_1 = round(pris_ny_set.args[0], 3) # Runder av 3.5503 -> 3.55
    pris_ny_2 = round(pris_ny_set.args[1], 3) # Runder av 30.4496 -> 30.45

    # Setter pris_ny = 3.55 inn i x_max og definerer det nye uttrykket som x_topp_1 
    x_topp_1 = x_max.subs(pris_ny, pris_ny_1) # x_topp_1 = -164.02
    x_topp_1 = round(x_topp_1, None) # Runder av -164.02 -> -164

    # Setter pris_ny = 30.45 inn i x_max og definerer det nye uttrykket som x_topp_2 
    x_topp_2 = x_max.subs(pris_ny, pris_ny_2) # x_topp_2 = 164.02
    x_topp_2 = round(x_topp_2, None) # Runder av 164.02 -> 164

    # Ganger med 1000 for å få salgsprisen i kr (og ikke i "antall 1000 kr")
    pris_ny_1_kr = pris_ny_1 * 1000
    pris_ny_2_kr = pris_ny_2 * 1000

    # Svar-setninger
    svar_c_liste = list()
    svar_c_liste.append(f"")
    svar_c_liste.append(f"Oppg c)")
    svar_c_liste.append(f"")
    svar_c_liste.append(f"- En salgspris på kr {pris_ny_1_kr} gir x = {x_topp_1} produserte sofaer")
    svar_c_liste.append(f"- En salgspris på kr {pris_ny_2_kr} gir x = {x_topp_2} produserte sofaer")
    svar_c_liste.append(f"")
    svar_c_liste.append(f"- Vi kan ikke kan ha et negativt antall produserte sofaer")
    svar_c_liste.append(f"")
    svar_c_liste.append(f"- I denne oppgaven blir derfor riktig salgspris kr {pris_ny_2_kr} per sofa")

    # Print svar-setninger
    for svar in svar_c_liste: print(svar)
