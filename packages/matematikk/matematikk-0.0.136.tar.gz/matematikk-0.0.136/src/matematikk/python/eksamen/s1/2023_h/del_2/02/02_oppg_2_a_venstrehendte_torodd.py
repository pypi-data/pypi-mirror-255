# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Torodd)
# Oppgave 2 a) Venstrehendte - Minst 25 venstrehendte gutter 

import numpy as np

# definerer tilfeldighetsgeneratoren
rng = np.random.default_rng()

# tal simuleringar
N = 10000000

# simulerer uttrekk av 280 gutar
simulert = rng.binomial(n = 280, p = 0.1, size = N)

# tel opp gunstige utfall og finn sannsynet
gunstige = sum(simulert >= 25)
sannsyn = gunstige / N

print(f"P(X>=25) = {sannsyn:.4f}")
