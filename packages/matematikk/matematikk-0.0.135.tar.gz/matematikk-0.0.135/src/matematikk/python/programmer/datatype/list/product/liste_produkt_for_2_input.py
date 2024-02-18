# 🚀 programmering.no | 🤓 matematikk.as
# - Finn produktet av alle elementene i en liste

# Input
liste = input("Liste: ") # Husk [ ] og "", f.eks. [2.5, 10]

# Enkel funksjon som klipper opp inp-str til liste med float-el
def str_til_float_liste(str_liste = list()):

    float_liste = list()
    el = str()
    for i in range(len(str_liste)):
        if str_liste[i] == " ": pass
        elif str_liste[i] == "[": pass
        elif str_liste[i] == "]":
            float_liste.append(float(el))
            el = ""
        elif str_liste[i] == ",":
            float_liste.append(float(el))
            el = ""
        else: el += str_liste[i]
    return float_liste

# Funksjon som multipliserer alle el i en liste
def produkt_liste(liste):

	# Sett startverdi som 1
	produkt = 1

	# Oppdater sum for hver iterasjon
	for el in liste:
		produkt *= el

	return(produkt)

# Input-string endres til liste med float-el
liste = str_til_float_liste(liste)

# Sum
produkt = produkt_liste(liste)

# Print
print(f"Liste                   : {liste}")
print(f"Produktet av elementene : {produkt}")
