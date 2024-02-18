# 🚀 programmering.no | 🤓 matematikk.as
# - Del en liste opp i mindre lister med n elementer i hver liste

import numpy as np

# Verdier
steg  = 4
liste = [
                    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                    "k", "l", "m", "n", "o", "p", "q", "r", "s", "s",
                    "u", "v", "w", "x", "y", "z"
                ]

# Del opp listen i del-lister med n elementer i hver del-liste
def oppdeling_lister_numpy(liste):

    # Del opp listen med numpy
    del_lister = np.array_split(liste, steg)

    return del_lister

# Del-lister
del_lister = oppdeling_lister_numpy(liste)

# Print
print(f"Del-lister (hele): {del_lister}")
print("Del-lister (en og en):")
for del_liste in del_lister:
	print(f"{del_liste}")
