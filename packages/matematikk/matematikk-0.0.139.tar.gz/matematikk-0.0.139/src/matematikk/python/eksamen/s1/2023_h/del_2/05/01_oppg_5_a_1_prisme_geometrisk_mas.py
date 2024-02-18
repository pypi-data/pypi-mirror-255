# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 5 a) Volum av prisme - Største volum dersom sidene i bunnen er 5 dm (geometrisk løsning) 

import random

# Konstanter
_blokk = 1 # 0: Av, 1: På, Skjul/debug deler av koden med if-blokker

# Definerer funksjoner
def prisme_volum_max_fra_areal_geo(lengde = float(),
                                   dybde  = float(),
                                   A_max  = float(),
                                   rund   = 2):

    # Regner geometrisk ut volum av prisme når areal_maks, lengde og dybde er gitt

    # Skisse av kassen
    if _blokk == -1:
        #                    |------------
        #                    | .	       .
        #                    |  -	   V    -
        #                    |   .------------
        #                    _   |			 |
        #                     .  |	   A     |   hoyde
        #             dybde     _|			 |
        #                        .------------
        # 
        #                            lengde
        pass

    # Regner ut det samlede arealet til veggene 
    areal_vegger = A_max - (lengde * dybde)

    # Regner ut arealet til 1 av de 4 veggene 
    areal_vegg = areal_vegger / 4

    # Regner ut høyden fra areal_vegg = dybde * hoyde 
    hoyde = areal_vegg / dybde

    # Regner ut maksimalt volum 
    volum_max = lengde * dybde * hoyde

    # Runder av svaret
    volum_max = round(volum_max, rund)

    return volum_max

# a) Største volum dersom sidene i bunnen er 5 dm (geometrisk løsning)
if _blokk == 1:

    # Regner ut vha. den motsatte sannsynligheten
    volum_max = prisme_volum_max_fra_areal_geo(lengde = 5,
                                               dybde  = 5,
                                               A_max  = 120,
                                               rund   = 2)

    # Print svar-setninger
    svar_a_0 = f"Oppg a)"
    svar_a_1 = f"- Det største volumet kassen kan ha er {volum_max} dm^3"
    print("")
    print(svar_a_0)
    print(svar_a_1)
