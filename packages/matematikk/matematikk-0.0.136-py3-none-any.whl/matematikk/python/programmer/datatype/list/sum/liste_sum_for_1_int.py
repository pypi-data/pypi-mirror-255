# 🚀 programmering.no | 🤓 matematikk.as
# - Regn ut summen av elementene i en liste med for-løkke

# Verdier
liste = [2, 3, 10]

# Funksjon som summerer el i en liste
def sum_liste(liste):

	# Nullstill
	sum = 0

	# Oppdater sum for hver iterasjon
	for el in liste:
		sum += el

	return(sum)

# Sum
sum = sum_liste(liste)

# Print
print(f"Liste                : {liste}")
print(f"Summen av elementene : {sum}")
