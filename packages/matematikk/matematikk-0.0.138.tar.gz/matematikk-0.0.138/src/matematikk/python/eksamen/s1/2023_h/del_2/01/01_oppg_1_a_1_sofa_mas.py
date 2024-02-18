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
koeff_liste        = list()        # Liste med koeffesienter i fra polyfit()
koeff              = float()       # Polynomets koeffisienter
ledd               = str()         # Polynomets ledd
ledd_grad          = int()         # Polynomets ledd inkludert grad
uttrykk            = str()         # Polynomets uttrykk (hs)
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
rund               = 2             # -1: Ingen avrunding, 0: Eks: 123.0, n > 0: n siffer etter desimaltegnet, None: Heltall
_blokk             = 1             # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker

# a) Finn O(x)
if _blokk == 1:

    # polyfit() returnerer en liste med regresjons-koeffesientene
    koeff_liste = polyfit(x_liste, y_liste, grad)

    # Hver iterasjon lager det neste leddet i polynomet
    for i in range(len(koeff_liste)):

        # Runder av koeffesienten
        if rund == -1: koeff = koeff_liste[i]
        if rund != -1: koeff = round(koeff_liste[i], rund)

        # Type caster float -> str
        koeff = str(koeff)

        # Lager leddene i fra størst til minst grad
        ledd_grad = grad - i

        # Formaterer leddene
        if ledd_grad >= 2: ledd = koeff + f"{variabel}^{str(ledd_grad)} + "
        if ledd_grad == 1: ledd = koeff + f"{variabel} + "
        if ledd_grad == 0: ledd = koeff

        # Legger det nye leddet til polynomet
        uttrykk += ledd

    poly = navn + f"({variabel}) = " + uttrykk

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
