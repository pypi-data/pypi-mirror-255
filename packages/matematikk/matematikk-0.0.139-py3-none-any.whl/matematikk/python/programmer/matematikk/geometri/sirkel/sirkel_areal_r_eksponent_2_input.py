# 🚀 programmering.no | 🤓 matematikk.as
# - Regn ut arealet av en sirkel

# Verdier
pi = 3.14

# Input
r = input("Sirkelens radius er: ")

# Areal-funksjon for sirkel
def sirkel_areal(r):

    # Formel for arealet av sirkel
    areal = pi * float(r)**2

    return areal

# Areal
areal = sirkel_areal(r)

# Print
print(f"Arealet er:: {areal}")
