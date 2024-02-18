# 🚀 programmering.no | 🤓 matematikk.as
# - Finn det største elementet i en liste med for-løkke

# Verdier
liste = [2, 3, 400, 50, 10]

# Funksjon for å finne max el i en liste med for-løkke
def maksimum_for_loop(liste):

	# Sett første el som forløpig max
	max = liste[0]

	# Itererer gjennom listen
	for i in range(1, len(liste)):

		# Oppdater max hvis el er større enn nåværende max
		if liste[i] > max:
			max = liste[i]

	return max

# Maksimum
max = maksimum_for_loop(liste)

# Print
print(f"Liste             : {liste}")
print(f"Maksimum i listen : {max}")
