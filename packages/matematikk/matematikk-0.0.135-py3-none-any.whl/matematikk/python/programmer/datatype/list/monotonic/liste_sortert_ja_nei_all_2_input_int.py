# 🚀 programmering.no | 🤓 matematikk.as
# - Se om listen er sortert i stigende eller synkende rekkefølge (monotonisk)
# - Kort versjon med all()

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
def er_liste_monotonisk(liste):

	# Returner True hvis listen er monotonisk og False hvis ikke
	return (all(liste[i] <= liste[i + 1] for i in range(len(liste) - 1)) or
			all(liste[i] >= liste[i + 1] for i in range(len(liste) - 1)))

# Input-string endres til liste med int-el
liste = str_til_int_liste(liste)

# Monotonisk eller ikke
er_monotonisk = er_liste_monotonisk(liste)

# Liste
if er_monotonisk == True:
	print(f"Er listen sortert? Ja")
if er_monotonisk == False:
	print(f"Er listen sortert? Nei")
