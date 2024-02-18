# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 1 a) Sofa-produksjon til møbelfabrikk - Finn O(x) 
# - Lager polynom-funksjon av valgfri grad vha. regresjon (CAS)
# - Kopier kommandoen i terminalen og importer matematikk (CAS)
#   $ pip install matematikk

from matematikk import reggis, Symbol

# a) Finn O(x)
K = reggis(variabel = Symbol("x"),
           grad     = 2,
           x_liste  = [10, 25, 40, 70, 100, 140, 180],
           y_liste  = [270, 550, 870, 1500, 2200, 3300, 4500],
           rund     = 2)

print(K)

