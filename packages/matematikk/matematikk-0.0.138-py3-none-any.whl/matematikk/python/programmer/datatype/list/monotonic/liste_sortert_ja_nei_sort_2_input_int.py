# 🚀 programmering.no | 🤓 matematikk.as
# - Se om listen er sortert i stigende eller synkende rekkefølge (monotonisk)
# - Kopierer, sorterer og sammenligner med den originale listen

# Input
liste = input("Liste: ") # Husk [ ], f.eks. [1, 2, 3, 4]

# Enkel funksjon som klipper opp inp-str til liste med int-el
def str_til_int_liste(str_liste = list()):

    int_liste = list()
    el = str()
    for i in range(len(str_liste)):
        if str_liste[i] == " ": pass
        elif str_liste[i] == "[": pass
        elif str_liste[i] == "]":
            int_liste.append(int(el))
            el = ""
        elif str_liste[i] == ",":
            int_liste.append(int(el))
            el = ""
        else: el += str_liste[i]
    return int_liste

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

# Input-string endres til liste med int-el
liste = str_til_int_liste(liste)

# Monotonisk eller ikke
er_monotonisk = er_liste_monotonisk_sort(liste)

# Liste
if er_monotonisk == True:
	print(f"Er listen sortert? Ja")
if er_monotonisk == False:
	print(f"Er listen sortert? Nei")
