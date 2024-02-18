# 🚀 programmering.no | 🤓 matematikk.as
# 1T - Eksamen - 2022 Høst (Udir)
# Oppgave 3 b) Rasjonal funksjon til Lars - if else 

def f(x):
	return (1 - 2 * x) / (x - 2)

x = 8

while x >= -8:

    if x == 2: print(x, "Ikke definert: x = 2 deler på 0")
    else: print(x, f(x))

    x = x - 1
