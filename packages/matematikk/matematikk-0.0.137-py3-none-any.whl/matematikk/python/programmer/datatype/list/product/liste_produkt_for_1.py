# 🚀 programmering.no | 🤓 matematikk.as
# - Finn produktet av alle elementene i en liste

# Verdier
liste = [2, 4, 10]

# Funksjon som multipliserer alle el i en liste
def produkt_liste(liste):

	# Sett startverdi som 1
	produkt = 1

	# Oppdater sum for hver iterasjon
	for el in liste:
		produkt *= el

	return(produkt)

# Sum
produkt = produkt_liste(liste)

# Print
print(f"Liste                   : {liste}")
print(f"Produktet av elementene : {produkt}")
