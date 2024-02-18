# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 5 a) Volum av prisme - Største volum dersom sidene i bunnen er 5 dm (løsning med likninger) 

from sympy import Eq, Reals, core, Symbol, ConditionSet, FiniteSet, Intersection, solve, solveset, nsolve

# Konstanter
_blokk = 1 # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker

# Definerer funksjoner
def superløs(variabel = Symbol(""),
             vs       = Symbol(""),
             hs       = Symbol(""),
             likning  = list(),
             rund     = -1,
             debug    = -1):

    vis_datatype = True
    losning_set, losning_set_sub = set(), set()
    losning_liste, losning_element, losning_rund_liste, losning_ut = list(), list(), list(), list()
    losning_rund_status, sett_typ, likn_ant, los_ant, _v_avrund_typ = str(), str(), str(), str(), str()
    losning_rund = float()

    if type(likning) != list: likning_tmp = likning; likning = []; likning.append(likning_tmp)

    if len(likning) == 0:
        likn_ant = "En likning"
        if type(variabel) == type(list()): variabel = variabel[0]
        if type(vs) != core.mul.Mul and type(vs) == type(list()): vs = vs[0]
        if type(hs) != core.mul.Mul and type(hs) == type(list()): hs = hs[0]
        _likning = Eq(vs, hs); losning_set = solveset(_likning, variabel, domain = Reals)

        if len(likning) == 0 and type(losning_set) == FiniteSet:
            sett_typ = "FiniteSet";
            if len(losning_set) == 1: los_ant = "en løsning"
            if len(losning_set) > 1: los_ant = str(len(losning_set)) + " " + "løsninger"

        if len(likning) == 0 and type(losning_set) == ConditionSet:
            sett_typ = "ConditionSet"; losning_element = nsolve(_likning, variabel, 1)
            los_ant = "en numerisk løsning"; losning_set = []; losning_set.append(losning_element)

        if len(likning) == 0 and type(losning_set) == Intersection:
            sett_typ = "Intersection"; losning_set_sub = losning_set.args[1]
            losning_element = losning_set_sub.args; losning_set = [];
            for el in losning_element: losning_set.append(el); rund = -1
            if len(losning_set) == 1: los_ant = "en løsning som er et uttrykk"
            if len(losning_set) > 1: los_ant = str(len(losning_set)) + " " + "løsninger som er uttrykk"

    if len(likning) > 0:
        sett_typ = ""; likn_ant = "Flere likninger (likningssett)"
        losning_set = solve(likning, variabel, dict=True)
        for i in range(len(losning_set)):
            koordinat_verdi_liste = list(); koordinat_variabel_rund_liste = list()
            for koordinat_variabel, koordinat_verdi in losning_set[i].items():
                koordinat_verdi_liste.append(koordinat_verdi)
                losning_rund = round(float(koordinat_verdi), rund)
                koordinat_variabel_rund_liste.append(losning_rund)
            losning_liste.append(koordinat_verdi_liste); losning_rund_liste.append(koordinat_variabel_rund_liste)

    for losning in losning_set:
        if rund == -1:
            _v_avrund_typ = "(eksakt)"; losning_rund_status = "Nei"; losning_rund_liste = ""
            if len(likning) == 0: losning_liste.append(losning); losning_ut = losning_liste
            if len(likning) > 0: losning_ut = losning_liste

        if rund != -1:
            _v_avrund_typ = "(avrundet)"; losning_rund_status = "Ja"
            if len(likning) == 0:
                losning_liste.append(losning); losning_rund = round(losning, rund)
                losning_rund_liste.append(losning_rund); losning_ut = losning_rund_liste
            if len(likning) > 0: losning_ut = losning_rund_liste

    if len(losning_ut) == 1: losning_ut = losning_ut[0]

    if debug == 1:
        print("")
        print(f"*** Debug ****")
        if vis_datatype == True:
            print(f"Data-type                        :: {sett_typ}")
        print(f"Løsnings-type                    :: {likn_ant} med {los_ant} {_v_avrund_typ}")
        print(f"Løsnings-sett                    :: {losning_set}")
        print(f"Løsnings-element(er)             :: {losning_liste}")
        print(f"Avrunding (ja/nei)               :: {losning_rund_status}")
        print(f"Løsnings-elemente(er) avrundet   :: {losning_rund_liste}")
        print(f"-----------------------------------")
        print(f"Løsning ut (returnert) -----------> {losning_ut}")
        print(f"-----------------------------------")

    return losning_ut

# a) Største volum dersom sidene i bunnen er 5 dm (løsning med likninger)
if _blokk == 1:

    # Regner ut volum av prisme med likning når areal_maks, lengde og dybde er gitt

    # Skisse av kassen
    if _blokk == 0:
        #                    |------------
        #                    | .	       .
        #                    |  -	   V    -
        #                    |   .------------
        #                    _   |			 |
        #                     .  |	   A     |   h
        #                 s     _|			 |
        #                        .------------
        # 
        #                                s
        pass

    # Konstanter og CAS-variabler (symbol)
    V                  = Symbol("V")   # Prismets volum
    V_80               = 80   # Prismets volum i oppg c)
    A                  = Symbol("A")   # Arealet av platene
    A_max              = 120           # Maksimalt arealet av platene
    s                  = Symbol("s")   # Sidene i den kvadratiske grunnflaten
    s_5                = 5             # Lengden på sidene
    h                  = Symbol("h")   # Prismets høyde

    # Definerer uttrykkene for A og V
    A = s**2 + 4*s*h
    V = s**2 * h

    # Setter s = 5 inn i A og definerer det nye uttrykket som A_5 (slik at ikke A skrives over) 
    A_5 = A.subs(s, s_5)

    # Løser likningen 120 = 5**2 + 4*5*h 
    h_losning = superløs(variabel = h,
                         vs       = A_max,
                         hs       = A_5,
                         rund     = 2,
                         debug    = -1)

    # Setter h = -(s + 5)/4 inn i V og definerer det nye uttrykket som V_uttrykk 
    V_max = V.subs(s, s_5).subs(h, h_losning) # Bruker .subs flere ganger etter hverandre ("chain rule")

    # Print svar-setninger
    svar_a_0 = f"Oppg a)"
    svar_a_1 = f"- Det største volumet kassen kan ha er {V_max} dm^3"
    print("")
    print(svar_a_0)
    print(svar_a_1)

# b) Maksimalt volum av kassen
if _blokk == 1:

    # Maksimalt volum steg-for-steg
    if _blokk == 0:
        # 1. For å finne maksimalt volum til kassen, så må vi
        #    derivere V
        # 2. Vi finner som vanlig ekstremalpunktet til V ved å sette den
        #    deriverte lik 0 og løse denne likningen
        # 3. Men, fordi V foreløpig er en funksjon av både s og h, så må
        #    vi først gjøre om V til å kun være uttrykt med en variabel
        # 4. Vi kan mao. bruke konstanten for det maksimale arealet 120 i
        #    likningen for A til å skrive denne likningen om til å være
        #    h uttrykt med s
        # 5. Når vi så bytter ut ut h i likningen til V med dette uttrykket,
        #    så får vi V kun uttrykt med s
        pass

    # Løser likningen 120 = s**2 + s*5*h for h
    h_uttrykk = superløs(variabel = h,
                         vs       = A_max,
                         hs       = A,
                         rund     = 2,
                         debug    = -1) # h = -(s + 5)/4

    # Setter h = -(s + 5)/4 inn i V og definerer det nye uttrykket som V_uttrykk 
    V_uttrykk = V.subs(h, h_uttrykk) # Nå er V kun uttrykt med s, og kan derfor enkelt deriveres

    # Deriverer V mhp. s og får dV = 30 - 3*s**2/4
    dV = V_uttrykk.diff()

    # Løser likningen dV = 0 
    s_topp_eksakt = superløs(variabel = s,
                             vs       = dV,
                             hs       = 0,
                             rund     = -1,  # rund  = -1 gir eksakt verdi
                             debug    = -1)  # debug = 1  viser både eksakt og avrundet verdi med superløs()

    # Setter inn den positive av de to løsningene for s, -2*sqrt(10) og 2*sqrt(10), inn i V_uttrykk
    V_uttrykk_eksakt = V_uttrykk.subs(s, s_topp_eksakt[1]) # V_uttrykk = 40*sqrt(10)

    # Runder av svaret
    V_uttrykk_rund = round(V_uttrykk_eksakt, 1)

    # Print svar-setninger
    svar_b_0 = f"Oppg b)"
    svar_b_1 = f"- Eksakt lengde er s_1 = {s_topp_eksakt[0]} og s_2 = {s_topp_eksakt[1]} dm"
    svar_b_2 = f"- Fordi s er en lengde, så bruker vi kun den positive løsningen"
    svar_b_3 = f"- Dette gir et eksakt maksimalt volum på V = {V_uttrykk}"
    svar_b_4 = f"- Avrundet svar gir derfor løsningen V = {V_uttrykk_rund} dm^3"
    print("")
    print(svar_b_0)
    print(svar_b_1)
    print(svar_b_2)
    print(svar_b_3)
    print(svar_b_4)

# c) Minste samlede areal til platene når kassen er 80 cm^3
if _blokk == -1:

    # Minst arealsteg-for-steg
    if _blokk == 0:
        # 1. Når vi ser på uttrykkene for A og V, så ser
        #    vi at dette er et likningssett med to ukjente, s og h
        # 2. På samme måte som i oppg. b), kan vi derfor
        #    først bruke V og finne et uttrykk for h mhp. s
        #    (volumet V er kjent, 80)
        # 4. Dette uttrykket for h kan vi deretter sette inn i A,
        #    som så blir uttrykt kun med s
        # 5. A kan derfor deriveres mhp. s
        #    Detter løser vi likningen dA = 0 på samme måte som
        #    i oppg. b) for å finne den verdien av s som gir det laveste arealet
        # 6. Når vi har funnet denne verdien for s, så kan vi regne ut hvor
        #    stort dette arealet er ved å sette den inn i A
        pass

    # Løser likningen 80 = s**2 * h for h
    h_uttrykk = superløs(variabel = h,
                         vs       = V_80,
                         hs       = V,
                         rund     = -1,
                         debug    = -1) # h = 80/s**2

    # Setter h = 80/s**2 inn i A og definerer det nye uttrykket som A_s 
    A_s = A.subs(h, h_uttrykk)

    # Deriverer A mhp. s og får dA = 2*s - 320/s**2
    dA = A_s.diff()

    # Løser likningen dA = 0 
    s_bunn = superløs(variabel = s,
                      vs       = dA,
                      hs       = 0,
                      rund     = -1,
                      debug    = -1) # s = 2*20**(1/3)

    # Setter s = 2*20**(1/3) inn i A_s og definerer det nye uttrykket som A_min 
    A_min = A_s.subs(s, s_bunn)

    # Runder av svaret
    A_min_rund = round(A_min, 2)

    # Print svar-setninger
    svar_c_0 = f'Oppg c)'
    svar_c_1 = f'- Fordi a-koeffisienten til A er positiv, så "smiler" grafen'
    svar_c_2 = f'- Dette betyr at vi har et bunnpunkt (grunnen til at vi valgte variabelnavnet s_bunn)'
    svar_c_3 = f'- I dette bunnpunktet er det minste areaelet A = {A_min_rund} dm^2'
    print("")
    print(svar_c_0)
    print(svar_c_1)
    print(svar_c_2)
    print(svar_c_3)
