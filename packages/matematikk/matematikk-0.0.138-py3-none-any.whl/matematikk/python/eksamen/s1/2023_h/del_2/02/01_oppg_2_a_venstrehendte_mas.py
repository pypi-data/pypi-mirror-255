# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 2 a) Venstrehendte - Minst 25 venstrehendte gutter 

import numpy as np

# Konstanter
p_vh               = 0.1       # Sannsynligheten for at gutt er venstrehendt (vh)
k_vh               = 25        # Utvalget k med vh på skolen er 25 eller større
n_skole            = 280       # Gutter på skolen
m_skole            = 10000000  # Mulige utfall (alle skole-simuleringene)
m_skole_liste      = list()    # Liste med mulige utfall (fra simuleringene)
g_skole            = int()     # Gunstige utfall (fra simuleringene)
sannsyn_sim        = float()   # Sannsynligheten for at k gutter på skolen er vh (simulert)

# Definer tilfeldighets-generatoren (random number generator)
rng = np.random.default_rng()

# Simulering steg-for-steg
# 1. Simulerer først at det er 10 % sannsynlighet for at en gutt er vh
# 2. Denne gutten blir så enten vh eller ikke, 1 eller 0
# 3. Gjør dette 280 ganger og får f.eks. 0, 1, 0, 0, 0, 0, 1, 0, ..., 1
# 4. Teller hvor mange av de 280 som ble vh, f.eks. 27
# 5. Legger 27 i listen, [27]
# 6. Gjør dette med 10 000 000 skoler, [27, 25, 29, ..., 24]
# 7. m_skole_liste får dermed alle utfallene (fra simuleringen)
m_skole_liste = rng.binomial(n = n_skole, p = p_vh, size = m_skole)

# Tell gunstige utfall (alle skoler med 25 eller flere vh)
g_skole = sum(m_skole_liste >= k_vh)

# Definisjonen av sannsynlighet gir P(VH) = g / m, der hendelsen VH: "Gutt på skolen er vh"
sannsyn_sim = g_skole / m_skole

# Gang med 100 for prosent og rund av til f.eks. 1 eller 0 (None) desimaler
sannsyn_sim = round(sannsyn_sim * 100, 1)

# Lag svar-setninger
svar_1 = "Sannsynligheten for at det er minst 25 venstrehendte gutter på skolen er:"
svar_2 = f"P(X >= {k_vh}) = {sannsyn_sim} %"

# Print svar-setninger
print("")
print(svar_1)
print("")
print(svar_2)
