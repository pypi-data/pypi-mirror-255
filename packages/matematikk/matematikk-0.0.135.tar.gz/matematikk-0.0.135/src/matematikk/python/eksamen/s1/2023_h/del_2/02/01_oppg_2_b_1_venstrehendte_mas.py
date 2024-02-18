# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 2 b) Venstrehendte - P("Minst 3 venstrehendte gutter") > 0.2 
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

import numpy as np # lala

# Konstanter
_blokk             = 1         # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker
p_vh               = 0.1       # Sannsynligheten for at gutt er venstrehendt (vh)
k_vh               = 3         # Utvalget k med vh i klassen er 3 eller større
n_klasse           = 1         # Gutter i klassen (starter på 1 eller k_vh)
m_klasse           = 1000      # Mulige utfall (alle klasse-simuleringene)
m_klasse_liste     = list()    # Liste med mulige utfall (fra simuleringene)
g_klasse           = int()     # Gunstige utfall (fra simuleringene)
sannsyn_gitt       = 0.2       # Sannsynligheten for at k gutter i klassen er vh (gitt i oppg)
sannsyn_sim        = float()   # Sannsynligheten for at k gutter i klassen er vh (simulert)

# Definer tilfeldighets-generatoren (random number generator)
rng = np.random.default_rng()

# Definerer funksjoner
def sannsynlighet_for_minst_3_vh(n_klasse):

    # Regner ut sannsynligheten for k antall vh i en klasse med n_klasse gutter (se while-løkke)

    # Simulering steg-for-steg
    if _blokk == -1:
        # 1. En endring fra oppg a) er at antall gutter starter på 1 og kan øke
        # 2. Etter første simulering sammenlignes sannsynligheten med 20 %
        # 3. Hvis den er mindre enn 20 % øker klassen med 1 gutt
        # 4. Da gjøres simuleringen om igjen med den nye verdien for n_klasse
        # 5. Denne gutten blir så enten vh eller ikke, 1 eller 0
        # 6. Gjør dette n_klasse ganger og får f.eks. 0, 0, 1, 0 og 1 (hvis n_klasse er 5)
        # 7. Teller hvor mange av de n_klasse som ble vh, f.eks. 2
        # 8. Legger 2 i listen, [2]
        # 9. Gjør dette med 1000 klasser, [2, 0, 0, ..., 1]
        # 10. m_skole_liste får dermed alle utfallene (fra simuleringen)
        pass
    m_klasse_liste = rng.binomial(n = n_klasse, p = p_vh, size = m_klasse)

    # Tell gunstige utfall (alle klasser med 3 eller flere vh)
    g_klasse = sum(m_klasse_liste >= k_vh)

    # Definisjonen av sannsynlighet gir P(VH) = g / m, der hendelsen VH: "Gutt på skolen er vh"
    sannsyn_sim = g_klasse / m_klasse

    # Returnerer sannsynligheten tilbake til while-løkken
    return sannsyn_sim

# While-løkke steg-for-steg
if _blokk == -1:
    # 1. Løkken kaller først sannsynlighet_for_minst_3_vh() med
    #    argumentet n_klasse (nåværende gutter i klassen)
    # 2. sannsynlighet_for_minst_3_vh() returnerer sannsyn_sim (sannsynligheten
    #    for vh i en klasse med n_klasse gutter, se simulerings-steg)
    # 3. Hvis sannsyn_sim < 20 % (betingelsen), så øker n_klasse med 1
    # 4. Isåfall kaller løkken sannsynlighet_for_minst_3_vh() om igjen
    # 5. Løkken vil da repeterer dette til sannsyn_sim >= 20 % (betingelsen brytes)
    pass

# Regner ut sannsynligheten for k antall vh i en klasse med n_klasse gutter (se while-løkke)
while sannsynlighet_for_minst_3_vh(n_klasse) < sannsyn_gitt:

    # n_klasse øker med 1 hver gang løkken (og simuleringen) kjøres
    n_klasse += 1

# Lag svar-setninger
svar_1 = f"Når det skal være større enn 20 % sannsynlighet for at"
svar_2 = f"minst {k_vh} gutter i klassen er venstrehendte,"
svar_3 = f"så må det være minst {n_klasse} gutter i klassen"

# Print svar-setninger
print("")
print(svar_1)
print(svar_2)
print(svar_3)
