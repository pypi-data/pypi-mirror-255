# 🚀 programmering.no | 🤓 matematikk.as
# Sinus 1T (2020) - BrettBoka - 1.5 Formler (s. 29) 
# Oppgave 1.56 Vindpark II: Elbiler (Matematikk AS)

# Blokk med definisjoner
_blokk             = 1 # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker
if _blokk == 1:

    # Konstanter
    pi                 = 3.14          # Pi avrundet til 3.14
    turbin_radius      = 58.5          # Rotorbladets lengde, [m]
    turbin_areal       = 0             # Turbinens areal, [m^2], A = pi * r^2
    turbin_k           = 0.0003        # Turbin-konstant (lufttetthet og virkningsgrad), [W(s^3/m^5)]
    turbin_effekt      = 0             # Turbinens effekt (sekund), [kW]
    turbin_energi      = 0             # Turbinens energi (år), [kWh]
    turbin_vindpark    = 80            # Antall turbiner i vindparken
    vindstyrke         = 5             # Lett bris, [m/s]
    tid_h_per_dogn     = 24            # Timer per døgn, [h/døgn]
    tid_dogn           = 300           # Døgn turbinen kjører, [døgn]
    tid_h              = 0             # Timer turbinen kjører, [h]
    hus_energi         = 20000         # Energi per hus (år), [kWh]
    hus_turbin         = 0             # Antall hus en turbin forsyner (år)
    hus_vindpark       = 0             # Antall hus vindparken forsyner (år)
    elbil_energi       = 3000          # Energi per elbil (år), [kWh]
    elbil_turbin       = 0             # Antall elbiler en turbin forsyner (år)
    elbil_vindpark     = 0             # Antall elbiler vindparken forsyner (år)

    # Enheter
    enhet_m_kvad       = "m^2"         # Kvadratmeter
    enhet_kw           = "kW"          # Kilowatt
    enhet_kwh          = "kWh"         # Kilowattimer

    # Tekst
    txt_oppg           = "Oppg 1.56"
    txt_strek          = "---------"
    txt_info_1         = "Turbinens areal                            :"
    txt_info_2         = "Turbinens effekt (sekund)                  :"
    txt_info_3         = "Turbinens energi (år)                      :"
    txt_a              = "a) Antall elbiler en turbin forsyner (år)  :"
    txt_b              = "b) Antall elbiler vindparken forsyner (år) :"

    # Innstillinger
    inp                = 0             # # 0: Boken, 1: Bruker
    avrund_valg        = 1             # # 0: Ikke avrunding, 1: Avrunding
    avrund_ant         = None          # # None: 12.78 -> 13, 0: 12.78 -> 13.0, 1: 12.78 -> 12.8, 2: 12.78 -> 12.78

# Input
print("")
print(txt_strek)
print(txt_oppg)
print(txt_strek)
# if inp == 1:
#     print("")
#     turbin_radius = input("Hvor lange er rotorbladene [m]? ")
#     vindstyrke = input("Hva er vindstyrken [m/s]? ")
#
#     # Type casting: str -> float
#     turbin_radius      = float(turbin_radius)
#     vindstyrke         = float(vindstyrke)

# Turbinens areal
turbin_areal       = pi * (turbin_radius**2)

# Turbinens effekt (sekund)
turbin_effekt      = turbin_k * (vindstyrke**3) * turbin_areal

# Turbinens energi (år)
tid_h              = tid_h_per_dogn * tid_dogn
turbin_energi      = turbin_effekt * tid_h

# a) Antall elbiler en turbin forsyner (år)
elbil_turbin       = turbin_energi / elbil_energi

# b) Antall elbiler vindparken forsyner (år)
elbil_vindpark     = elbil_turbin * turbin_vindpark

# Avrunding
if avrund_valg == 1:
    turbin_areal   = round(turbin_areal, avrund_ant)
    turbin_effekt  = round(turbin_effekt, avrund_ant)
    turbin_energi  = round(turbin_energi, avrund_ant)
    elbil_turbin   = round(elbil_turbin, avrund_ant)
    elbil_vindpark = round(elbil_vindpark, avrund_ant)

# Print
print("")
print(txt_info_1, turbin_areal, enhet_m_kvad)
print(txt_info_2, turbin_effekt, enhet_kw)
print(txt_info_3, turbin_energi, enhet_kwh)
print(txt_a, elbil_turbin)
print(txt_b, elbil_vindpark)
