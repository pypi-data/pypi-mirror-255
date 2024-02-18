# 🚀 programmering.no | 🤓 matematikk.as
# - Finn antall elementer i en liste med len()

# Input
liste = input("Liste: ") # Husk [ ] og '', f.eks. ['gull', 'sølv', 'bronse']

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

# Print
print(f"Liste: {liste}")

# Antall el i listen ("lengden" til listen)
el_ant = len(liste)

# Print
print(f"Antall el i listen: {el_ant}")
