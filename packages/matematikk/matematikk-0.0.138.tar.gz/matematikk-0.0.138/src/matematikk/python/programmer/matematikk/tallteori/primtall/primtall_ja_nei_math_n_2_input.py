# 🚀 programmering.no | 🤓 matematikk.as
# - Se om tallet er et primtall

from math import sqrt

# Input
n = input("Se om tallet er primtall: ")

# Funksjon for å se om tallet er primtall
def er_primtall_sqrt(n):

    # Type cast inp-str -> int
    n = int(n)

    # Alle primtall er større enn 1
    if n > 1:

        # Iterer fra 2 til n / 2 + 1 (medium tempo)
        for i in range(2, int(sqrt(n)) + 1):

            # n er ikke et primtall hvis det er delelig med i
            if n % i == 0:
                print(f"Er {n} et primtall? Nei")
                break

        # Hvis for-løkken fullføres uten break
        else: print(f"Er {n} et primtall? Ja")

    # Hvis tallet ikke er større enn 1 er det ikke primtall
    else: print(f"Er {n} et primtall? Nei")

# Primtall eller ikke
er_primtall_sqrt(n)
