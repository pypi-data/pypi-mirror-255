# 🚀 programmering.no | 🤓 matematikk.as
# - Finn partallene i en liste med mod 2

# Verdier
liste = [-3, -2.5, -1, 0, 1, 2, 3, 4, 5, 6]

# Funksjon for å finner partallene i en liste
def partall_liste_mod(liste):

	# Nullstill
	partall_liste = list()

	# Itererer gjennom listen
	for tall in liste:

		# Hvis resten av divisjon med 2 er 0, så er tallet et partall
		if tall % 2 == 0:
			partall_liste.append(tall)

	return partall_liste

# Partall-liste
partall_liste = partall_liste_mod(liste)

# Print
print(f"Original liste : {liste}")
print(f"Partall-liste  : {partall_liste}")
