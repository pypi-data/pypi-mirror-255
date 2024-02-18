# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Torodd)
# Oppgave 2 c) Venstrehendte - Nøyaktig 3 venstrehendte elever i klassen 

import numpy as np

# definerer tilfeldighetsgeneratoren
rng = np.random.default_rng()

# tal simuleringar
N = 10000000

# trekk venstrehendte jenter og gutar for seg
jenter = rng.binomial(n=17, p=0.08, size=N)
gutar = rng.binomial(n=13, p=0.10, size=N)

# finn totalt tal venstrehendte kvart forsøk
venstrehendte = jenter + gutar

# tel opp gunstige og finn sannsynet.
gunstige = sum(venstrehendte == 3)
sannsyn = gunstige / N
print(f"P(nøyaktig tre venstrehendte) = {sannsyn:.4f}")
