# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Torodd)
# Oppgave 6 a) Tredjegradsfunksjon - Påstand 1: Grafen f har minst ett ekstremalpunkt 

from sympy import symbols, diff, solve, solveset, Eq, Reals

# Grafen til f har minst ett ekstremalpunkt
# Hvis f skal ha minst ett ekstremalpunkt må f`ha minst ett nullpunkt

# definerer symboler
x, a, b, c, d = symbols("x a b c d")

# definerer f
f = a*x**3 + b*x**2 + c*x + d

# deriverer f
df = diff(f, x)

# finn nullpunkta til f'(x)
løysingar = solveset(Eq(df, 0), x, domain=Reals)
print(løysingar)
