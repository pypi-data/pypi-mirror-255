# 🚀 programmering.no | 🤓 matematikk.as
# - Kopier liste med deepcopy()

from copy import deepcopy

# Verdier
liste_1 = [{"Navn": "Clark"}]
liste_2 = [{"Navn": "Clark"}]

# Kopier liste med copy()
liste_copy_1 = liste_1.copy()

# Endre feltet til en ny verdi
liste_1[0]["Navn"] = "Superman"

# Begge listene ble endret (er i praksis samme liste)
print(f"Liste 1 - copy()")
print(f"Original liste : {liste_1}")
print(f"Kopiert liste  : {liste_copy_1}")

# Kopier liste med deepcopy()
liste_copy_2 = deepcopy(liste_2)

# Endre feltet til en ny verdi
liste_2[0]["Navn"] = "Superman"

# Kun den ene listen ble endret (er to uavhengige lister)
print(f"Liste 2 - deepcopy()")
print(f"Original liste : {liste_2}")
print(f"Kopiert liste  : {liste_copy_2}")
