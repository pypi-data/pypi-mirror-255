# 🚀 programmering.no | 🤓 matematikk.as
# - Se om intervallet har primtall
# - Algoritmen kan optimaliseres ved å bytte ut int(n / 2) med int(sqrt(n))

# Input
min = input("Min verdi: ")
max = input("Max verdi: ")

# Funksjon for å se intervallet har primtall
def er_primtall_intervall(min, max):

    # Itererer gjennom intervallet
	for n in range(int(min), int(max) + 1):

		# Alle primtall er større enn 1
		if n > 1:

			# Iterer fra 2 til n / 2 + 1 (medium tempo)
			for i in range(2, int(n / 2) + 1):

				# n er ikke et primtall hvis det er delelig med i
				if n % i == 0:
					print(f"Er {n} et primtall? Nei")
					break

			# Hvis for-løkken fullføres uten break
			else: print(f"Er {n} et primtall? Ja")

		# Hvis tallet ikke er større enn 1 er det ikke primtall
		else: print(f"Er {n} et primtall? Nei")

# Primtall eller ikke
er_primtall_intervall(min, max)
