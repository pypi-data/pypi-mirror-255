# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 3 c) Sparekonto - År før totalt innskudd er fordoblet 
# - Løser oppgaven med CAS i Python
# - Prosentvis vekst er en eksponentialfunksjon som kan skrives på formen
#   - f(x) = a * b^x, f(0) = a (startverdi), b > 0 (vekstfaktor)

from sympy import ConditionSet, core, Eq, FiniteSet, Intersection, nsolve, Reals, solve, solveset, Symbol

# Konstanter og CAS-variabler (symbol)
B_P                = Symbol("B_P")     # Beløp etter n år (Per)
B_K                = Symbol("B_K")     # Beløp etter n år (Kåre)
B_30000            = 30000             # 30 000,- spart
I                  = Symbol("I")       # Innskuddet (startbeløpet inn på konto)
V_P                = Symbol("V_P")     # Vekstfaktor (Per)
V_K                = Symbol("V_K")     # Vekstfaktor (Kåre)
p_rente_p                = 3                 # Årlig rente i banken (Per)
p_rente_k                = 6                 # Årlig rente i banken (Per)
n                  = Symbol("n")       # Antall år med sparing
n_8                = 8                 # Periode på 8 år
n_dobbelt_p        = float()           # År med sparing (Per)
n_dobbelt_k        = float()           # År med sparing (Kåre)
n_forhold          = float()           # Forholdet n_dobbelt_p / n_dobbelt_k
n_dobbelt_totalt   = float()           # Antall år før totalt innskudd er fordoblet
_blokk             = 1                 # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker

# Definerer funksjoner
def vekstfaktor(fortegn = str(),
                p       = float(),
                rund    = -1):
    
    # Vekstfaktor er definert som V = 1 ± p / 100, p: prosentvis vekst [%]
    v = 0.0
    if fortegn == "+": v = 1 + p / 100 # "+": Øker
    if fortegn == "-": v = 1 - p / 100 # "-": Minker
    
    # Runder av svaret
    if rund != 1: v = round(v, rund)
    
    return v

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

# Definerer uttrykket for vekstfaktoren, v = 1 + p / 100
V_P = vekstfaktor(p_rente_p, "+")
V_K = vekstfaktor(p_rente_k, "+")

# a) Finn innskuddet til Per
if _blokk == 1:

    # Definerer uttrykket for B
    B = I * V_P**n # B = I * 1.03**n (en ukjente, I og n)

    # Setter n = 8 inn i B og definerer det nye uttrykket som B_8 
    B_8 = B.subs(n, n_8) # B_8 = I * 1.03**8

    # Løser likningen 30000 = I * 1.03**8 for I
    I = superløs(variabel = I,
                 vs       = B_30000,
                 hs       = B_8,
                 rund     = None,
                 debug    = -1)

    # Svar-setninger
    svar_a_liste = list()
    svar_a_liste.append(f"")
    svar_a_liste.append(f"Oppg a)")
    svar_a_liste.append(f"")
    svar_a_liste.append(f"- Dersom Per skal ha kr {B_30000} på kontoen sin etter {n_8} år,")
    svar_a_liste.append(f"  så må han ha et innskudd på ca. kr {I}")

    # Print svar-setninger
    for svar in svar_a_liste: print(svar)

# b) Påstand: Dobbelt så lang tid
if _blokk == 1:

    # Definerer uttrykkene for B_P og B_K
    B_P = I * V_P**n
    B_K = I * V_K**n

    # Løser likningen 2 * 23682 = 23682 * 1.03**n for n
    n_dobbelt_p = superløs(variabel = n,
                           vs       = 2 * I,
                           hs       = B_P,
                           rund     = 2,
                           debug    = -1)

    # Løser likningen 2 * 23682 = 23682 * 1.06**n for n
    n_dobbelt_k = superløs(variabel = n,
                           vs       = 2 * I,
                           hs       = B_K,
                           rund     = 2,
                           debug    = -1)

    # Regner ut forholdet n = 23.45 / 11.90 = 1.97 
    n_forhold = n_dobbelt_p / n_dobbelt_k

    # Runder av svaret
    n_forhold = round(n_forhold, 2)

    # Svar-setninger
    svar_b_liste = list()
    svar_b_liste.append(f"")
    svar_b_liste.append(f"Oppg b)")
    svar_b_liste.append(f"")
    svar_b_liste.append(f"- Nei, det vil ikke gå nøyaktig dobbelt så lang tid, men ca.")
    svar_b_liste.append(f"  {n_dobbelt_p} år / {n_dobbelt_k} år = {n_forhold} ganger så lang tid")
    svar_b_liste.append(f"- Vi kan også vise at likningen ikke kan løses")
    svar_b_liste.append(f"     2 * B_P = 2 * B_K | 1 / 2")
    svar_b_liste.append(f"     B_P = B_K")
    svar_b_liste.append(f"     I * 1.03^(2n) = I * 1.06^n | 1 / I")
    svar_b_liste.append(f"     1.03^(2n) = 1.06^n")
    svar_b_liste.append(f"     (1.03^2)^n = 1.06^n, a^(nm) = (a^n)^m")
    svar_b_liste.append(f"     1.0609^n ≠ 1.06^n")
    svar_b_liste.append(f"")
    svar_b_liste.append(f"- Påstanden er derfor ikke riktig")
    # Print svar-setninger
    for svar in svar_b_liste: print(svar)

# c) År før totalt innskudd er fordoblet
if _blokk == 1:

    # Løser likningen I * V_P**n + I * V_K**n = 4 * I 
    n_dobbelt_totalt = superløs(variabel = n,
                                vs       = B_P + B_K,
                                hs       = 4 * I,
                                rund     = 2,
                                debug    = -1)

    # Svar-setninger
    svar_c_liste = list()
    svar_c_liste.append(f"")
    svar_c_liste.append(f"Oppg c)")
    svar_c_liste.append(f"")
    svar_c_liste.append(f"- Det vil gå ca. {n_dobbelt_totalt} år før Per og Kåre til sammen")
    svar_c_liste.append(f"  har dobbelt så mye som de satt inn")
    # Print svar-setninger
    for svar in svar_c_liste: print(svar)
