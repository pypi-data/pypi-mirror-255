# 🚀 programmering.no | 🤓 matematikk.as
# - Se om listen er sortert i stigende eller synkende rekkefølge (monotonisk)
# - Kort versjon med all()

# Verdier
liste = [1, 2, 3, 4, 5, 6, 7]

# Funksjon som ser om listen er monotonisk eller ikke
def er_liste_monotonisk(liste):

	# Returner True hvis listen er monotonisk og False hvis ikke
	return (all(liste[i] <= liste[i + 1] for i in range(len(liste) - 1)) or
			all(liste[i] >= liste[i + 1] for i in range(len(liste) - 1)))

# Monotonisk eller ikke
er_monotonisk = er_liste_monotonisk(liste)

# Liste
print(f"Liste: {liste}")
if er_monotonisk == True:
	print(f"Er listen sortert? Ja")
if er_monotonisk == False:
	print(f"Er listen sortert? Nei")
