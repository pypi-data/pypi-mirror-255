# 🚀 programmering.no | 🤓 matematikk.as
# - Se om listen er sortert i stigende eller synkende rekkefølge (monotonisk)
# - Kopierer, sorterer og sammenligner med den originale listen

# Input
liste_1 = [1, 2, 3, 4, 5]
liste_2 = [1, 2, 3, 5, 4]

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
er_monotonisk_1 = er_liste_monotonisk_sort(liste_1)
er_monotonisk_2 = er_liste_monotonisk_sort(liste_2)

# Liste 1
print(f"Liste 1: {liste_1}")
if er_monotonisk_1 == True:
	print(f"Er liste 1 sortert? Ja")
if er_monotonisk_1 == False:
	print(f"Er liste 1 sortert? Nei")

# Liste 2
print(f"Liste 2: {liste_2}")
if er_monotonisk_2 == True:
	print(f"Er liste 2 sortert? Ja")
if er_monotonisk_2 == False:
	print(f"Er liste 2 sortert? Nei")
