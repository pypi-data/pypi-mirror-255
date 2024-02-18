# 🚀 programmering.no | 🤓 matematikk.as
# - Regn ut arealet av en sirkel

import math

# Verdier
r = 3

# Areal-funksjon for sirkel
def sirkel_areal_math(r):

    # Formel for arealet av sirkel
    areal = math.pi * pow(float(r), 2)

    return areal

# Areal
areal = sirkel_areal_math(r)

# Print
print(f"Arealet er:: {areal}")
