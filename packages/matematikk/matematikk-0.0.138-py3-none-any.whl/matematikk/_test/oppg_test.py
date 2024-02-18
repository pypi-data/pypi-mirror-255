# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Matematikk AS)
# Oppgave 1 b) Sofa-produksjon til møbelfabrikk - Størst overskudd 
# - Løser oppgaven med CAS i Python
# - Kopier kommandoen i terminalen og importer matematikk 
#   $ pip install matematikk

from matematikk import overskudd_max, reggis, Symbol

# a) Finn O(x)
K = reggis(variabel = Symbol("x"),
           grad     = 2,
           x_liste  = [10, 25, 40, 70, 100, 140, 180],
           y_liste  = [270, 550, 870, 1500, 2200, 3300, 4500],
           rund     = 2)
print(K)

# b) Størst overskudd
x_max = overskudd_max(variabel = Symbol("x"),
                      uttrykk  = -0.041*Symbol("x")**2 + 11*Symbol("x") - 103,
                      rund     = None,
                      debug    = -1)
print(x_max)
