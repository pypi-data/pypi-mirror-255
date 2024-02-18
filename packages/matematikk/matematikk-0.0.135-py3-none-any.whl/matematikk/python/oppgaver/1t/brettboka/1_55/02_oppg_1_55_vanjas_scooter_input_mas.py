# 🚀 programmering.no | 🤓 matematikk.as
# Sinus 1T (2020) - BrettBoka - 1.5 Formler (s. 27) 
# Oppgave 1.59 Vanjas scooter (Matematikk AS)

# Blokk med definisjoner
_blokk             = 1 # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker
if _blokk == 1:

    # Konstanter
    distanse_igjen     = 14            # Distanse hun har igjen, [km]
    distanse_kjort     = 0             # Distanse hun har kjørt, [km]
    distanse_tot       = 35            # Distanse mellom husene, [km]
    distanse_0         = 0             # Distanse hjemme er 0, [km]
    tid_igjen          = 0             # Tiden hun har igjen, [h]
    tid_kjort          = 0             # Tiden hun har kjørt, [h]
    tid_tot            = 0             # Tiden hun bruker mellom husene, [h]
    tid_min_per_time   = 60            # 60 min per time
    fart               = 0             # Farten hennes, [km/h], v = s / t <=> t = s / v
    fart_km_per_min    = 0.7           # 0.7 km per min

    # Konverter fart fra km/min -> km/h
    fart               = fart_km_per_min * tid_min_per_time

    # Enheter
    enhet_km           = "km"          # Kilometer
    enhet_min          = "min"         # Minutter
    enhet_km_h         = "km/h"        # Kilometer i timen

    # Tekst
    txt_oppg           = "Oppg 1.55"
    txt_strek          = "---------"
    txt_info_1         = "Distanse mellom husene            :"
    txt_a_1            = "a) Formel for tiden hun har kjørt"
    txt_a_2            = "      s = 35 - 0.7 t"
    txt_a_3            = "      0.7 t = 35 - s"
    txt_a_4            = "      0.7 t / 0.7 = (35 - s) / 0.7"
    txt_a_5            = "      t = (35 - s) / 0.7"
    txt_b              = "b) Tiden hun har kjørt            :"
    txt_c              = "c) Tiden hun bruker mellom husene :"
    txt_info_2         = "Tiden hun har igjen               :"
    txt_info_3         = "Distanse hun har kjørt            :"
    txt_info_4         = "Distanse hun har igjen            :"
    txt_info_5         = "Farten hennes                     :"

    # Innstillinger
    inp                = 1             # # 0: Boken, 1: Bruker
    avrund_valg        = 1             # # 0: Ikke avrunding, 1: Avrunding
    avrund_ant         = None          # # None: 12.78 -> 13, 0: 12.78 -> 13.0, 1: 12.78 -> 12.8, 2: 12.78 -> 12.78

# Input
print("")
print(txt_strek)
print(txt_oppg)
print(txt_strek)
print("")
print(txt_info_1, distanse_tot, enhet_km)
if inp == 1:

    print("")
    distanse_igjen = input("Hvor langt har hun kjørt [km]? ")
    fart = input("Hva er farten hennes [km/h]? ")

    # Type casting: str -> float
    distanse_igjen     = float(distanse_igjen)
    fart               = float(fart)

# a) Formel for tiden hun har kjørt
def get_tid(distanse):
    # v = s / t <=> t = s / v
    _tid           = (distanse_tot - distanse) / fart
    _tid           = _tid * tid_min_per_time
    return _tid

def get_tid_ez(distanse):
    # t = (35 - s) / 0.7
    _tid           = (distanse_tot - distanse) / fart_km_per_min
    return _tid

# b) Tiden hun har kjørt
tid_kjort          = get_tid(distanse_igjen)

# c) Tiden hun bruker mellom husene
tid_tot            = get_tid(distanse_0)

# Tiden hun har igjen
tid_igjen          = tid_tot - tid_kjort

# Distanse hun har kjørt
distanse_kjort     = distanse_tot - distanse_igjen

# Avrunding
if avrund_valg == 1:
    tid_kjort      = round(tid_kjort, avrund_ant)
    tid_tot        = round(tid_tot, avrund_ant)
    tid_igjen      = round(tid_igjen, avrund_ant)
    distanse_kjort = round(distanse_kjort, avrund_ant)
    distanse_igjen = round(distanse_igjen, avrund_ant)
    fart           = round(fart, avrund_ant)

# Print
print("")
print(txt_a_1)
print(txt_a_2)
print(txt_a_3)
print(txt_a_4)
print(txt_a_5)
print(txt_b, tid_kjort, enhet_min)
print(txt_c, tid_tot, enhet_min)
print("")
print(txt_info_2, tid_igjen, enhet_min)
print(txt_info_3, distanse_kjort, enhet_km)
print(txt_info_4, distanse_igjen, enhet_km)
print(txt_info_5, fart, enhet_km_h)
print("")
