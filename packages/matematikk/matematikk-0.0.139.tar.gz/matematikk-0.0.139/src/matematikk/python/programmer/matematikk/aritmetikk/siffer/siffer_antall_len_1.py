# 🚀 programmering.no | 🤓 matematikk.as
# - Finn antall siffer i et heltall

# Verdier
n = 371

# Regner ut antall siffer i heltallet n
def siffer_antall_len(n):

    # Eks: str(371) -> "371" => len("371") = 3 (siffer)
    siffer_ant = len(str(n))

    return siffer_ant

# Antall siffer i heltallet n
siffer_ant = siffer_antall_len(n)

# Print
print(f"Antall siffer i {n} er: {siffer_ant}")
