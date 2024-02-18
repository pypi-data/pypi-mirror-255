# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 5 a) Volum av prisme - Største volum dersom sidene i bunnen er 5 dm (løsning med likninger) 

from sympy import Eq, Reals, Symbol, solveset

# Konstanter
_blokk = 1 # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker

# Definerer funksjoner
def los_sett(variabel = Symbol(""),
             vs       = Symbol(""),
             hs       = Symbol(""),
             rund     = None):

    # Lager likningen med Eq(vs, hs) 
    likning = Eq(vs, hs)

    # Løser likningen for aktuell variabel med solveset() og får løsnings-settet på formen {1234.56789}
    losning_set = solveset(likning, variabel, domain = Reals) # Løsnings-domene i ℝ (Reals)

    # Henter elementet i fra løsnings-settet, f.eks. 1234.56789
    losning = losning_set.args[0] # [0] er første element (det eneste her)

    # Runder av f.eks. 1234.56789 -> 1234.6
    losning = round(losning, rund)

    return losning

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
    A                  = Symbol("A")   # Arealet av platene
    A_max          = 120           # Maksimalt arealet av platene
    s                  = Symbol("s")   # Sidene i den kvadratiske grunnflaten
    s_5                = 5             # Lengden på sidene
    h                  = Symbol("h")   # Prismets høyde

    # Definerer uttrykkene for A og V
    A = s**2 + 4*s*h
    V = s**2 * h

    # Setter s = 5 inn i A og definerer det nye uttrykket som A_5 (slik at ikke A skrives over) 
    A_5 = A.subs(s, s_5)

    # Løser likningen 120 = 5**2 + 4*5*h 
    h_losning = los_sett(vs       = A_max,
                         hs       = A_5,
                         variabel = h,
                         rund     = 2)

    # Setter h = -(s + 5)/4 inn i V og definerer det nye uttrykket som V_uttrykk 
    V_max = V.subs(s, s_5).subs(h, h_losning) # Bruker .subs flere ganger etter hverandre ("chain rule")

    # Print svar-setninger
    svar_a_0 = f"Oppg a)"
    svar_a_1 = f"- Det største volumet kassen kan ha er {V_max} dm^3"
    print("")
    print(svar_a_0)
    print(svar_a_1)
