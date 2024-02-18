# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Torodd)
# Oppgave 4 a) Sannsynlighet med 5 terninger - Bestem den største verdien av k som er slik at P(X ≥ k) > 0,8 

import numpy as np
rng = np.random.default_rng()

def sum_større_eller_lik(k):
    N = 1000000
    terningar = rng.integers(1, 7, size = (5, N))
    fem_kast = terningar.sum(axis=0)
    gunstige = sum(fem_kast >= k)
    p = gunstige / N
    return p

k = 30

while sum_større_eller_lik(k) < 0.8:
    k = k - 1

print(k)
