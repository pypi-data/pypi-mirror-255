# 🚀 programmering.no | 🤓 matematikk.as
# - Se om tallet på posisjon n er et fibonacci-tall
# - Fibonacci-rekken genereres av formelen F(n) = F(n-2) + F(n-1)
# - De første fibonacci-tallene er 0, 1, 1, 2, 3, 5, 8, 13, 21, ..., n
# - Newtons metode definerer det første fibonacci-tallet som 1 (og ikke 0)
#   Vi kan forskyve rekken med m = n - 1 slik at dette likevel blir 0

from math import sqrt

# Input
n = input("Finn fibonacci-tallet på posisjon (n): ")

# Funksjon for å finne fibonacci-tallet med Newtons metode
def fibonacci_n_newton(n):

	# Verdier
	fib_n_1 = 0 # Det første fibonacci-tallet

	# Type cast inp-str -> int
	n = int(n)

	# Ikke definert
	if n < 1:

		# Print feilmelding
		print("n (posisjon) må være et heltall")

		return "Ikke definert"

	# Det første fibonacci-tallet
	elif n == 1: return fib_n_1

	# Regn ut det n`te fibonacci-tallet med Newtons metode
	else:

		# Posisjonen til det forrige fibonacci-tallet
		m = n - 1

		# Formel for Newtons metode
		fib_n = ((1 + sqrt(5))**m - (1 - sqrt(5))**m) / (2**m*sqrt(5))

		return int(fib_n)

# Fibonacci-tall
fib_n = fibonacci_n_newton(n)

# Print
print(f"Fibonacci-tallet på posisjon n = {n} er: {fib_n}")
