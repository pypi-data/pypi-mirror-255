# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 6 a) Tredjegradsfunksjon - Påstand 1: Grafen f har minst ett ekstremalpunkt 

from sympy import ConditionSet, core, diff, Eq, FiniteSet, Intersection, nsolve, Reals, solve, solveset, Symbol

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
def ekstremalpunkt(variabel = Symbol(""),
                   f        = Symbol(""),
                   rund     = -1,
                   debug    = -1):

    # Deriverer funksjonen f mhp.  og får 
    df = diff(f, x)

    # Løser likningen df = 0 
    f_ekstremalpunkt = superløs(variabel = variabel,
                                vs       = df,
                                hs       = 0,
                                rund     = rund,
                                debug    = debug)

    return f_ekstremalpunkt

# Konstanter
_blokk = 1 # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker

# a) Påstand 1: Grafen f har minst ett ekstremalpunkt
if _blokk == 1:

    # Konstanter og CAS-variabler (symbol)
    a                  = Symbol("a")   # Funksjonens a-koeffisient
    b                  = Symbol("b")   # Funksjonens b-koeffisient
    c                  = Symbol("c")   # Funksjonens c-koeffisient
    d                  = Symbol("d")   # Funksjonens c-koeffisient
    f                  = Symbol("f")   # Funksjonens navn
    x                  = Symbol("f")   # Funksjonens variabel

    # Svar-setninger
    svar_a_liste = list()
    svar_a_liste.append(f"")
    svar_a_liste.append(f"Oppg a)")
    svar_a_liste.append(f"")
    svar_a_liste.append(f"- Hvis alle tredjegradsfunksjoner har minst ett ekstremalpunkt,")
    svar_a_liste.append(f"  så kan vi først finne uttrykket til ekstremalpunktene")
    svar_a_liste.append(f"- Dette finner vi ved å")
    svar_a_liste.append(f"  1. Definere et generelt uttryk for f")
    svar_a_liste.append(f"  2. Derivere f")
    svar_a_liste.append(f"  3. Løse likningen df = 0")
    svar_a_liste.append(f"  4. Løsningen på df = 0 vil være evt. ekstremalpunkt")
    svar_a_liste.append(f"  5. Se om vi kan trekke noen konklusjoner fra løsningen")

    # Definerer uttrykket for f
    f = a * x**3 + b * x**2 + c * x + d

    # Finner ekstremalpunktene til f(x) = a * x**3 + b * x**2 + c * x + d
    f_ekstremalpunkt = ekstremalpunkt(variabel = x,
                                      f        = a * x**3 + b * x**2 + c * x + d,
                                      rund     = -1,
                                      debug    = -1)

    # Printer løsningene -b/(3*a) ± sqrt(-3*a*c + b**2)/(3*a)
    svar_a_liste.append(f"")
    svar_a_liste.append(f"- Ekstremalpunktene til f er:")
    for i in range(len(f_ekstremalpunkt)):
        svar_a_liste.append(f"  - ekstremalpunkt_{i} = {f_ekstremalpunkt[i]}")

    # Svar-setninger
    svar_a_liste.append(f"")
    svar_a_liste.append(f"- Når uttrykket under rot-tegnet (diskriminanten, -3*a*c + b**2)")
    svar_a_liste.append(f"  er negativt, så har likningen df = 0 ingen løsning")
    svar_a_liste.append(f"- Dette betyr igjen betyr at slike funksjoner ikke har")
    svar_a_liste.append(f"  noen ekstremalpunkter")
    svar_a_liste.append(f"- Vi kan også uttrykke en negativ diskrimant med ulikheten")
    svar_a_liste.append(f"  -3*a*c + b**2 < 0")
    svar_a_liste.append(f"- Deretter kan vi løse denne ulikheten for f.eks. a for å")
    svar_a_liste.append(f"  vise sammenhengen mellom a og de andre to koeffisientene, b og c")
    svar_a_liste.append(f"- Eller, vi kan gjøre det samme for f.eks. b (og vise")
    svar_a_liste.append(f"  sammenhengen mellom b og de to andre koeffisientene, a og c")
    svar_a_liste.append(f"- Dette er altså kun for bedre å vise sammenhengen")
    svar_a_liste.append(f"  mellom de tre koeffisientene, istedenfor å bare vise en uliket")
    svar_a_liste.append(f"- NB: Passer på at ulikhets-tegnet peker riktig vei når vi først løser")
    svar_a_liste.append(f"- en slik likning, for så å konverterer løsningen tilbake til en ulikhet")

    # Løser likningen -3*a*c + b**2 = 0 for a
    a_uttrykk = superløs(variabel = a,
                         vs       = -3*a*c + b**2,
                         hs       = 0,
                         rund     = -1,
                         debug    = -1)

    # Svar-setninger
    svar_a_liste.append(f"")
    svar_a_liste.append(f"- Som vi ser, så finnes det tredjegradsfunksjoner som ikke har minst")
    svar_a_liste.append(f"  ett ekstremalpunkt")
    svar_a_liste.append(f"- Mer bestemt, så vil alle tredjegradsfunksjoner hvor")
    svar_a_liste.append(f" {a} > {a_uttrykk} ikke ha noen ekstremalpunkt")
    svar_a_liste.append(f"")
    svar_a_liste.append(f"- Påstand 1 er derfor usann")

    # Print svar-setninger
    for svar in svar_a_liste: print(svar)
