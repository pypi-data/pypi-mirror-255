# 🚀 programmering.no | 🤓 matematikk.as
# Sannsynlighet (Matematikk AS)
# Mal - Sannsynlighets-relasjoner - P(X <velg relasjon> k) > sannsyn_gitt 
# - Programmet tar sikte på å kunne løse alle sannsynlighets-oppgaver som
#   - Er på prøver på VGS-nivå, del 2 (med hjelpemidler)
#   - Bruker binomisk sannsynlighets-modell/-fordeling
#     1. To utfall (enten eller)
#     2. Uavhengige delforsøk (utfallet for den ene påvirker ikke det andre)
#     3. Lik sannsynlighet for alle delforsøkene
#   - Finner sannsynlighetene gjennom simulering av mange delforsøk
#   - Veksler mellom de ulike relasjonene (==, >=, >, <= og <)
#   - Vil ofte stå på formen "Hvor mange objekter n må det være i en gruppe,
#     når det skal være en gitt sannsynlighet for at det i den samme gruppen er
#     k objekter med en binomisk fordelt egenskap"
#   - Eksempel: "Hvor mange svaner må det være i en dam for at det med minst 42 %
#     sannsynlighet skal være flere enn 4 svarte svaner i den samme dammen"
# - Skriv inn verdier og relasjoner fra oppgaven under "# Konstanter",
#   og få riktig svar som ferdige setninger i en tabell
#   - Programmet finner både n og relasjonen til n, f.eks. "minst 109"
#   - Du kan få det samme svaret som i eks. ved å bruke seed/"frø" = 1337 i
#     tilfeldighets-generatoren, np.random.default_rng(1337)
#   - Simuleringen bruker tilfeldige tall, så seed kan brukes for å få nøyaktig
#     samme sannsynlighet hver gang (de "tilfeldige" tallene i simuleringen er de samme)
#
#   ┌───────────────────────────────────────────────────┐
#   │ Dammen må ha minst 109 svaner                     │
#   ├───────────────────────────────────────────────────┤
#   │ ✓ Det skal være minst 4 svarte svaner             │
#   │ ✓ Sannsynligheten for utfallet er større enn 42 % │
#   └───────────────────────────────────────────────────┘
#
# - Tabellen nedenfor viser hvilke synonymer som kan brukes som relasjoner
#
#   ┌──────┬──────────┬──────────────────┬────────┬──────────────────┬────────┐
#   │ k    │ ==       │ >=               │ >      │ <=               │ <      │
#   │ k er │ nøyaktig │ minst            │ flere  │ maksimalt        │ mindre │
#   │      │ akkurat  │ større eller lik │ større │ mindre eller lik │ færre  │
#   │      │ lik      │                  │ mer    │                  │        │
#   └──────┴──────────┴──────────────────┴────────┴──────────────────┴────────┘

import numpy as np

# Konstanter
gruppe_navn      = "Dammen"                # Gruppens navn
obj              = "svaner"                # Alle i gruppen er samme obj
obj_p            = "svarte svaner"         # Et obj kan være obj_p eller ikke
p                = 0.03                    # Sannsynligheten for at ett obj er obj_p
k                = 4                       # Utvalget k med obj_p i gruppen
k_rel            = "minst"                 # Velg relasjon for k
n_gruppe         = 1                       # Antall obj i gruppen (starter på 1)
n_svar_rel       = str()                   # Relasjon for antall obj_p i svaret (regnes ut i koden)
n_svar_liste     = list()                  # Liste med svar-setningene
m_gruppe         = 1000                    # Mulige utfall (alle gruppe-simuleringene)
m_gruppe_liste   = list()                  # Liste med mulige utfall (fra simuleringene)
g_gruppe         = int()                   # Gunstige utfall (fra simuleringene)
sannsyn_gitt     = 0.42                    # Sannsynligheten for at k antall obj_p er i gruppen (gitt i oppg)
sannsyn_gitt_rel = "større"                # Velg relasjon for sannsyn_gitt
sannsyn_sim      = int()                   # Sannsynligheten for at k antall obj_p i gruppen (simulert)
rng              = np.random.default_rng() # Definer tilfeldighets-generatoren (random number generator)

# Innstillinger
_blokk           = 1                       # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker
_debug_while     = 1                       # 0: Av, 1: Debug while-løkke (f.eks. se sannsyn_sim-verdiene, om løkken henger)
_debug_matriks   = 0                       # 0: Av, 1: Debug riktig sannsynlighets-blokk i matriks (f.eks. trim bort ubrukte blokker, finn bugs)

# Debug while-løkke og matriks
def d(_d_s, nr):
    if _d_s == 1: print(nr)
def d_w(_d_w, sannsyn_sim):
    if _d_w == 1: print("... sannsyn_sim ::", sannsyn_sim)

# Gjør alle synonymer om til samme ord (som returneres og brukes videre internt i koden)
def synonymer(rel):
    if rel == "==" or rel == "nøyaktig"  or rel == "akkurat"          or rel == "lik": return "nøyaktig"
    if rel == ">=" or rel == "minst"     or rel == "større eller lik":                 return "minst"
    if rel == ">"  or rel == "flere"     or rel == "større"           or rel == "mer": return "flere"
    if rel == "<=" or rel == "maksimalt" or rel == "mindre eller lik":                 return "maksimalt"
    if rel == "<"  or rel == "mindre"    or rel == "færre":                            return "mindre"
    print("Feilmelding: Relasjonen er skrevet feil (er ikke i tabellen)"); return "Ikke definert"

# Formater svar-tabellen
def tabell_format(n_svar_liste):

    # Formateringen lager lange nok streker og mellomrom
    svar_lengde     = 0
    svar_liste_ny   = []

    # Iterer gjennom listen og oppdater strek og svar-lengden hvis svaret er lengre enn forrige
    for svar in n_svar_liste:
        if len(svar) > svar_lengde:
            strek = ""
            for _ in svar:
                strek += "─"
                svar_lengde = len(strek)

    # Regn ut tilsvarende lengde på mellomrommene ("padding") frem til høyre strek-marg
    def space(svar):
        space_diff = len(strek) - len(svar)
        sp = ""
        for _ in range(space_diff): sp += " "
        return sp

    # Legg de formaterte svar-setningene i en ny liste som returneres
    svar_liste_ny.append("┌─" + strek                                    + "─┐")
    svar_liste_ny.append("│ " + n_svar_liste[0] + space(n_svar_liste[0]) + " │")
    svar_liste_ny.append("├─" + strek                                    + "─┤")
    svar_liste_ny.append("│ " + n_svar_liste[1] + space(n_svar_liste[1]) + " │")
    svar_liste_ny.append("│ " + n_svar_liste[2] + space(n_svar_liste[2]) + " │")
    svar_liste_ny.append("└─" + strek                                    + "─┘")

    return svar_liste_ny

# Regner ut sannsynligheten for k antall obj_p i en gruppe med n_gruppe obj (se while-løkke)
def sannsynlighet_for(n_gruppe,
                      g_gruppe   = g_gruppe,
                      k_rel      = synonymer(k_rel),
                      s_rel      = synonymer(sannsyn_gitt_rel),
                      n_svar_rel = n_svar_rel,
                      _d_s       = _debug_matriks,
                      _d_w       = _debug_while):

    # Simulering steg-for-steg
    if _blokk == -1:
        # 1. n_gruppe starter på 1 og kan øke
        # 2. Etter første simulering sammenlignes sannsyn_sim med sannsyn_gitt
        # 3. Hvis sannsyn_sim < sannsyn_gitt øker n_klasse med 1
        # 4. Da gjøres simuleringen om igjen med den nye verdien for n_gruppe
        # 5. Simulerer at det er p sannsynlighet for at et obj er obj_p
        # 6. Dette obj blir så enten obj_p eller ikke, 1 eller 0
        # 7. Gjør dette n_gruppe ganger og får f.eks. 0, 0, 1, 0 og 1 (hvis n_gruppe er 5)
        # 8. Teller hvor mange av n_gruppe som ble obj_p, f.eks. 2
        # 9. Legger 2 i listen, [2]
        # 10. Gjør dette med m_gruppe grupper, [2, 0, 0, ..., 1]
        # 11. m_gruppe_liste får dermed alle utfallene (fra simuleringen)
        pass
    m_gruppe_liste = rng.binomial(n = n_gruppe, p = p, size = m_gruppe)

    # Matriks steg-for-steg
    if _blokk == 1:
        if _blokk == -1:
            # 1. Når du leser setningen "Det er_________x % sannsyn..." (x = sannsyn_gitt) nedenfor,
            #   så kan du tenke at du "fyller inn" relasjonene som står i kolonnene under
            #   (relasjonene som du først skrev inn som konstanter i starten av koden)
            # 2. Da kan du lese av hele den aktuelle raden (riktig kombinasjon for dine relasjoner) og se
            #    2.1. Hvilke relasjon som returneres til ditt svar (hvis oppg spør om hvor stor n_gruppe med obj
            #         må være for å få ønsket sannsynlighet for å tilfeldig trekke k obj_p fra gruppen
            #    2.2. Hvilken sannsynlighets-blokk som brukes (hvis du setter _debug_sannsyn = 1), f.eks. "3-2"
            pass
        #          Det er_________x % sannsyn for__________(enn) k obj_p i gruppen
        if _blokk == 1:
            if s_rel == "nøyaktig"  and k_rel == "nøyaktig":   g_gruppe = sum(m_gruppe_liste == k); d(_d_s, "1-1"); n_svar_rel = "nøyaktig"
            if s_rel == "nøyaktig"  and k_rel == "minst":      g_gruppe = sum(m_gruppe_liste >= k); d(_d_s, "1-2"); n_svar_rel = "nøyaktig"
            if s_rel == "nøyaktig"  and k_rel == "flere":      g_gruppe = sum(m_gruppe_liste >  k); d(_d_s, "1-3"); n_svar_rel = "nøyaktig"
            if s_rel == "nøyaktig"  and k_rel == "maksimalt":  g_gruppe = sum(m_gruppe_liste <= k); d(_d_s, "1-4"); n_svar_rel = "nøyaktig"
            if s_rel == "nøyaktig"  and k_rel == "mindre":     g_gruppe = sum(m_gruppe_liste <  k); d(_d_s, "1-5"); n_svar_rel = "nøyaktig"
        if _blokk == 1:
            if s_rel == "minst"     and k_rel == "nøyaktig":   g_gruppe = sum(m_gruppe_liste == k); d(_d_s, "2-1"); n_svar_rel = "minst"
            if s_rel == "minst"     and k_rel == "minst":      g_gruppe = sum(m_gruppe_liste >= k); d(_d_s, "2-2"); n_svar_rel = "minst"
            if s_rel == "minst"     and k_rel == "flere":      g_gruppe = sum(m_gruppe_liste >  k); d(_d_s, "2-3"); n_svar_rel = "flere"
            if s_rel == "minst"     and k_rel == "maksimalt":  g_gruppe = sum(m_gruppe_liste <= k); d(_d_s, "2-4"); n_svar_rel = "maksimalt"
            if s_rel == "minst"     and k_rel == "mindre":     g_gruppe = sum(m_gruppe_liste <  k); d(_d_s, "2-5"); n_svar_rel = "mindre"
        if _blokk == 1:
            if s_rel == "flere"     and k_rel == "nøyaktig":   g_gruppe = sum(m_gruppe_liste == k); d(_d_s, "3-1"); n_svar_rel = "flere"
            if s_rel == "flere"     and k_rel == "minst":      g_gruppe = sum(m_gruppe_liste >= k); d(_d_s, "3-2"); n_svar_rel = "minst"
            if s_rel == "flere"     and k_rel == "flere":      g_gruppe = sum(m_gruppe_liste >  k); d(_d_s, "3-3"); n_svar_rel = "flere"
            if s_rel == "flere"     and k_rel == "maksimalt":  g_gruppe = sum(m_gruppe_liste <= k); d(_d_s, "3-4"); n_svar_rel = "maksimalt"
            if s_rel == "flere"     and k_rel == "mindre":     g_gruppe = sum(m_gruppe_liste <  k); d(_d_s, "3-5"); n_svar_rel = "mindre"
        if _blokk == 1:
            if s_rel == "maksimalt" and k_rel == "nøyaktig":   g_gruppe = sum(m_gruppe_liste == k); d(_d_s, "4-1"); n_svar_rel = "maksimalt"
            if s_rel == "maksimalt" and k_rel == "minst":      g_gruppe = sum(m_gruppe_liste >= k); d(_d_s, "4-2"); n_svar_rel = "maksimalt"
            if s_rel == "maksimalt" and k_rel == "flere":      g_gruppe = sum(m_gruppe_liste >  k); d(_d_s, "4-3"); n_svar_rel = "maksimalt"
            if s_rel == "maksimalt" and k_rel == "maksimalt":  g_gruppe = sum(m_gruppe_liste <= k); d(_d_s, "4-4"); n_svar_rel = "minst"
            if s_rel == "maksimalt" and k_rel == "mindre":     g_gruppe = sum(m_gruppe_liste <  k); d(_d_s, "4-5"); n_svar_rel = "minst"
        if _blokk == 1:
            if s_rel == "mindre"    and k_rel == "nøyaktig":   g_gruppe = sum(m_gruppe_liste == k); d(_d_s, "5-1"); n_svar_rel = "mindre"
            if s_rel == "mindre"    and k_rel == "minst":      g_gruppe = sum(m_gruppe_liste >= k); d(_d_s, "5-2"); n_svar_rel = "maksimalt"
            if s_rel == "mindre"    and k_rel == "flere":      g_gruppe = sum(m_gruppe_liste >  k); d(_d_s, "5-3"); n_svar_rel = "minst"
            if s_rel == "mindre"    and k_rel == "maksimalt":  g_gruppe = sum(m_gruppe_liste <= k); d(_d_s, "5-4"); n_svar_rel = "minst"
            if s_rel == "mindre"    and k_rel == "mindre":     g_gruppe = sum(m_gruppe_liste <  k); d(_d_s, "5-5"); n_svar_rel = "minst"

    # Definisjonen av sannsynlighet gir P(OP) = g / m, der hendelsen OP: "obj i gruppen er obj_p"
    sannsyn_sim = g_gruppe / m_gruppe

    # 0: Av, 1: Debug while-løkke (f.eks. se sannsyn_sim-verdiene, om løkken henger)
    d_w(_d_w, f"{sannsyn_sim}")

    # Returnerer en liste med sannsynlighet og relasjon
    return [sannsyn_sim, n_svar_rel]

# While-løkke steg-for-steg
if _blokk == -1:
    # 1. Betingelsen i løkken er to-delt
    #    1.1 For ">=", ">", "==": sannsyn_sim går fra 0 opp til sannsyn_gitt
    #    1.2 For "<=", "<"      : sannsyn_sim går fra 1 ned til sannsyn_sim
    # 2. Løkken kaller f_sannsynlighet_for() med to arg
    #    2.1. sannsyn_gitt_rel (valgfri/har default): ("==", ">=", ">", "<=", "<")
    #    2.2. n_klasse (obligatorisk)               : nåværende gutter i klassen
    # 3. sannsynlighet_for() returnerer to variabler (i en liste)
    #    3.1 sannsynlighet_for()[0]: sannsyn_sim
    #    3.2 sannsynlighet_for()[1]: svar_rel (relasjonen i svaret)
    # 4. Hvis f.eks. sannsyn_sim < sannsyn_gitt (betingelsen), så øker n_gruppe med 1
    # 5. Isåfall kaller løkken sannsynlighet_for() om igjen
    # 6. Løkken vil da repeterer dette til sannsyn_sim >= sannsyn_gitt (betingelsen brytes)
    # 7. Merk at == ikke kan brukes i sannsynlighet_for(n_gruppe)[0] == sannsyn_gitt
    #   fordi sannsyn_sim aldri starter på sannsyn_gitt (betingelsen brytes isåfall med en gang)
    #   == erstattes derfor med <=, som blir beste tilnærming (bryter betingelsen med en
    #   sannsyn_sim er rett over, eller teoretisk sett lik)
    pass
while ((synonymer(sannsyn_gitt_rel)    == "nøyaktig"    and (k_rel == "nøyaktig"  or k_rel == "minst"   or k_rel == "flere") and
        sannsynlighet_for(n_gruppe)[0] <= sannsyn_gitt) or # == er byttet ut med <= (se kommentar over)
       (synonymer(sannsyn_gitt_rel)    == "nøyaktig"    and (k_rel == "maksimalt" or k_rel == "mindre") and
        sannsynlighet_for(n_gruppe)[0] >= sannsyn_gitt) or

       (synonymer(sannsyn_gitt_rel)    == "minst"       and (k_rel == "nøyaktig"  or k_rel == "minst"   or k_rel == "flere") and
        sannsynlighet_for(n_gruppe)[0] <= sannsyn_gitt) or
       (synonymer(sannsyn_gitt_rel)    == "minst"       and (k_rel == "maksimalt" or k_rel == "mindre") and
        sannsynlighet_for(n_gruppe)[0] >= sannsyn_gitt) or

       (synonymer(sannsyn_gitt_rel)    == "flere"       and (k_rel == "nøyaktig"  or k_rel == "minst"   or k_rel == "flere") and
        sannsynlighet_for(n_gruppe)[0] <  sannsyn_gitt) or
       (synonymer(sannsyn_gitt_rel)    == "flere"       and (k_rel == "maksimalt" or k_rel == "mindre") and
        sannsynlighet_for(n_gruppe)[0] >  sannsyn_gitt) or

       (synonymer(sannsyn_gitt_rel)    == "maksimalt"   and (k_rel == "nøyaktig"  or k_rel == "minst"   or k_rel == "flere") and
        sannsynlighet_for(n_gruppe)[0] <= sannsyn_gitt) or
       (synonymer(sannsyn_gitt_rel)    == "maksimalt"   and (k_rel == "maksimalt" or k_rel == "mindre") and
        sannsynlighet_for(n_gruppe)[0] >= sannsyn_gitt) or

       (synonymer(sannsyn_gitt_rel)    == "mindre"      and (k_rel == "nøyaktig"  or k_rel == "minst"   or k_rel == "flere") and
        sannsynlighet_for(n_gruppe)[0] <  sannsyn_gitt) or
       (synonymer(sannsyn_gitt_rel)    == "mindre"      and (k_rel == "maksimalt" or k_rel == "mindre") and
        sannsynlighet_for(n_gruppe)[0] >  sannsyn_gitt)):

    # n_gruppe øker med 1 hver gang løkken (og simuleringen) kjøres
    n_gruppe += 1

# Kaller sannsynlighet_for() en ekstra gang med forrige klasse_n for å få relasjonen til svaret
n_svar_rel = sannsynlighet_for(n_gruppe - 1, sannsyn_gitt_rel)[1]

# Returner "enn" for relasjonene i if-blokkene og "" for andre
def enn_rel(rel):
    if rel == "flere" or rel == "større" or rel == "mer" or rel == "mindre" or rel == "færre": return f"{rel} enn "
    else: return f"{rel} "

# Gang med 100 for prosent og rund av til f.eks. 1 eller 0 (None) desimaler
sannsyn_gitt = round(sannsyn_gitt * 100, None)

# Legg svar-setningene i en liste og formater
n_svar_liste = [
        f"{gruppe_navn} må ha {enn_rel(n_svar_rel)}{n_gruppe} {obj} ",
        f"✓ Det skal være {enn_rel(k_rel)}{k} {obj_p}",
        f"✓ Sannsynligheten for utfallet er {enn_rel(sannsyn_gitt_rel)}{sannsyn_gitt} %"]
n_svar_liste = tabell_format(n_svar_liste)

# Print svar-setninger
for svar in n_svar_liste:
    print(svar)
