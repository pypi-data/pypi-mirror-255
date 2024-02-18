# 🚀 programmering.no | 🤓 matematikk.as
# - Finn det minste tallet i en liste med for-løkke

# Input
liste = [2, 3, 400, 50, 10]

# Funksjon for å finne min el i en liste med for-løkke
def minimum_for_loop(liste):

	# Sett første el som forløpig min
	min = liste[0]

	# Itererer gjennom listen
	for i in range(1, len(liste)):

		# Oppdater min hvis el er mindre enn nåværende min
		if liste[i] < min:
			min = liste[i]

	return min

# Minimum
min = minimum_for_loop(liste)

# Print
print(f"Liste             : {liste}")
print(f"Minimum i listen  : {min}")
