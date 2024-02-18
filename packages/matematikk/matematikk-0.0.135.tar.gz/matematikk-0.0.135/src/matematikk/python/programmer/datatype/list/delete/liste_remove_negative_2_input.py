# 🚀 programmering.no | 🤓 matematikk.as
# - Fjern alle negative tall fra en liste med remove()

# Input
liste = input("Liste: ") # Husk [ ] og "", f.eks. [2.5, 10]

# Enkel funksjon som klipper opp inp-str til liste med float-el
def str_til_float_liste(str_liste = list()):

    float_liste = list()
    el = str()
    for i in range(len(str_liste)):
        if str_liste[i] == " ": pass
        elif str_liste[i] == "[": pass
        elif str_liste[i] == "]":
            float_liste.append(float(el))
            el = ""
        elif str_liste[i] == ",":
            float_liste.append(float(el))
            el = ""
        else: el += str_liste[i]
    return float_liste

# Funksjon som fjerner negative tall fra en liste
def fjern_negative_tall(liste):

	# Nullstill
	positive_tall_liste = list()

	# Itererer gjennom listen
	for tall in liste:

		# Legg tallet i listen hvis det er positivt
		if tall > 0:
			positive_tall_liste.append(tall)

	return positive_tall_liste

# Input-string endres til liste med float-el
liste = str_til_float_liste(liste)

# Liste med negative tall
positive_tall_liste = fjern_negative_tall(liste)

# Print
print(f"Original liste          : {liste}")
print(f"Liste med positive tall : {positive_tall_liste}")
