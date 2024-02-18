# 🚀 programmering.no | 🤓 matematikk.as
# - Se om intervallet har fibonacci-tall
# - Fibonacci-rekken genereres av formelen F(n) = F(n-2) + F(n-1)
# - De første fibonacci-tallene er 0, 1, 1, 2, 3, 5, 8, 13, 21, ..., n
# - F(n) er også et fibonacci-tall hvis 5 * n^2 ± 4 er et kvadrat-tall

import math

# Verdier
min = 1
max = 5

# Funksjon for å se om n er et kvadrat-tall
def er_kvadrattall(n = int()):

    # Ta kvadrat-roten av n
    rot = math.sqrt(float(n))

    # Rund av roten til et heltall
    rot_heltall = int(rot)

    # Lag et nytt kvadrat-tall av de to røttene
    kvadrat = rot_heltall * rot_heltall

    # Hvis det nye kvadrat-tallet er lik n => n er et kvadrat-tall
    if kvadrat == n: return True

    # Hvis det nye kvadrat-tallet ikke er lik n => n er ikke et kvadrat-tall
    if kvadrat != n: return False

# Funksjon for å se om tallet er et fibonacci-tall
def er_fibonacci_tall(n):

    # Ikke definert
    if n < 1: return False

    # Tallet n er et fibonacci-tall hvis 5 * n^2 ± 4 er et kvadrattall
    er_fib_true_1 = er_kvadrattall(5 * int(n)**2 + 4)
    er_fib_true_2 = er_kvadrattall(5 * int(n)**2 - 4)

    # Ett eller begge er fibonacci-tall
    if er_fib_true_1 or er_fib_true_2: return True

    # Ingen er fibonacci-tall
    else: return False

# Funksjon for å printe fibonacci-tallene
def er_fibonacci_tall_print(n):

    # Print
    if er_fibonacci_tall(n) == True: print(f"Er {n} et fibonacci-tall? Ja")
    else:                            print(f"Er {n} et fibonacci-tall? Nei")

# Funksjon for å se om intervallet har fibonacci-tall
def er_fibonacci_tall_intervall(min, max):

    # Itererer gjennom intervallet
    for n in range(int(min), int(max) + 1):
        er_fibonacci_tall_print(n)

# Fibonacci-tall eller ikke
er_fibonacci_tall_intervall(min, max)
