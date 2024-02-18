# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Torodd)
# Oppgave 2 b) Venstrehendte - P("Minst 3 venstrehendte gutter") > 0.2 

import numpy as np

# definerer tilfeldighetsgeneratoren
rng = np.random.default_rng()

def minst_tre_av(n):
    # tal simuleringar
    N = 1000

    # simulerer uttrekk av n gutar
    simulert = rng.binomial(n = n, p = 0.1, size = N)

    # tel opp gunstige utfall og finn sannsynet
    gunstige = sum(simulert >= 3)
    sannsyn = gunstige / N

    return sannsyn

n_gutar = 3

while minst_tre_av(n_gutar) < 0.20:
    n_gutar += 1

print(n_gutar)
