# 🚀 programmering.no | 🤓 matematikk.as
# - Regn ut summen av elementene i en liste med for-løkke

# Input
liste = input("Listen som summeres: ") # Husk [ ], f.eks. [1, 2, 3, 4]

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

# Funksjon som summerer el i en liste
def sum_liste(liste):

	# Nullstill
	sum = 0

	# Oppdater sum for hver iterasjon
	for el in liste:
		sum += el

	return(sum)

# Input-string endres til liste med int-el
liste = str_til_int_liste(liste)

# Sum
sum = sum_liste(liste)

# Print
print(f"Liste                : {liste}")
print(f"Summen av elementene : {sum}")
