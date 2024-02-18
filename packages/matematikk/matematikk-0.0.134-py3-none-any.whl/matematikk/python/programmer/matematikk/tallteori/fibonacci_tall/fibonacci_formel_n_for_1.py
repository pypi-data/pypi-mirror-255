# 🚀 programmering.no | 🤓 matematikk.as
# - Se om tallet på posisjon n er et fibonacci-tall
# - Fibonacci-rekken genereres av formelen F(n) = F(n-2) + F(n-1)
# - De første fibonacci-tallene er 0, 1, 1, 2, 3, 5, 8, 13, 21, ..., n

# Verdier
n = 12

# Funksjon for å finne fibonacci-tallet med for-løkke
def fibonacci_n_for_loop(n):

	# Verdier
	fib_n_1 = 0   # Det første fibonacci-tallet
	fib_n_2 = 1   # Det andre fibonacci-tallet

	# Type cast inp-str -> int
	n = int(n)

	# Ikke definert
	if n < 1:

		# Print feilmelding
		print("n (posisjon) må være et heltall")

		return "Ikke definert"

	# Det første fibonacci-tallet
	elif n == 1: return fib_n_1

	# Det andre fibonacci-tallet
	elif n == 2: return fib_n_2

	# Regn ut det n`te fibonacci-tallet med for-løkke
	else:

		# Generer det neste fibonacci-tallet for hver iterasjon
		for _ in range(2, n):
			fib_n_3 = fib_n_1 + fib_n_2
			fib_n_1 = fib_n_2
			fib_n_2 = fib_n_3

		return fib_n_2

# Fibonacci-tall
fib_n = fibonacci_n_for_loop(n)

# Print
print(f"Fibonacci-tallet på posisjon n = {n} er: {fib_n}")
