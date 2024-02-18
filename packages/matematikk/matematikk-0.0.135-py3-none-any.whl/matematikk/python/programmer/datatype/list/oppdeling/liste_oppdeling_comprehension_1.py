# 🚀 programmering.no | 🤓 matematikk.as
# - Del en liste opp i mindre lister med n elementer i hver liste

# Verdier
n_deler = 4
liste   = [
                    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                    "k", "l", "m", "n", "o", "p", "q", "r", "s", "s",
                    "u", "v", "w", "x", "y", "z"
                ]

# Del opp listen i del-lister med n elementer i hver del-liste
def oppdeling_lister_comprehension(liste):

    # Nullstill
    del_lister = []

    # Lager del-listene med list comprehension
    del_lister = [liste[i : i + n_deler] for i in range(0, len(liste), n_deler)]

    return del_lister

# Del-lister
del_lister = oppdeling_lister_comprehension(liste)

# Print
print(f"Del-lister (hele): {del_lister}")
print("Del-lister (en og en):")
for del_liste in del_lister:
	print(f"{del_liste}")
