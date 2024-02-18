# 🚀 programmering.no | 🤓 matematikk.as
# Sinus 1T (2020) - BrettBoka - 1.5 Formler (s. 55) 
# Oppgave 9 Tittel (Matematikk AS)

from math import sqrt

# Blokk med definisjoner
_blokk             = 1 # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker
if _blokk == 1:

    # Konstanter
    katet_1_a          = 3             # Trekant A: Lengden til katet 1, f.eks. [m]
    katet_2_a          = 4             # Trekant A: Lengden til katet 2, [m]
    hypotenus_a        = 5             # Trekant A: Lengden til hypotenus, [m]
    katet_1_b          = 105           # Trekant B: Lengden til katet 1, [m]
    katet_2_b          = 208           # Trekant B: Lengden til katet 2, [m]
    hypotenus_b        = 233           # Trekant B: Lengden til hypotenus, [m]

    # Enheter
    enhet_m            = "m"           # Meter

    # Tekst
    txt_oppg           = "Oppg 9 - Kapitteltest 1"
    txt_strek          = "-----------------------"
    txt_a_1            = "a) Trekant A: Lengden til katet 1   :"
    txt_a_2            = "   Trekant A: Lengden til katet 2   :"
    txt_a_3            = "   Trekant A: Lengden til hypotenus :"
    txt_b_1            = "b) Trekant B: Lengden til katet 1   :"
    txt_b_2            = "   Trekant B: Lengden til katet 2   :"
    txt_b_3            = "   Trekant B: Lengden til hypotenus :"
    txt_info_1         = "   h^2 = k_1^2 + k_2^2, Pythagoras teorem"
    txt_info_2         = "a) h = √(k_1^2 + k_2^2)"
    txt_info_3         = "b) k_1^2 + k_2^2 = h^2"
    txt_info_4         = "   k_2^2 = h^2 - k_1^2"
    txt_info_5         = "   k_2 = √(h^2 - k_1^2)"
    txt_error          = "Kateter kan ikke være lengre enn hypotenus"
    txt_ikke_def       = "Ikke definert"

    # Innstillinger
    inp                = 1             # # 0: Boken, 1: Bruker
    avrund_valg        = 1             # # 0: Ikke avrunding, 1: Avrunding
    avrund_ant         = None          # # None: 12.78 -> 13, 0: 12.78 -> 13.0, 1: 12.78 -> 12.8, 2: 12.78 -> 12.78

# Input
print("")
print(txt_strek)
print(txt_oppg)
print(txt_strek)
if inp == 1:
    print("")
    katet_1_a = input("a) Trekant A: Hva er lengden til katet 1 [m]? ")
    katet_2_a = input("a) Trekant A: Hva er lengden til katet 2 [m]? ")
    katet_1_b = input("b) Trekant B: Hva er lengden til katet 1 [m]? ")
    hypotenus_b = input("b) Trekant B: Hva er lengden til hypotenus [m]? ")

# Type casting: str -> float
katet_1_a          = float(katet_1_a)
katet_2_a          = float(katet_2_a)
katet_1_b          = float(katet_1_b)
hypotenus_b        = float(hypotenus_b)

# a) Trekant A: Lengden til hypotenus
hypotenus_a        = sqrt(katet_1_a**2 + katet_2_a**2)

# b) Trekant B: Lengden til katet 2
try:
    # Prøv om lengdene er ok
    katet_2_b      = sqrt(hypotenus_b**2 - katet_1_b**2)

    # Avrunding
    if avrund_valg == 1:
        katet_1_a       = round(katet_1_a, avrund_ant)
        katet_2_a       = round(katet_2_a, avrund_ant)
        hypotenus_a     = round(hypotenus_a, avrund_ant)
        katet_1_b       = round(katet_1_b, avrund_ant)
        katet_2_b       = round(katet_2_b, avrund_ant)
        hypotenus_b     = round(hypotenus_b, avrund_ant)
except:
    # Lengdene er ikke definert
    print("")
    print(txt_error)
    hypotenus_b    = txt_ikke_def
    katet_2_b      = txt_ikke_def

# Print
print("")
print(txt_info_1)
print(txt_info_2)
print(txt_info_3)
print(txt_info_4)
print(txt_info_5)
print("")
print(txt_a_1, katet_1_a, enhet_m)
print(txt_a_2, katet_2_a, enhet_m)
print(txt_a_3, hypotenus_a, enhet_m)
print(txt_b_1, katet_1_b, enhet_m)
print(txt_b_2, katet_2_b, enhet_m)
print(txt_b_3, hypotenus_b, enhet_m)
print("")
