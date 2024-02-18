# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Torodd)
# Oppgave 6 a) Tredjegradsfunksjon - Påstand 1: Grafen f har minst ett ekstremalpunkt 

from sympy import symbols, limit, oo

# definerer funksjonen og symbola
x, a, b, c, d = symbols("x a b c d")
f = a*x**3 + b*x**2 + c*x + d

# grense mot uendeleg
limit(f, x, oo)

# grense mot minus uendeleg
løsning = limit(f, x, -oo)
print(løsning)
