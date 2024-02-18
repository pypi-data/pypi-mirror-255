# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Torodd)
# Oppgave 1 a) Sofa-produksjon til møbelfabrikk - Finn O(x) 

import numpy as np

# definerer variablar for x og y
x = np.array([10, 25, 40, 70, 100, 140, 180])
y = np.array([270, 550, 870, 1500, 2200, 3300, 4500])

# finn koeffesientane med regresjon (andregradsfunksjon)
a, b, c = np.polyfit(x, y, 2)

print(f"K(x) = {a:.3f}x^2 + {b:.0f}x + {c:.0f}")
