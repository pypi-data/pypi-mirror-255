# 🚀 programmering.no | 🤓 matematikk.as
# - Rotere en liste til høyre eller venstre
# - Def: Listene roterer som "Pacman"
#   Å f.eks. rotere med 3 til venstre betyr at 3 elementer først "forsvinner"
#   til venstre, før de dukker opp igjen på høyre side
# - Eks: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] => [4, 5, 6, 7, 8, 9, 10, 1, 2, 3]

# Input
liste = input("Listen som roteres: ") # Husk [ ], f.eks. [1, 2, 3, 4]
rotasjon_retning = input("Rotasjons-retning (v /h): ")
rotasjon_antall = input("Rotasjons-antall: ")

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

# Funksjon som roterer listen til ventre eller høyre
def roter_liste(liste, rotasjon_retning, rotasjon_antall):

	liste          = str_til_int_liste(liste)
	rota_ant       = int(rotasjon_antall)
	rotert_liste_1 = list()
	rotert_liste_2 = list()
	ferdig_liste   = list()

	i = 0
	while i < len(liste):

        # Eks. 3 venstre-rotert => [4, 5, 6, 7, 8, 9, 10] + [1, 2, 3]
		if rotasjon_retning == "v":
			if i <  rota_ant: 			   rotert_liste_1.append(liste[i]) # Eks: [1, 2, 3]
			if i >= rota_ant: 			   rotert_liste_2.append(liste[i]) # Eks: [4, 5, 6, 7, 8, 9, 10]

        # Eks. 3 høyre-rotert => [8, 9, 10] + [1, 2, 3, 4, 5, 6, 7]
		if rotasjon_retning == "h":
			if i >= len(liste) - rota_ant: rotert_liste_2.append(liste[i]) # Eks: [8, 9, 10]
			if i <  len(liste) - rota_ant: rotert_liste_1.append(liste[i]) # Eks: [1, 2, 3, 4, 5, 6, 7]

        # Inkrement i
		i += 1

	# Legg sammen listene
	ferdig_liste =  rotert_liste_2 + rotert_liste_1

	return ferdig_liste

# Roterte lister
rotert_v_liste = roter_liste(liste, "v", rotasjon_antall) # Eks: ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "v", 3)
rotert_h_liste = roter_liste(liste, "h", rotasjon_antall)

# Print
print(f"Liste før rotasjon   	         : {liste}")
if rotasjon_retning == "v":
	print(f"Liste etter venstre-rotasjon ({rotasjon_antall}) : {rotert_v_liste}")
if rotasjon_retning == "h":
	print(f"Liste etter right-rotasjon   ({rotasjon_antall}) : {rotert_h_liste}")
