# 🚀 programmering.no | 🤓 matematikk.as
# - Reverserer rekkefølgen til elementene i en liste
# - Hastighet reverse(): Ca. 33 ms per loop for liste m/ 100 000 000 el

# Input
liste = input("Listen som reverseres: ") # Husk [ ], f.eks. [1, 2, 3, 4]

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

# Input-string endres til liste med int-el
liste = str_til_int_liste(liste)

# Kopier listen hvis du vil beholde originalen
reversert_liste = liste.copy()

# Reverse
reversert_liste.reverse()

# Print
print(f"Original liste  : {liste}")
print(f"Reversert liste : {reversert_liste}")
