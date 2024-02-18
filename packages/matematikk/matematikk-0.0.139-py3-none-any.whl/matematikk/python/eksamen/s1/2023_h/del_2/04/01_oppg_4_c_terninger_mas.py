# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 4 a) Sannsynlighet med 5 terninger - Bestem den største verdien av k som er slik at P(X ≥ k) > 0,8 

import random

# Konstanter
_blokk = 1 # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker

# Definerer funksjoner
def terninger_minst_2_like_av_n(n_terninger = int(),
                                svar_typ    = "desimaltall",
                                rund        = 2):

    # Definert for maksimalt 5 terninger

    # Ingen like: Gunstige
    g_ingen_like    = 1                 # (*) Starter på 1 pga. ganges med seg selv i uttrykket 6/6 * 5/6 * ...
    g_sider         = 6                 # Alle terningene har 6 sider
    terning_nr      = 1                 # Den 1. terningen av n_terninger

    # Løkken steg-for-steg: lager uttrykket 6/6 * 5/6 * 4/3 ... med alle terningene (n_terninger)
    while terning_nr <= n_terninger:    # Steg 1: Betingelsen sjekker om vi har flere terninger
        g_ingen_like    *= g_sider      # Steg 2: (***) Ganges med seg selv hver ganng g_sider minker med 1, 6/6 * 5/6 * ...
        g_sider         -= 1            # Steg 3: g_sider minker med en for hver terning
        terning_nr      += 1            # Steg 4: terning_nr øker med 1 så lenge <= n_terninger (betingelsen)

    # Ingen like: Mulige
    m_ingen_like = 6**n_terninger

    # Definisjonen av sannsynlighet gir P(2L) = g / m, der hendelsen 2L: "Minst to like"
    sannsyn_ingen_like = g_ingen_like / m_ingen_like

    # Minst 2 like (den motsatte sannsynligheten)
    sannsyn_minst_to_like = 1 - sannsyn_ingen_like

    # Velg mellom svar som desimaltall eller prosent
        if svar_typ == "prosent": sannsyn_minst_to_like *= 100
        if svar_typ == "rund"   : pass

    # Runder av svaret
    sannsyn_minst_to_like = round(sannsyn_minst_to_like, rund)

    return sannsyn_minst_to_like

def terninger_oyne_sum_fra_n_storre_enn_k(n_terninger = int(),
                                          oyne_sum    = int(),
                                          svar_typ    = "prosent",
                                          rund        = 2):

    oyne_sum_liste  = list()      # Liste med resultatet for hver simulering
    m_terning_sim   = 10000       # Antall simuleringer (antall mulige)

    # For-løkken steg-for-steg: Legger et tilfeldig antall øyne i listen for hver iterasjon
    for sim in range(m_terning_sim):                    # Iterer gjennom alle elementene i m_terning_sim
        oyne_sum_sim = 0                                # Nullstiller oyne_sum_sim før hver iterasjon
        for i in range(n_terninger):                    # Iterer gjennom antall terninger
            terning_kast = random.randint(1, 6)         # Simulert kast for hver terning gir et tall mellom 1 og 6
            oyne_sum_sim += terning_kast                # For alle terningene legges antall øyne til oyne_sum_sim
            # if oyne_sum_sim == 30: print(Yatzee!)     # Kan debugge løkken når vi f.eks. får yatzee med 6'ere

        # Legg summen av øynene i fra hver simulering i listen
        oyne_sum_liste.append(oyne_sum_sim)

    # Tell antall gunstige summer i listen
    g_terning = 0
    for terning in oyne_sum_liste:
        if terning > oyne_sum:
            g_terning += 1

    # Definisjonen av sannsynlighet gir P(X >= 20) = g / m, der hendelsen X: "Summen av øyne er større enn 20"
    sannsyn_terning = g_terning / m_terning_sim # print(sannsyn_terning) # Debug sannsynligheten når løkken kjører

    # Velg mellom svar som desimaltall eller prosent
        if svar_typ == "prosent": sannsyn_terning *= 100
        if svar_typ == "rund"   : pass

    # Runder av svaret
    sannsyn_terning = round(sannsyn_terning, rund)

    return sannsyn_terning

def terninger_k_oyne_sum_fra_n_storre_enn_p(n_terninger  = int(),
                                            oyne_sum     = int(),
                                            svar_typ     = "desimaltall",
                                            rund         = 2,
                                            sannsyn_gitt = 0.75):

    oyne_sum_start = oyne_sum

    while terninger_oyne_sum_fra_n_storre_enn_k(n_terninger = n_terninger,
                                                oyne_sum    = oyne_sum_start,
                                                svar_typ    = svar_typ,
                                                rund        = rund)     < sannsyn_gitt:
        oyne_sum_start -= 1

    return oyne_sum_start

# a) Sannsynligheten for minst 2 av 5 terningene er like
if _blokk == 1:

    # Regner ut vha. den motsatte sannsynligheten
    sannsyn_minst_to_like = terninger_minst_2_like_av_n(n_terninger = 5,
                                                        svar_typ    = "prosent",
                                                        rund        = 2)

    # Print svar-setninger
    svar_a_0 = f"Oppg a)"
    svar_a_1 = f"- Sannsynligheten for minst 2 like av 5 terninger er {sannsyn_minst_to_like} %"
    print("")
    print(svar_a_0)
    print(svar_a_1)

# b) Bruk programmering til å bestemme P(X > 20)
if _blokk == 1:

    sannsyn_terning = terninger_oyne_sum_fra_n_storre_enn_k(n_terninger = 5,
                                                            svar_typ    = "prosent",
                                                            rund        = 2)

    # Print svar-setninger
    svar_b_0 = f"Oppg b)"
    svar_b_1 = f"- P(x > 20) = {sannsyn_terning} %"
    print("")
    print(svar_b_0)
    print(svar_b_1)

# c) Bestem den største verdien av k som er slik at P(X ≥ k) > 0,8
if _blokk == 1:

    oyne_sum = terninger_k_oyne_sum_fra_n_storre_enn_p(n_terninger  = 5,
                                                       oyne_sum     = 30,
                                                       svar_typ     = "desimaltall",
                                                       rund         = 2,
                                                       sannsyn_gitt = 0.8)

    # Print svar-setninger
    svar_c_0 = f"Oppg c)"
    svar_c_1 = f"- Den største verdien k kan ha slik at P(X ≥ k) > 0,8 er {oyne_sum} (øyne)"
    print("")
    print(svar_c_0)
    print(svar_c_1)
