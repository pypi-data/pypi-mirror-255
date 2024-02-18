# 🚀 programmering.no | 🤓 matematikk.as
# - Fjern alle positive tall fra en liste med remove()

# Verdier
liste = [-3, -2.5, -1, 0, 1, 2, 3, 4, 5, 6]

# Funksjon som fjerner positive tall fra en liste
def fjern_positive_tall(liste):

	# Nullstill
	negative_tall_liste = list()

	# Itererer gjennom listen
	for tall in liste:

		# Legg tallet i listen hvis det er negativt
		if tall < 0:
			negative_tall_liste.append(tall)

	return negative_tall_liste

# Liste med positive tall
negative_tall_liste = fjern_positive_tall(liste)

# Print
print(f"Original liste          : {liste}")
print(f"Liste med negative tall : {negative_tall_liste}")
