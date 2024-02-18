# 🚀 programmering.no | 🤓 matematikk.as
# - Teller hvor mange utvalgte elementer det er i en liste

# Verdier
liste    = ["A", "B", "B", "C", "F"]
karakter = "B"

# Antall
antall = liste.count("B")

# Print
print(f"Liste: {liste}")
if antall > 0:
    print(f"{antall} elev(er) fikk karakter {karakter}")
else:
	print("Ingen elever fikk karakter {karakter}")
