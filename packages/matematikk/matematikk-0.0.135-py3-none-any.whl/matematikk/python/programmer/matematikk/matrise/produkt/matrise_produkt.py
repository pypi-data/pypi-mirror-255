# 🚀 programmering.no | 🤓 matematikk.as
# - Regn ut produktet av to matriser med numpy

import numpy as np

# Matrise A (3x3)
matrise_A = np.array(
                    [[12, 7, 3],
                    [ 4,  5, 6],
                    [ 7,  8, 9]])

# Matrise B (3x4)
matrise_B = np.array(
                    [[5, 8, 1, 2],
                    [ 6, 7, 3, 0],
                    [ 4, 5, 9, 1]])

# Produktet av A og B (3x3 * 3x4 => 3x4)
matrise_produkt = np.dot(matrise_A, matrise_B)

# Print radene i produktet (3x4)
for r in matrise_produkt:

    # Rad
	print(r)
