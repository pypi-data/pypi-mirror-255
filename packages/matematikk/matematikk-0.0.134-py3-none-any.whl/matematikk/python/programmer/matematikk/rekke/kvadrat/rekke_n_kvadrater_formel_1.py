# 🚀 programmering.no | 🤓 matematikk.as
# - Regn ut summen av de n første kvadratene i rekken

# Verdier
n = 12

# Sum-funksjon for n kvadrater
def rekke_n_kvadrater_sum(n):

    # Type cast inp-str -> int
    n = int(n)

    # Formel for sum av n kvadrater
    sum = int((n * (n + 1) * (2 * n + 1)) / 6)

    return sum

# Summer n kvadrater
sum = rekke_n_kvadrater_sum(n)

# Print
print(f"Summen av de {n} første kvadratene er: {sum}")
