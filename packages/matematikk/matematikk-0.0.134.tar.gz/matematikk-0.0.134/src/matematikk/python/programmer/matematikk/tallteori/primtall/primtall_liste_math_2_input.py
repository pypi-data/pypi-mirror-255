# 🚀 programmering.no | 🤓 matematikk.as
# - Se om intervallet har primtall

# Variabler
primtall_liste = list()

from math import sqrt

# Input
min = input("Min verdi: ")
max = input("Max verdi: ")

# Funksjon for å se intervallet har primtall
def er_primtall_intervall_sqrt(min, max):

    # Itererer gjennom intervallet
	for n in range(int(min), int(max) + 1):

		# Alle primtall er større enn 1
		if n > 1:

			# Iterer fra 2 til n / 2 + 1 (medium tempo)
			for i in range(2, int(sqrt(n)) + 1):

				# n er ikke et primtall hvis det er delelig med i
				if n % i == 0: break

			# Hvis for-løkken fullføres uten break
			else: primtall_liste.append(n)

	return primtall_liste

# Primtall eller ikke
primtall_liste = er_primtall_intervall_sqrt(min, max)

# Print
if len(primtall_liste) == 0:
	print(f"Det er ingen primtall mellom {min} og {max}")
else:
	print(f"Primtallene mellom {min} og {max} er: {primtall_liste}")
