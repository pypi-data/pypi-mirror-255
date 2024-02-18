# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Torodd)
# Oppgave 1 b) Sofa-produksjon til møbelfabrikk - Størst overskudd 

from sympy import Symbol, diff, Eq, Reals, solveset

# definerer x
x = Symbol("x")

O = -0.041*x**2 +11*x -103

# definerer vs og hs av likninga
vs = diff(O)    #O'(x)
hs = 0

# set opp likninga, og løyser ho
likning = Eq(vs, hs)
løysing = solveset(likning, x, domain=Reals)

# skriv ut svaret
print(f"x = {løysing.evalf(4)}")
