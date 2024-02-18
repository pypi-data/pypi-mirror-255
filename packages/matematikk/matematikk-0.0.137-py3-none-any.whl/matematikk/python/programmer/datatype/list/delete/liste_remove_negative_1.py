# 🚀 programmering.no | 🤓 matematikk.as
# - Fjern alle negative tall fra en liste med remove()

# Verdier
liste = [-3, -2.5, -1, 0, 1, 2, 3, 4, 5, 6]

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

# Liste med negative tall
positive_tall_liste = fjern_negative_tall(liste)

# Print
print(f"Original liste          : {liste}")
print(f"Liste med positive tall : {positive_tall_liste}")
