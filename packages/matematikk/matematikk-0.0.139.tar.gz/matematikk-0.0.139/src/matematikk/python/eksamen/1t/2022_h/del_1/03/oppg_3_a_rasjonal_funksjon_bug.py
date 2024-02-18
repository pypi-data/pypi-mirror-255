# 🚀 programmering.no | 🤓 matematikk.as
# 1T - Eksamen - 2022 Høst (Udir)
# Oppgave 3 a) Rasjonal funksjon til Lars - Finn buggen i koden til Lars 

# Funksjonen
def f(x):
	return (1 - 2 * x) / (x - 2)

x = 8

while x >= -8 :

    print(x , f(x))
    x = x - 1
