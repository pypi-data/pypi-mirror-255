# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Udir)
# Oppgave 5 Grensekostnaden K'(x) til bedrift 

def K(x):
	return 0.1*x**2 + 100*x + 9000

grense = 200
h = 0.0001
a = 1

while (K(a + h) - K(a))/h < grense:
    a = a + 1

print(a)
