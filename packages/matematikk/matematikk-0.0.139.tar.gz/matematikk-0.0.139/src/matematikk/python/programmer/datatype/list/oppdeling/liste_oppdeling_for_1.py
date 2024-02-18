# 🚀 programmering.no | 🤓 matematikk.as
# - Del en liste opp i mindre lister med n elementer i hver liste

# Verdier
steg  = 4
liste = [
                    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                    "k", "l", "m", "n", "o", "p", "q", "r", "s", "s",
                    "u", "v", "w", "x", "y", "z"
                ]

# Del opp listen i del-lister med n elementer i hver del-liste
def oppdeling_lister_for_loop(liste):

    # Nullstill
    start      = 0
    slutt      = len(liste)
    del_lister = []

    # Itererer gjennom listen
    for i in range(start, slutt, steg):
        del_lister.append(liste[i : i + steg])

    return del_lister

# Del-lister
del_lister = oppdeling_lister_for_loop(liste)

# Print
print(f"Del-lister (hele): {del_lister}")
print("Del-lister (en og en):")
for del_liste in del_lister:
	print(f"{del_liste}")
