# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 2 c) Venstrehendte - Nøyaktig 3 venstrehendte elever i klassen 

import numpy as np

# Konstanter
p_vh_gutter                = 0.1       # Sannsynligheten for at gutt er venstrehendt (vh)
p_vh_jenter                = 0.08      # Sannsynligheten for at jente er vh
k_vh_elever                = 3         # Utvalget k med vh elever i klassen er nøyaktig 3
n_gutter                   = 13        # Gutter i klassen
n_jenter                   = 17        # Jenter i klassen
m_klasse                   = 10000000  # Mulige utfall (alle klasse-simuleringene)
m_gutter_klasse_liste      = list()    # Liste med mulige utfall (fra gutte-simuleringene)
m_jenter_klasse_liste      = list()    # Liste med mulige utfall (fra jente-simuleringene)
m_elever_klasse_liste      = list()    # Liste med mulige utfall (fra de kombinerte elev-simuleringene, se stegene nedenfor)
g_klasse_elever            = int()     # Gunstige utfall (fra simuleringene)
sannsyn_sim                = float()   # Sannsynligheten for at 3 elever i klassen er vh (simulert)

# Innstillinger
_blokk                     = 1         # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker

# Definer tilfeldighets-generatoren (random number generator)
rng = np.random.default_rng()

if _blokk == -1:
    # Simulering steg-for-steg
    # 1. I denne simuleringen kan vi først tenke at vi har to adskilte
    #    gutte- og jente-klasser som sitter i hvert sitt nabo-rom
    # 2. Deretter gjør vi den samme simuleringen med guttene som i a) og b) oppg
    # 3. Simulerer at det er 10 % sannsynlighet for at en gutt er vh
    # 4. Denne gutten blir så enten vh eller ikke, 1 eller 0
    # 5. Gjør dette 13 ganger og får f.eks. 0, 1, 0, 0, 0, 0, 1, 0, ..., 0
    # 6. Teller hvor mange av de 13 guttene som ble vh, f.eks. 2
    # 7. Legger 2 i listen, [2]
    # 8. Gjør dette med 10 000 000 gutte-klasser, m_gutter_klasse_liste = [2, 0, 1, ..., 0]
    # 9. Gjentar de samme stegene med jentene, men med 8 % sannsynlighet for at en jente er vh 
    # 10. Får f.eks. m_jenter_klasse_liste = [1, 0, 1, ..., 1] fra jente-simuleringen
    # 11. Nå kan vi tenke oss at denne veggen mellom dem egentlig aldri fantes, og at de
    #     hele tiden satt i samme store klasserom
    # 12. De 10 000 000 simuleringene vi gjorde ble altså gjort som en kombinasjon (simulering nr 1
    #     for guttene er også simulering nr 1 for jentene)
    # 13. Vi kan derfor plusse de to listene element-vis slik (pluss sammen kolonnene)
    #         m_gutter_klasse_liste = [2, 0, 1, ..., 0]
    #       + m_jenter_klasse_liste = [1, 0, 1, ..., 1]
    #       = m_elever_klasse_liste = [3, 0, 2, ..., 1] <-- 10 000 000 kombinerte elev-simuleringer
    # 14. Dette er grunnen til at antall mulige utfall blir 10 000 000
    # 15. Deretter finner vi antall gunstige utfall og sannsynligheten på samme måte som i a) og b) oppg
    pass
m_gutter_klasse_liste = rng.binomial(n = n_gutter, p = p_vh_gutter, size = m_klasse)
m_jenter_klasse_liste = rng.binomial(n = n_jenter, p = p_vh_jenter, size = m_klasse)

# # Plusser sammen de to listene for å få en kombinert elev-liste med 10 000 000 mulige utfall
m_elever_klasse_liste = m_gutter_klasse_liste + m_jenter_klasse_liste

# Tell gunstige utfall (alle kobinerte klasser med nøyaktig 3 vh)
g_klasse_elever = sum(m_elever_klasse_liste == k_vh_elever)

# Definisjonen av sannsynlighet gir P(VH) = g / m, der hendelsen VH: "Elev i klassen er vh"
sannsyn_sim = g_klasse_elever / m_klasse

# Gang med 100 for prosent og rund av til f.eks. 1 eller 0 (None) desimaler
sannsyn_sim = round(sannsyn_sim * 100, 2)

# Lag svar-setninger
svar_1 = "Sannsynligheten for at det er nøyaktig 3 venstrehendte elever i klassen er:"
svar_2 = f"P(X >= {k_vh_elever}) = {sannsyn_sim} %"

# Print svar-setninger
print("")
print(svar_1)
print("")
print(svar_2)
