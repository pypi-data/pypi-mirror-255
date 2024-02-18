# 🚀 programmering.no | 🤓 matematikk.as
# - Del en liste opp i mindre lister med n elementer i hver liste

# Input
liste = input("Listen som skal deles opp: ") # Husk [ ] og '', f.eks. ['gull', 'sølv', 'bronse']
n_deler = input("Antall elementer per liste: ")

# Enkel funksjon som klipper opp inp-str til liste med str-el
def str_til_str_liste(str_liste = list()):

    str_ferdig_liste = list()
    el = str()
    for i in range(len(str_liste)):
        if str_liste[i] == " ": pass
        elif str_liste[i] == "[": pass
        elif str_liste[i] == "]":
            str_ferdig_liste.append(el)
            el = ""
        elif str_liste[i] == ",":
            str_ferdig_liste.append(el)
            el = ""
        elif str_liste[i] == '"': pass # Fjerner doble hermetegn ("")
        elif str_liste[i] == "'": pass # Fjerner doble hermetegn ('')
        else: el += str_liste[i]
    return str_ferdig_liste

# Input-string endres til liste med str-el
liste = str_til_str_liste(liste)

# Del opp listen i del-lister med n elementer i hver del-liste
def oppdeling_lister_comprehension(liste, n_deler):

    n_deler    = int(n_deler)
    del_lister = []

    # Lager del-listene med list comprehension
    del_lister = [liste[i : i + n_deler] for i in range(0, len(liste), n_deler)]

    return del_lister

# Del-lister
del_lister = oppdeling_lister_comprehension(liste, n_deler)

# Print
print(f"Del-lister (hele): {del_lister}")
print("Del-lister (en og en):")
for del_liste in del_lister:
	print(f"{del_liste}")
