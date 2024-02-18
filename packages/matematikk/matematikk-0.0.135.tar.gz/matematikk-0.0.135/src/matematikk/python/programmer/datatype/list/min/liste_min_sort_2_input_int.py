# 🚀 programmering.no | 🤓 matematikk.as
# - Finn det minste tallet i en liste med sort()

# Verdier
liste = input("Finn minimum i listen: ") # Husk [ ], f.eks. [1, 2, 3, 4]

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

# Funksjon for å finne min el i en liste med sort()
def minimum_sort(liste):

	# Sorterer listen i synkende rekkefølge med reverse-argument i sort()
	liste.sort(reverse=True)

	# Min el er siste el i listen (index -1)
	min = liste[-1]

	return min

# Input-string endres til liste med int-el
liste = str_til_int_liste(liste)

# Minimum
min = minimum_sort(liste)

# Print
print(f"Liste             : {liste}")
print(f"Minimum i listen  : {min}")
