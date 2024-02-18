# 🚀 programmering.no | 🤓 matematikk.as
# - Kopier liste med extend()

# Verdier
liste = ["A", "B", "C"]

# Funksjon som kopierer en liste med extend
def copy_liste_extend(liste):

    # Nullstill
    liste_copy = list()

    # Extend
    liste_copy.extend(liste)

    return liste_copy

# Kopiert liste
liste_copy = copy_liste_extend(liste)

# Print
print(f"Original liste : {liste}")
print(f"Kopiert liste  : {liste_copy}")
