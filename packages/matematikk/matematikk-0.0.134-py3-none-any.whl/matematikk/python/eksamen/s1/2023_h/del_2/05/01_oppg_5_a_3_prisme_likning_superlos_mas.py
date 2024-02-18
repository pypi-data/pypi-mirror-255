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
    s            = Symbol("s")
    h            = Symbol("h")
    A_max        = 120
    s_5          = 5

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
