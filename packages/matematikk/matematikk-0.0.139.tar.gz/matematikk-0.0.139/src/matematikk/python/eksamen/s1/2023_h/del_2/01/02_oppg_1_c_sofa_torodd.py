# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Torodd)
# Oppgave 1 c) Sofa-produksjon til møbelfabrikk - Minst salgspris 

from sympy import Symbol, diff, Eq, Reals, solveset

_blokk = 1

if _blokk == 1:

    # definerer symboler
    x = Symbol("x")
    a = Symbol("a")

    # definerer K(x) og I(x). Ny pris = a.
    K = 0.041*x**2 + 17*x + 103
    I = a*x

    # Bestemmer O(x)
    O = I - K

    # Finn likning for ekstremalpunktet til O
    vs = diff(O, x)
    hs = 0

    # set opp likninga, og løyser ho
    likning = Eq(vs, hs)
    løysing = solveset(likning, x, domain=Reals)
    løysing # <--- Slett?

if _blokk == 1:

    # definerer x-verdien til ekstremalpunktet uttrykt ved a
    x_topp = 12.2*a - 207.3

    # finn O(x_topp)
    nyO = O.subs(x, x_topp)

    # Sett opp likning for O(x_topp)=1000
    vs = nyO
    hs = 1000

    # set opp likninga, og løyser ho
    likning = Eq(vs, hs)
    løysing = solveset(likning, a, domain=Reals)

if _blokk == 1:

    a1 = 3.55
    a2 = 30.45

    x1 = x_topp.subs(a, a1).evalf()
    x2 = x_topp.subs(a, a2).evalf()

    print(f"Pris på {a1*1000} kr gjev x = {x1:.0f}")
    print(f"Pris på {a2*1000} kr gjev x = {x2:.0f}")
