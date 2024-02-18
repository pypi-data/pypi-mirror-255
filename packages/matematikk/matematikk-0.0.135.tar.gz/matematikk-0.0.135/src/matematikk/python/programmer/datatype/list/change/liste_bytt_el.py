# 🚀 programmering.no | 🤓 matematikk.as
# - Bytt første og siste element i en liste

# Verdier
liste = [1, 2, 3, 4, 5]

# Print
print(f"Liste: {liste}")

# Kopier det første el til en midlertidig tmp-variabel
el_tmp = liste[0]

# Bytt det første el i listen med det siste
liste[0] = liste[-1]

# Bytt det siste el med tmp-variabelen
liste[-1] = el_tmp

# Print
print(f"Liste: {liste}")
