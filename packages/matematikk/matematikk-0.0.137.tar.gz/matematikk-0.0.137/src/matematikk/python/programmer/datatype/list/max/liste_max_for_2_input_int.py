# 🚀 programmering.no | 🤓 matematikk.as
# - Finn det største elementet i en liste med for-løkke

# Input
liste = input("Finn maksimum i listen: ") # Husk [ ], f.eks. [1, 2, 3, 4]

# Enkel funksjon som klipper opp inp-str til liste med int-el
def str_til_int_liste(str_liste = list()):

    int_liste = list()
    el = str()
    for i in range(len(str_liste)):
        if str_liste[i] == " ": pass
        elif str_liste[i] == "[": pass
        elif str_liste[i] == "]":
            int_liste.append(int(el))
            el = ""
        elif str_liste[i] == ",":
            int_liste.append(int(el))
            el = ""
        else: el += str_liste[i]
    return int_liste

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

# Input-string endres til liste med int-el
liste = str_til_int_liste(liste)

# Maksimum
max = maksimum_for_loop(liste)

# Print
print(f"Liste             : {liste}")
print(f"Maksimum i listen : {max}")
