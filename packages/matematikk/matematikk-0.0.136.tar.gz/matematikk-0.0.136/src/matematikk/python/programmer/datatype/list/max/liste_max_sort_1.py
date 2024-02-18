# 🚀 programmering.no | 🤓 matematikk.as
# - Finn det største elementet i en liste med sort()

# Verdier
liste = [10, 7000, 20, 3, 400]

# Funksjon for å finne max el i en liste med sort()
def maksimum_sort(liste):

	# Sorterer listen i stigende rekkefølge
	liste.sort()

	# Max el er siste el i listen (index -1)
	max = liste[-1]

	return max

# Maksimum
max = maksimum_sort(liste)

# Print
print(f"Liste             : {liste}")
print(f"Maksimum i listen : {max}")
