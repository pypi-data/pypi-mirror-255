# 🚀 programmering.no | 🤓 matematikk.as
# - Regn ut summen av de n første kubene i rekken

# Input
n = input("Antall kuber (n): ")

# Sum-funksjon for n kuber
def rekke_n_kuber_sum(n):

    # Type cast inp-str -> int
    n = int(n)

    # Formel for sum av n kuber
    sum = int((n * (n + 1) / 2)**2)

    return sum

# Summer n kuber
sum = rekke_n_kuber_sum(n)

# Print
print(f"Summen av de {n} første kubene er: {sum}")
