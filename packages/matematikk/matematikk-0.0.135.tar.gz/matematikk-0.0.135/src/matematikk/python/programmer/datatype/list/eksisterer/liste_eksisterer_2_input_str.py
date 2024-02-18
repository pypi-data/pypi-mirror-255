# 🚀 programmering.no | 🤓 matematikk.as
# - Ser om et element eksisterer i en liste

# Input
liste = input("Liste: ") # Husk [ ] og '', f.eks. ['gull', 'sølv', 'bronse']
el = input("Søk etter element: ") # Uten hermetegn, f.eks. gull

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

# Ser om el eksisterer i listen
if el in liste:
    print(f"Ja, {el} eksisterer i listen")
else:
	print("Nei, elementet eksisterer ikke i listen")
