# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 1 a) Sofa-produksjon til møbelfabrikk - Finn O(x)
# - Løser oppgaven med CAS i Python
# - Lager polynom-funksjon av valgfri grad vha. regresjon (CAS)
# - Kopier kommandoen i terminalen og importer matematikk (CAS)
#   $ pip install matematikk

from matematikk import reggis, Symbol
  
# Variabler
x                  = Symbol("x")       # Polynomets variabel
K                  = Symbol("K")       # Polynomets navn (vs)
grad               = 2                 # Polynomets grad
x_liste            = [                 # Liste med x-verdier
    10,
    25,
    40,
    70,
    100,
    140,
    180]
y_liste            = [                 # Liste med y-verdier
    270,
    550,
    870,
    1500,
    2200,
    3300,
    4500]
rund               = 2                 # -1: Ingen avrunding, 0: Eks: 123.0, n > 0: n siffer etter desimaltegnet, None: Heltall
_blokk             = 1                 # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker

# a) Finn O(x)
if _blokk == 1:

    # Lager polynom-funksjon av valgfri grad vha. regresjon (string)
    # - Lager polynom-funksjon av valgfri grad vha. regresjon (CAS)
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
