# 🚀 programmering.no | 🤓 matematikk.as
# - Finn alle fibonacci-tallene til og med posisjon n
# - Fibonacci-rekken genereres av formelen F(n) = F(n-2) + F(n-1)
# - De første fibonacci-tallene er 0, 1, 1, 2, 3, 5, 8, 13, 21, ..., n

# Verdier
fib_1 		= 0 		# Det første fibonacci-tallet
fib_2 		= 1 		# Det andre fibonacci-tallet
fib_liste 	= list() 	# Liste med fibonacci-tall
n           = 13        # Til og med tall på posisjon n

# Legg fibonacci-tallet i listen
if int(n) > 0: fib_liste.append(fib_1)
if int(n) > 1: fib_liste.append(fib_2)

# Rekursiv fibonacci-funksjon
def fibonacci_n_liste(n):

	# Type cast inp-str -> int
	n = int(n)

	# Ikke definert
	if n < 1:
		print("n (posisjon) må være et heltall")
		return "Ikke definert"

	# Det første fibonacci-tallet
	elif n <= len(fib_liste):
		return fib_liste[n -1]

	# Regn ut det n`te fibonacci-tallet rekursivt
	else:

		# Rekursiv formel for fibonacci-tall
		fib_n = fibonacci_n_liste(n - 1) + fibonacci_n_liste(n - 2)

		# Legg til og print fibonacci-listen
		fib_liste.append(fib_n)

		return fib_n

# Fibonacci-liste
fibonacci_n_liste(n)

# Print
print(f"Fibonacci-liste: {fib_liste}")
