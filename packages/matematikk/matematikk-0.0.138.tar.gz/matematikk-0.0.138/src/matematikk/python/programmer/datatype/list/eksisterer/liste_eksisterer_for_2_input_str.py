# 🚀 programmering.no | 🤓 matematikk.as
# - Ser om et element eksisterer i en liste

# Nullstill
eksisterer_flagg = False

# Input
liste = input("Liste: ") # Husk [ ] og '', f.eks. ['gull', 'sølv', 'bronse']
el_inp = input("Søk etter element: ") # Uten hermetegn, f.eks. gull

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

# Itererer gjennom listen
for el in liste:

    # El eksisterer i listen
    if el == el_inp:

        # Sett flagget til True
        eksisterer_flagg = True

        # Print el
        print(f"Ja, {el_inp} eksisterer i listen")

# Hvis flagget fremdeles er False eksister ikke el i listen
if eksisterer_flagg == False:

    # Print el
    print("Nei, elementet eksisterer ikke i listen")
