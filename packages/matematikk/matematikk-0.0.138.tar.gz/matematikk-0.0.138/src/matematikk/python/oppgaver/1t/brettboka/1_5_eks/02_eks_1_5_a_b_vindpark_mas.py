# 🚀 programmering.no | 🤓 matematikk.as
# Sinus 1T (2020) - BrettBoka - 1.5 Formler (s. 28) 
# Eksempel 1.5 a) og b) Vindpark I (Matematikk AS)

# Blokk med definisjoner
_blokk             = 1 # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker
if _blokk == 1:

    # Konstanter
    pi                 = 3.14          # Pi avrundet til 3.14
    turbin_radius      = 58.5          # Rotorbladets lengde, [m]
    turbin_areal       = 0             # Turbinens areal, [m^2], A = pi * r^2
    turbin_k           = 0.0003        # Turbin-konstant (lufttetthet og virkningsgrad), [W(s^3/m^5)]
    turbin_effekt      = 0             # Turbinens effekt (sekund), [kW]
    vindstyrke         = 5             # Lett bris, [m/s]

    # Enheter
    enhet_m_kvad       = "m^2"         # Kvadratmeter
    enhet_kw           = "kW"          # Kilowatt

    # Tekst
    txt_oppg           = "Eks 1.5 a) og b)"
    txt_strek          = "----------------"
    txt_a              = "a) Turbinens areal           :"
    txt_b              = "b) Turbinens effekt (sekund) :"

    # Innstillinger
    avrund_valg        = 1             # # 0: Ikke avrunding, 1: Avrunding
    avrund_ant         = None          # # None: 12.78 -> 13, 0: 12.78 -> 13.0, 1: 12.78 -> 12.8, 2: 12.78 -> 12.78

# a) Turbinens areal
turbin_areal       = pi * (turbin_radius**2)

# b) Turbinens effekt (sekund)
turbin_effekt      = turbin_k * (vindstyrke**3) * turbin_areal

# Avrunding
if avrund_valg == 1:
    turbin_areal   = round(turbin_areal, avrund_ant)
    turbin_effekt  = round(turbin_effekt, avrund_ant)

# Print
print("")
print(txt_strek)
print(txt_oppg)
print(txt_strek)
print("")
print(txt_a, turbin_areal, enhet_m_kvad)
print(txt_b, turbin_effekt, enhet_kw)
print("")
