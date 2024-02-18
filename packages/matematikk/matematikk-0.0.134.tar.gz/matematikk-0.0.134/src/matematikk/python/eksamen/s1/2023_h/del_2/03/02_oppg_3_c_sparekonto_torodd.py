# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Torodd)
# Oppgave 3 c) Sparekonto - År før totalt innskudd er fordoblet 

from sympy import Symbol, Eq, nsolve

# definerer symboler
x = Symbol("x")

# Finn likning
vs = 1.03**x + 1.06**x
hs = 4

# set opp likninga, og løyser ho numerisk
likning = Eq(vs, hs)
løysing = nsolve(likning, x, 1)
print(løysing)
