# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 2 b) Venstrehendte - Sannsynlighets-relasjoner - P(X <velg relasjon> k) > sannsyn_gitt 
# - Oppgave-teksten har antageligvis en feil (som dette programmet fikser)
# - Feilen er at ordet "MINST" ikke er tatt med
#   - "Hvor mange gutter må det (MINST) være i en klasse dersom
#      sannsynligheten for at minst tre av guttene er
#      venstrehendte, skal være større enn 20 prosent?"
# - Grunnen til at dette blir feil, er at man uten ordet "MINST" bare kunne sagt
#   et veldig stort antall gutter (f.eks. 1000 eller "uendelig")
# - Fordi hvis man kun spør om "hvor mange gutter det må være for at
#   denne sannsynligheten skal være større enn 20 %", så vil jo denne
#   sannsynligheten selvfølgelig raskt bli mye større enn 20 % når det er veldig
#   mange gutter i klassen, og det kun er snakk om 3 venstrehendte der
# - Derfor er det fornuftig å heller finne det minste antallet gutter i klassen
#   (grensetilfelle), som gjør at denne sannsynligheten akkurat blir større enn 20 %

import numpy as np

# Konstanter
_blokk             = 0         # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker
p_vh               = 0.1       # Sannsynligheten for at gutt er venstrehendt (vh)
k_vh               = 3         # Utvalget k med vh i klassen
n_klasse           = 1         # Gutter i klassen (starter på 1 eller k_vh)
m_klasse           = 1000      # Mulige utfall (alle klasse-simuleringene)
m_klasse_liste     = list()    # Liste med mulige utfall (fra simuleringene)
g_klasse           = int()     # Gunstige utfall (fra simuleringene)
sannsyn_gitt       = 0.2       # Sannsynligheten for at k gutter i klassen er vh (gitt i oppg)
sannsyn_gitt_rel   = ">="      # Velg relasjon for sannsyn_gitt ("==", ">=", ">", "<=", "<")
sannsyn_sim        = float()   # Sannsynligheten for at k gutter i klassen er vh (simulert)
n_svar_rel         = str()     # Relasjon for antall vh i svaret (regnes ut i koden)

# Definer tilfeldighets-generatoren (random number generator)
rng = np.random.default_rng()

# Regner ut sannsynligheten for k antall vh i en klasse med n_klasse gutter (se while-løkke)
def sannsynlighet_for(n_klasse, s_rel = sannsyn_gitt_rel):

    # Simulering steg-for-steg
    if _blokk == 1:
        # 1. n_klasse starter på 1 og kan øke
        # 2. Etter første simulering sammenlignes sannsyn_sim med sannsyn_gitt
        # 3. Hvis sannsyn_sim < sannsyn_gitt øker n_klasse med 1
        # 4. Da gjøres simuleringen om igjen med den nye verdien for n_klasse
        # 5. Simulerer at det er p_vh sannsynlighet for at en gutt er vh
        # 6. Denne gutten blir så enten vh eller ikke, 1 eller 0
        # 7. Gjør dette n_klasse ganger og får f.eks. 0, 0, 1, 0 og 1 (hvis n_klasse er 5)
        # 8. Teller hvor mange av de n_klasse som ble vh, f.eks. 2
        # 9. Legger 2 i listen, [2]
        # 10. Gjør dette med m_klasse klasser, [2, 0, 0, ..., 1]
        # 11. m_skole_liste får dermed alle utfallene (fra simuleringen)
        pass
    m_klasse_liste = rng.binomial(n = n_klasse, p = p_vh, size = m_klasse)

    # Tell gunstige utfall og velg riktig relasjon til svaret
    if s_rel == "==":                 g_klasse = sum(m_klasse_liste == k_vh); n_svar_rel = "nøyaktig"
    if s_rel == ">=" or s_rel == ">": g_klasse = sum(m_klasse_liste >= k_vh); n_svar_rel = "minst"
    if s_rel == "<=" or s_rel == "<": g_klasse = sum(m_klasse_liste <= k_vh); n_svar_rel = "maksimalt"

    # Definisjonen av sannsynlighet gir P(VH) = g / m, der hendelsen VH: "Gutt på skolen er vh"
    sannsyn_sim = g_klasse / m_klasse

    # Returnerer en liste med sannsynlighet og relasjon
    return [sannsyn_sim, n_svar_rel]

# While-løkke steg-for-steg
if _blokk == 1:
    # 1. En endring fra 02_oppg_2_b er at betingelsen i løkken nå er to-delt
    #    1.1 For ">=", ">", "==": sannsyn_sim går fra 0 opp til sannsyn_gitt
    #    1.2 For "<=", "<"      : sannsyn_sim går fra 1 ned til sannsyn_sim
    # 2. Løkken kaller først f_sannsynlighet_for() med to argumenter
    #    2.1. sannsyn_gitt_rel (valgfri/har default): ("==", ">=", ">", "<=", "<")
    #    2.2. n_klasse (obligatorisk)               : nåværende gutter i klassen
    # 3. sannsynlighet_for() returnerer to variabler (i en liste)
    #    3.1 sannsynlighet_for()[0]: sannsyn_sim
    #    3.2 sannsynlighet_for()[1]: svar_rel (relasjonen i svaret)
    # 4. Hvis f.eks. sannsyn_sim < sannsyn_gitt (betingelsen), så øker n_gruppe med 1
    # 5. Isåfall kaller løkken sannsynlighet_for() om igjen
    # 6. Løkken vil da repeterer dette til sannsyn_sim >= sannsyn_gitt (betingelsen brytes)
    pass
while   (((sannsyn_gitt_rel == ">=" or sannsyn_gitt_rel == ">" or sannsyn_gitt_rel == "==") and
            (sannsynlighet_for(n_klasse, sannsyn_gitt_rel)[0] < sannsyn_gitt))
    or   ((sannsyn_gitt_rel == "<=" or sannsyn_gitt_rel == "<") and
            (sannsynlighet_for(n_klasse, sannsyn_gitt_rel)[0] > sannsyn_gitt))):

    # n_klasse øker med 1 hver gang løkken (og simuleringen) kjøres
    n_klasse += 1

# Kaller sannsynlighet_for() en ekstra gang med forrige klasse_n for å få relasjonen til svaret
n_svar_rel = sannsynlighet_for(n_klasse - 1, sannsyn_gitt_rel)[1]

# Gang med 100 for prosent og rund av til f.eks. 1 eller 0 (None) desimaler
sannsyn_gitt = round(sannsyn_gitt * 100, None)

# Lag svar-setninger
svar_1 = f"Når det skal være større enn {sannsyn_gitt} % sannsynlighet for at"
svar_2 = f"{n_svar_rel} {k_vh} gutter i klassen er venstrehendte,"
svar_3 = f"så må det være {n_svar_rel} {n_klasse} gutter i klassen"

# Print svar-setninger
print("")
print(svar_1)
print(svar_2)
print(svar_3)
