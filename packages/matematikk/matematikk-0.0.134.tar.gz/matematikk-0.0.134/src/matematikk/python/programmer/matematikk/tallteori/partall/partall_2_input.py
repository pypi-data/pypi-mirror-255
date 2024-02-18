# 🚀 programmering.no | 🤓 matematikk.as
# - Finn partallene i en liste med mod 2

# Input
liste = input("Finn partallene i listen: ") # Husk [ ], f.eks. [1, 2, 3, 4]

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

# Input-string endres til liste med int-el
liste = str_til_int_liste(liste)

# Partall-liste
partall_liste = partall_liste_mod(liste)

# Print
print(f"Original liste : {liste}")
print(f"Partall-liste  : {partall_liste}")
