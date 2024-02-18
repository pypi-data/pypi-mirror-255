# 🚀 programmering.no | 🤓 matematikk.as
# Sinus 1T (2020) - BrettBoka - 1.5 Formler (s. 28) 
# Eksempel 1.5 a) og b) Vindpark I (boken)

from math import pi
radius = 58.5
vindstyrke = 5
areal = pi*radius**2
effekt = 0.0003*areal*vindstyrke**3
print("Arealet er", round(areal), "kvadratmeter.")
print("Effekten er", round(effekt), "kW.")
