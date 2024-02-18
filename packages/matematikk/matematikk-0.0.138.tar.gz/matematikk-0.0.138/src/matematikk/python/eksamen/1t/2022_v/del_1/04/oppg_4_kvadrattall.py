# 🚀 programmering.no | 🤓 matematikk.as
# 1T - Eksamen - 2022 Vår (Udir)
# Oppgave 4 a) Kvadrattallene fra 1 til 160 000 - Forklar koden 

def f(x):
	return x ** 2   # Definerer funksjonen f gitt ved f(x) = x ^ 2

x = 1

while x <= 400:
    print(f(x))
    x = x + 1
