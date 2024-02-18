# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 1 b) Sofa-produksjon til møbelfabrikk - Størst overskudd 
# - Løser oppgaven med CAS i Python
# - Kopier kommandoene i terminalen og importer pakkene 
#   $ pip install numpy
#   $ pip install sympy
#   $ pip install matematikk

from matematikk import reggis, superløs, diff, Symbol

# Variabler
x            = Symbol("x")       # Produksjons-mengden x
x_max       = float()           # Produksjonsmengden som gir størst overskudd
K            = Symbol("K")       # Polynomets navn (vs)
grad         = 2                 # Polynomets grad
poly         = Symbol("poly")    # Polynomet (vs og hs)
x_liste      = [                 # Liste med x-verdier
    10,
    25,
    40,
    70,
    100,
    140,
    180]
y_liste      = [                 # Liste med y-verdier
    270,
    550,
    870,
    1500,
    2200,
    3300,
    4500]
O            = Symbol("O")       # Overskudds-funksjonen
dO           = Symbol("dO")      # Den deriverte av overskudds-funksjonen
rund         = 2                 # -1: Ingen avrunding, 0: Eks: 123.0, n > 0: n siffer etter desimaltegnet, None: Heltall
_blokk       = 1                 # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker

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

    # Løser likningen dO = 0 
    x_max = superløs(variabel = x,
                     vs       = dO,
                     hs       = 0,
                     rund     = None,
                     debug    = -1)

    # Svar-setninger
    svar_b_liste = list()
    svar_b_liste.append(f"")
    svar_b_liste.append(f"Oppg b)")
    svar_b_liste.append(f"")
    svar_b_liste.append(f"- Negativ a-koeffisient gir et toppunkt på O")
    svar_b_liste.append(f"- Produksjonsmengden x = {x_max} gir størst overskudd")

    # Print svar-setninger
    for svar in svar_b_liste: print(svar)
