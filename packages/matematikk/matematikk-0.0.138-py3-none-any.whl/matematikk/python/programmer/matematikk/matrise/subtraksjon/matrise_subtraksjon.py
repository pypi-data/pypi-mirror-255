# 🚀 programmering.no | 🤓 matematikk.as
# - Subtraher to matriser med numpy

import numpy as np

# Verdier
matrise_A = np.array([[1, 2], [3, 4]])
matrise_B = np.array([[4, 5], [6, 7]])

# Print
print("")
print("Matrise A:")
print(matrise_A)
print("")
print("Matrise B:")
print(matrise_B)

# Subtraher matrise B fra A
matrise_differanse = np.subtract(matrise_A, matrise_B)

# Print
print("")
print("Matrise A - B:")
print(matrise_differanse)
