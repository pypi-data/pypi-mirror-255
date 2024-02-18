# 🚀 programmering.no | 🤓 matematikk.as
# - Finn det minste tallet i en liste med sort()

# Verdier
liste = [10, 7000, 20, 3, 400]

# Funksjon for å finne min el i en liste med sort()
def minimum_sort(liste):

	# Sorterer listen i synkende rekkefølge med reverse-argument i sort()
	liste.sort(reverse=True)

	# Min el er siste el i listen (index -1)
	min = liste[-1]

	return min

# Minimum
min = minimum_sort(liste)

# Print
print(f"Liste             : {liste}")
print(f"Minimum i listen  : {min}")
