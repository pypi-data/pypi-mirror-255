# 🚀 programmering.no | 🤓 matematikk.as
# - Finn positive tall i en liste

# Verdier
liste = [-3, -2.5, -1, 0, 1, 2, 3, 4, 5, 6]

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

# Positive tall
positive_tall_liste = positive_tall_liste(liste)

# Print
print(f"Original liste          : {liste}")
print(f"Liste med positive tall : {positive_tall_liste}")
