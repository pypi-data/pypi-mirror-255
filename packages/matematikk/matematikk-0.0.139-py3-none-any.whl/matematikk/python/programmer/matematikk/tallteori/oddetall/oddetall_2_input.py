# 🚀 programmering.no | 🤓 matematikk.as
# - Finn oddetallene i en liste

# Input
liste = input("Finn oddetallene i listen: ") # Husk [ ], f.eks. [1, 2, 3, 4]

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

# Funksjon for å finner oddetallene i en liste
def oddetall_liste_mod(liste):

	# Nullstill
	oddetall_liste = list()

	# Itererer gjennom listen
	for tall in liste:

		# Hvis resten av divisjon med 2 ikke er 0, så er tallet et oddetall
		if tall % 2 != 0:
			oddetall_liste.append(tall)

	return oddetall_liste

# Input-string endres til liste med int-el
liste = str_til_int_liste(liste)

# Oddetatall-listen
oddetall_liste = oddetall_liste_mod(liste)

# Print
print(f"Original liste : {liste}")
print(f"Oddetall-liste  : {oddetall_liste}")
