# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 5 a) Sannsynlighet med 5 terninger - Sannsynligheten for minst 2 av 5 terningene er like 

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

# a) Sannsynligheten for minst 2 av 5 terningene er like
if _blokk == 1:

    sannsyn_minst_to_like = terninger_minst_2_like_av_n(n_terninger = 5,
                                                        svar_typ    = "prosent",
                                                        rund        = 2)

    # Print svar-setninger
    svar_a_0 = f"Oppg a)"
    svar_a_1 = f"- Sannsynligheten for minst 2 like av 5 terninger er {sannsyn_minst_to_like} %"
    print("")
    print(svar_a_0)
    print(svar_a_1)
