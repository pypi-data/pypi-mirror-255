# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 1 a) Sofa-produksjon til møbelfabrikk - Finn O(x) 
# - Lager polynom-funksjon av valgfri grad vha. regresjon (string)
# - Importer reggis() fra matematikk for å regne med polynomet i CAS
# - Kopier kommandoene i terminalen og importer pakkene (CAS)
#   $ pip install numpy
#   $ pip install matematikk

from numpy import polyfit

# Variabler
variabel           = "x"           # Polynomets variabel
navn               = "K"           # Polynomets navn (vs)
grad               = 2             # Polynomets grad
poly               = str()         # Polynomet (vs og hs)
x_liste            = [             # Liste med x-verdier
    10,
    25,
    40,
    70,
    100,
    140,
    180]
y_liste            = [             # Liste med y-verdier
    270,
    550,
    870,
    1500,
    2200,
    3300,
    4500]
rund               = 5             # -1: Ingen avrunding, 0: Eks: 123.0, n > 0: n siffer etter desimaltegnet, None: Heltall
_blokk             = 1             # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker

# Definerer funksjoner
def reggis_str(variabel = str(),
               navn     = str(),
               grad     = int(),
               x_liste  = list(),
               y_liste  = list(),
               rund     = -1):

    # - Lager polynom-funksjon av valgfri grad vha. regresjon (string)

    # Variabler
    _koeff_liste   = list()    # Liste med koeffesienter i fra polyfit()
    _koeff         = str()     # Polynomets koeffisienter
    _ledd          = str()     # Polynomets ledd
    _ledd_grad     = str()     # Polynomets ledd inkludert grad
    _uttrykk       = str()     # Polynomets uttrykk (hs)
    _poly          = str()     # Polynomet (vs og hs)

    # polyfit() returnerer en liste med regresjons-koeffesientene
    _koeff_liste = polyfit(x_liste, y_liste, grad)

    # Hver iterasjon lager det neste leddet i polynomet
    for i in range(len(_koeff_liste)):

        # Runder av koeffesienten
        if rund == -1: _koeff = _koeff_liste[i]
        if rund != -1: _koeff = round(_koeff_liste[i], rund)

        # Type caster numpy_float64 -> str
        _koeff = str(_koeff)

        # Lager leddene i fra størst til minst grad
        _ledd_grad = grad - i

        # Formaterer leddene
        if _ledd_grad >= 2: _ledd = _koeff + f"{variabel}^{str(_ledd_grad)} + "
        if _ledd_grad == 1: _ledd = _koeff + f"{variabel} + "
        if _ledd_grad == 0: _ledd = _koeff

        # Legger det nye leddet til polynomet
        _uttrykk += _ledd

    _poly = navn + f"({variabel}) = " + _uttrykk

    return _poly

# a) Finn O(x)
if _blokk == 1:

    # Lager polynom-funksjon av valgfri grad vha. regresjon (string)
    poly = reggis_str(variabel = variabel,
                      navn     = navn,
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
    svar_a_liste.append(f"    {poly}")
    svar_a_liste.append(f"")
    svar_a_liste.append(f"  være en god model for det måntlige overskuffet (i tusen kroner)")

    # Print svar-setninger
    for svar in svar_a_liste: print(svar)
