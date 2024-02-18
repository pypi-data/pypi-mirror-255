# 🚀 programmering.no | 🤓 matematikk.as
# - Se om intervallet har armstrong-tall
# - Def: I et armstrong-tall er summen av siffrene
#   opphøyd i antall siffer lik tallet
# - Eks: 371 => 3 siffer
#   3^(3) + 7^(3) + 1^(3) = 27 + 343 + 1 = 371

# Input
min = input("Min verdi: ")
max = input("Max verdi: ")

# Nullstill
armstrong_liste = list()

# Funksjon for å se om intervallet har armstrong-tall
def er_armstrong_tall_intervall(min, max):

    # Itererer gjennom intervallet
    for n in range(int(min), int(max) + 1):

        # Variabler
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
        if sum == n_kopi: armstrong_liste.append(n_kopi)

    return armstrong_liste

# Armstrong-liste
armstrong_liste = er_armstrong_tall_intervall(min, max)

# Print
print(f"Armstrong-liste: {armstrong_liste}")
