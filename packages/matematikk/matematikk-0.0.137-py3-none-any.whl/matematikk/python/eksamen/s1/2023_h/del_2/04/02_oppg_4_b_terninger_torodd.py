# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Torodd)
# Oppgave 4 a) Sannsynlighet med 5 terninger - Bruk programmering til å bestemme P(X > 20) 

import numpy as np

# definerer tilfeldighetsgeneratoren
rng = np.random.default_rng()

# tal simuleringar
N = 10000000

# triller 5 terningar N gongar
terningar = rng.integers(1, 7, size=(5, N))

# finn summen av kvart forsøk
fem_kast = terningar.sum(axis=0)

# tel opp kor mange gongar summen vart større enn 20
gunstige = sum(fem_kast > 20)

# finn sannsynet og skriv ut
p = gunstige / N

print(f"P(X > 20) = {p:.4f}")
