# 🚀 programmering.no | 🤓 matematikk.as
# - Finn negative tall i en liste

# Verdier
liste = [-3, -2.5, -1, 0, 1, 2, 3, 4, 5, 6]

# Funksjon for å finne negative tall i en liste
def negative_tall_liste(liste):

	# Nullstill
	negative_tall_liste = list()

	# Itererer gjennom listen
	for tall in liste:

		# Legg tallet i listen hvis det er negativt
		if tall < 0:
			negative_tall_liste.append(tall)

	return negative_tall_liste

# Negative tall
negative_tall_liste = negative_tall_liste(liste)

# Print
print(f"Original liste          : {liste}")
print(f"Liste med negative tall : {negative_tall_liste}")
