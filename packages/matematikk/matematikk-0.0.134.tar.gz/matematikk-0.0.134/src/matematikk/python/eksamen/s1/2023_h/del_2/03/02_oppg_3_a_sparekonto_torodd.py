# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Torodd)
# Oppgave 3 a) Sparekonto - Finn innskuddet til Per 

from sympy import Symbol, Eq, Reals, solveset

# definerer symboler
x = Symbol("x")

# Finn likning
vs = x * 1.03**8
hs = 30000

# set opp likninga, og løyser ho
likning = Eq(vs, hs)
løysing = solveset(likning, x, domain=Reals)

print(løysing)
