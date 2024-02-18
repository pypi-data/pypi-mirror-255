# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 1 b) Sofa-produksjon til møbelfabrikk - Størst overskudd 
# - Løser oppgaven med CAS i Python
# - Kopier kommandoene i terminalen og importer pakkene 
#   $ pip install numpy
#   $ pip install sympy
#   $ pip install matematikk

from numpy import polyfit
from sympy import ConditionSet, core, diff, Eq, FiniteSet, Intersection, nsolve, Reals, solve, solveset, Symbol

# Variabler
x            = Symbol("x")       # Produksjons-mengden x
x_max       = float()           # Produksjonsmengden som gir størst overskudd
K            = Symbol("K")       # Polynomets navn (vs)
grad         = 2                 # Polynomets grad
poly         = Symbol("poly")    # Polynomet (vs og hs)
x_liste      = [                 # Liste med x-verdier
    10,
    25,
    40,
    70,
    100,
    140,
    180]
y_liste      = [                 # Liste med y-verdier
    270,
    550,
    870,
    1500,
    2200,
    3300,
    4500]
O            = Symbol("O")       # Overskudds-funksjonen
dO           = Symbol("dO")      # Den deriverte av overskudds-funksjonen
rund         = 2                 # -1: Ingen avrunding, 0: Eks: 123.0, n > 0: n siffer etter desimaltegnet, None: Heltall
_blokk       = 1                 # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker

# Definerer funksjoner
def reggis(variabel = Symbol(""),
           grad     = int(),
           x_liste  = list(),
           y_liste  = list(),
           rund     = -1):

    # - Lager polynom-funksjon av valgfri grad vha. regresjon (CAS)

    # Variabler
    _koeff_liste       = list()                # Liste med koeffesienter i fra polyfit()
    _koeff             = float()               # Polynomets koeffisienter
    _ledd              = Symbol("_ledd")       # Polynomets ledd
    _ledd_grad         = int()                 # Polynomets ledd inkludert grad
    _uttrykk           = Symbol("_uttrykk")    # Polynomets uttrykk (hs)

    # polyfit() returnerer en liste med regresjons-koeffesientene
    _koeff_liste = polyfit(x_liste, y_liste, grad)

    # Hver iterasjon lager det neste leddet i polynomet
    for i in range(len(_koeff_liste)):

        # - På 1. iterasjon må _uttrykk nulles ut slik at det ikke blir en
        #   egen variabel i uttrykket, f.eks. "_uttrykk + 0.04*x**2 + 17.05*x + 102.7"
        if i == 0: _uttrykk = 0

        # Runder av koeffesienten
        if rund == -1: _koeff = _koeff_liste[i]
        if rund != -1: _koeff = round(_koeff_liste[i], rund)

        # Lager leddene i fra størst til minst grad
        _ledd_grad = grad - i

        # Formaterer leddene
        if _ledd_grad >= 2: _ledd = _koeff * variabel**_ledd_grad
        if _ledd_grad == 1: _ledd = _koeff * variabel
        if _ledd_grad == 0: _ledd = _koeff

        # Legger det nye leddet til polynomet
        _uttrykk += _ledd

    return _uttrykk

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

# a) Finn O(x)
if _blokk == 1:

    # Lager polynom-funksjon av valgfri grad vha. regresjon (CAS)
    K = reggis(variabel = x,
               grad     = grad,
               x_liste  = x_liste,
               y_liste  = y_liste,
               rund     = rund)

    # Svar-setninger
    svar_a_liste = list()
    svar_a_liste.append(f"")
    svar_a_liste.append(f"Oppg a)")
    svar_a_liste.append(f"")
    svar_a_liste.append(f"- Med regresjon fra numpy (polyfit) ser vi at hvis bedriften")
    svar_a_liste.append(f"  produserer x enheter, så vil")
    svar_a_liste.append(f"")
    svar_a_liste.append(f"    {K}")
    svar_a_liste.append(f"")
    svar_a_liste.append(f"  være en god model for det måntlige overskuffet (i tusen kroner)")

    # Print svar-setninger
    for svar in svar_a_liste: print(svar)

# b) Størst overskudd
if _blokk == 1:

    # Definerer uttrykket for overskudds-funksjonen, O
    O = -0.041*x**2 + 11*x - 103

    # Deriverer O mhp. x og får dO = 11 - 0.082*x
    dO = diff(O, x) # O'(x)

    # Løser likningen dO = 0 
    x_max = superløs(variabel = x,
                     vs       = dO,
                     hs       = 0,
                     rund     = None,
                     debug    = -1)

    # Svar-setninger
    svar_b_liste = list()
    svar_b_liste.append(f"")
    svar_b_liste.append(f"Oppg b)")
    svar_b_liste.append(f"")
    svar_b_liste.append(f"- Negativ a-koeffisient gir et toppunkt på O")
    svar_b_liste.append(f"- Produksjonsmengden x = {x_max} gir størst overskudd")

    # Print svar-setninger
    for svar in svar_b_liste: print(svar)
