# 🚀 programmering.no | 🤓 matematikk.as
# - Regn ut summen av de n første kubene i rekken

# Verdier
n = 4

# Sum-funksjon for n kuber
def rekke_n_kuber_sum(n):

    # Nullstill
    sum = 0

    # For-løkken oppdaterer sum for hver iterasjon
    for i in range(int(n) + 1):
        sum = sum + pow(i, 3)

    return sum

# Summer n kuber
sum = rekke_n_kuber_sum(n)

# Print
print(f"Summen av de: {n} første kubene er {sum}")
