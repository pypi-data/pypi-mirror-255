# 🚀 programmering.no | 🤓 matematikk.as
# - Regn ut summen av de n første kvadratene i rekken

# Input
n = input("Antall kvadrater (n): ")

# Sum-funksjon for n kvadrater
def rekke_n_kvadrater_sum(n):

    # Nullstill
    sum = 0

    # For-løkken oppdaterer sum for hver iterasjon
    for i in range(int(n) + 1):
        sum = sum + pow(i, 2)

    return sum

# Summer n kvadrater
sum = rekke_n_kvadrater_sum(n)

# Print
print(f"Summen av de {n} første kvadratene er: {sum}")
