# 🚀 programmering.no | 🤓 matematikk.as
# - Finn positive tall i en liste

# Verdier
liste = input("Finn positive tall i listen: ") # Husk [ ], f.eks. [-2, -1, 3, 15]

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

# Funksjon for å finne positive tall i en liste
def positive_tall_liste(liste):

	# Nullstill
	positive_tall_liste = list()

	# Itererer gjennom listen
	for tall in liste:

		# Legg tallet i listen hvis det er positivt
		if tall > 0:
			positive_tall_liste.append(tall)

	return positive_tall_liste

# Input-string endres til liste med int-el
liste = str_til_int_liste(liste)

# Positive tall
positive_tall_liste = positive_tall_liste(liste)

# Print
print(f"Original liste          : {liste}")
print(f"Liste med positive tall : {positive_tall_liste}")
