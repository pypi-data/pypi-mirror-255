# 🚀 programmering.no | 🤓 matematikk.as
# - Transponer matrise med numpy

import numpy

# Matrise (datatype-format)
matrise = [[1, 2, 3], [4, 5, 6]]

# Print
print("")
print("Matrise (datatype-format):")
print(matrise)

# Matrise (matematisk format)
matrise = numpy.array(matrise)

# Print
print("")
print("Matrise (matematisk format):")
print(matrise)

# Print
print("")
print("Transponert matrise (matematisk format):")
print(matrise.T)
