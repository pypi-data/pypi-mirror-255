# 🚀 programmering.no | 🤓 matematikk.as
# - Del en liste opp i mindre lister med n elementer i hver liste

# Verdier
liste   = [
                    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                    "k", "l", "m", "n", "o", "p", "q", "r", "s", "s",
                    "u", "v", "w", "x", "y", "z"
                ]
n_deler = 3

# Del opp listen i del-lister med n elementer i hver del-liste
def oppdeling_lister(liste, n):

	# Itererer gjennom listen
	for i in range(0, len(liste), n):

		# Yield returner del-lister uten å bryte ut av loopen
		yield liste[i : i + n]

# Del-lister
del_lister = list(oppdeling_lister(liste, int(n_deler)))

# Print
print(f"Del-lister (hele): {del_lister}")
print("Del-lister (en og en):")
for del_liste in del_lister:
	print(f"{del_liste}")
