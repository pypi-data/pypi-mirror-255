# 🚀 programmering.no | 🤓 matematikk.as
# - Reverserer rekkefølgen til elementene i en liste
# - Hastighet reverse(): Ca. 33 ms per loop for liste m/ 100 000 000 el

# Verdier
original_liste = ["Python", "JavaScript", "Swift", "C++"]

# Kopier listen hvis du vil beholde originalen
reversert_liste = original_liste.copy()

# Reverse
reversert_liste.reverse()

# Print
print(f"Original liste  : {original_liste}")
print(f"Reversert liste : {reversert_liste}")
