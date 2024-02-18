# 🚀 programmering.no | 🤓 matematikk.as
# - Se om tallet på posisjon n er et fibonacci-tall
# - Fibonacci-rekken genereres av formelen F(n) = F(n-2) + F(n-1)
# - De første fibonacci-tallene er 0, 1, 1, 2, 3, 5, 8, 13, 21, ..., n

# Verdier
fib_1 = 0   # Det første fibonacci-tallet
fib_2 = 1   # Det andre fibonacci-tallet

# Input
n = 8

# Rekursiv fibonacci-funksjon
def fibonacci_n_rekursiv(n):

	# Type cast inp-str -> int
	n = int(n)

	# Ikke definert
	if n < 1:

		# Print feilmelding
		print("n (posisjon) må være et heltall")

		return "Ikke definert"

	# Det første fibonacci-tallet
	elif n == 1: return fib_1

	# Det andre fibonacci-tallet
	elif n == 2: return fib_2

	# Regn ut det n`te fibonacci-tallet rekursivt
	else: return fibonacci_n_rekursiv(n - 1) + fibonacci_n_rekursiv(n - 2)

# Fibonacci-tall
fib_n = fibonacci_n_rekursiv(n)

# Print
print(f"Fibonacci-tallet på posisjon n = {n} er: {fib_n}")
