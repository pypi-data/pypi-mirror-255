# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Torodd)
# Oppgave 6 a) Tredjegradsfunksjon - Påstand 1: Grafen f har minst ett ekstremalpunkt 

from sympy import symbols, diff, solve

# Dersom grafen til f har et vendepunkt for x = 3 er f'(1) = f'(5)

# Dersom grafen til f har vendepunkt for x = 3 vil det si at f''(3) = 0
# Siden f''(x) er den deriverte til f'(x) vet vi da at f'(x) har
# ekstremalpunkt for x = 3. Siden f'(x) er et tredjegradspolynom er f'(x)
# et andregradspolynom.
# Andregradspolynomer er symmetriske om ekstremalpunktet sitt.
# Siden x = 1 og x = 5 ligger like langt fra x = 3 vil f'(1) = f'(5)
#
# Påstanden er sann
