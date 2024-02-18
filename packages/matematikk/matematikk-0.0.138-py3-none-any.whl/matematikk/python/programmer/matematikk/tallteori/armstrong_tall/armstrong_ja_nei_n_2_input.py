# 🚀 programmering.no | 🤓 matematikk.as
# - Se om tallet er et armstrong-tall
# - Def: I et armstrong-tall er summen av siffrene
#   opphøyd i antall siffer lik tallet
# - Eks: 371 => 3 siffer
#   3^(3) + 7^(3) + 1^(3) = 27 + 343 + 1 = 371

# Input
n = input("Se om tallet er et armstrong tall: ")

# Funksjon for å se om tallet er et armstrong-tall
def er_armstrong_tall(n):

    # Variabler
    n               = int(n)        # Type cast inp-str -> int
    n_kopi          = n             # Kopier startverdien til n
    siffer_ant      = len(str(n))   # Eks: str(371) -> "371" => len("371") = 3 (siffer)
    sum             = 0             # Nullstill

    # Itererer gjennom sifrene i n (stop når n = 0)
    while n != 0:

        # Få det bakerste sifferet med modulus 10 (resten av å dele på 10)
        siffer = n % 10 # Eks: 371 % 10 = 1 fordi 371 / 10 = 370 (heltall) + 1 (rest)

        # Oppdater sum for hver iterasjon
        sum = sum + (siffer**siffer_ant)

        # n / 10 => Få det neste bakerste sifferet
        n = int(n / 10) # Eks: 371 (3 siffer) / 10 = 37.1 => int(37.1) = 37 (2 siffer) => ... => int(3.7) = 3 (1 siffer)

    # Se om sum er lik opprinnelig verdi til n
    if sum == n_kopi: print(f"Er {n_kopi} et armstrong-tall? Ja")
    else:             print(f"Er {n_kopi} et armstrong-tall? Nei")

# Armstrong-tall eller ikke
er_armstrong_tall(n)
