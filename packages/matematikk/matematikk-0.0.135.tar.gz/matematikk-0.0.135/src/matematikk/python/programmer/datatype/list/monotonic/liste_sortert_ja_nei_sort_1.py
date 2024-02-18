# 🚀 programmering.no | 🤓 matematikk.as
# - Se om listen er sortert i stigende eller synkende rekkefølge (monotonisk)
# - Kopierer, sorterer og sammenligner med den originale listen

# Input
liste = [1, 2, 3, 4, 5, 6, 7]

# Funksjon som ser om listen er monotonisk eller ikke
def er_liste_monotonisk_sort(liste):

    # Kopier alle el til de to listene
	stigende_liste = liste.copy()
	synkende_liste = liste.copy()

	# Sorter begge listene (stigende verdier)
	stigende_liste.sort()
	synkende_liste.sort()

	# Reverser den ene (synkende verdier)
	synkende_liste.reverse()

	# Hvis listen er enten stigende eller synkende
	if stigende_liste == liste or synkende_liste == liste: return True

    # Hvis listen er hverken stigende eller synkende
	else: return False

# Monotonisk eller ikke
er_monotonisk = er_liste_monotonisk_sort(liste)

# Liste
print(f"Liste: {liste}")
if er_monotonisk == True:
	print(f"Er listen sortert? Ja")
if er_monotonisk == False:
	print(f"Er listen sortert? Nei")
