# 🚀 programmering.no | 🤓 matematikk.as
# - Kopier liste med slice operator (:)

# Verdier
liste = ["A", "B", "C"]

# Funksjon som kopierer en liste med slice operator
def copy_liste_slice_operator(liste):

    # Slice operator
    liste_copy = liste[:]

    return liste_copy

# Kopiert liste
liste_copy = copy_liste_slice_operator(liste)

# Print
print(f"Original liste : {liste}")
print(f"Kopiert liste  : {liste_copy}")
