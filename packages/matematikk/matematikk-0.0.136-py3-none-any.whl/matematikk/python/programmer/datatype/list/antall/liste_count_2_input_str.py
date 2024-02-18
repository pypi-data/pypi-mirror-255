# 🚀 programmering.no | 🤓 matematikk.as
# - Teller hvor mange utvalgte elementer det er i en liste

# Input
liste = input("Liste: ") # Husk [ ] og '', f.eks. ['gull', 'sølv', 'bronse']
karakter = input("Karakter: ") # Uten hermetegn, f.eks. gull

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

# Antall
antall = liste.count(karakter)

# Print
if antall > 0:
	print(f"{antall} elev(er) fikk karakter {karakter}")
else:
	print(f"Ingen elever fikk karakter {karakter}")
