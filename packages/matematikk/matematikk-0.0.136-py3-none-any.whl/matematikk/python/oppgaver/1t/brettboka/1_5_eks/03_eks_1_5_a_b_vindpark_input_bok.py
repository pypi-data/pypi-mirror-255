# 🚀 programmering.no | 🤓 matematikk.as
# Sinus 1T (2020) - BrettBoka - 1.5 Formler (s. 28) 
# Eksempel 1.5 a) og b) Vindpark I - Input (boken)

from math import pi
svar = input("Hvor lange er rotorbladene i meter?")
radius = float(svar)
svar = input("Hva er vindstyrken i meter per sekund?")
vindstyrke = float(svar)
areal = pi*radius**2
effekt = 0.0003*areal*vindstyrke**3
print("Arealet er", round(areal), "kvadratmeter.")
print("Effekten er", round(effekt), "kW.")
