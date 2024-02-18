# 🚀 programmering.no | 🤓 matematikk.as
# - Finn oddetallene i en liste

# Verdier
liste = [-3, -2.5, -1, 0, 1, 2, 3, 4, 5, 6]

# Funksjon for å finner oddetallene i en liste
def oddetall_liste_mod(liste):

	# Nullstill
	oddetall_liste = list()

	# Itererer gjennom listen
	for tall in liste:

		# Hvis resten av divisjon med 2 ikke er 0, så er tallet et oddetall
		if tall % 2 != 0:
			oddetall_liste.append(tall)

	return oddetall_liste

# Oddetatall-listen
oddetall_liste = oddetall_liste_mod(liste)

# Print
print(f"Original liste : {liste}")
print(f"Oddetall-liste  : {oddetall_liste}")
