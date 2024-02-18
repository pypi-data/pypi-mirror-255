# 🚀 programmering.no | 🤓 matematikk.as
# - En pyramiden bygges av kvadratiske lag
# - Det er 10 000 klosser tilgjengelig
# - 1) Finn antall klosser i fig. nr n
# - 2) Finn totalt antall klosser til og med fig nr n
# - 3) Finn ut hvor mange pyramider som kan lages

# Verdier
ant_max      = 10000    # Antall klosser tilgjengelig
ant_fig      = 0        # Antall klosser i nåværende figur nr. n
ant_totalt   = 0        # Antall klosser totalt til og med figur nr. n
n            = 1        # Figur nr.

# Iterer så lenge totalt antall klosser er mindre eller lik 10000
while ant_totalt <= ant_max:

    # Oppdater antall klosser i nåværende figur nr. og total bruk
    ant_fig      += n**2
    ant_totalt   += ant_fig

    # Print nåværende resultater (før n inkrementeres)
    print("")
    print(f"Fig nr : {n}")
    print(f"I fig  : {ant_fig}")
    print(f"Totalt : {ant_totalt}")

    # Inkrementer n (etter print)
    n += 1
