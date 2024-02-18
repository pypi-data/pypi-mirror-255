# 🚀 programmering.no | 🤓 matematikk.as

from matematikk import Symbol, polyfit

def reggis(variabel = Symbol(""),
           grad     = int(),
           x_liste  = list(),
           y_liste  = list(),
           rund     = -1):

    # - Lager polynom-funksjon av valgfri grad vha. regresjon (CAS)

    # Variabler
    _koeff_liste       = list()                # Liste med koeffesienter i fra polyfit()
    _koeff             = float()               # Polynomets koeffisienter
    _ledd              = Symbol("_ledd")       # Polynomets ledd
    _ledd_grad         = int()                 # Polynomets ledd inkludert grad
    _uttrykk           = Symbol("_uttrykk")    # Polynomets uttrykk (hs)

    # polyfit() returnerer en liste med regresjons-koeffesientene
    _koeff_liste = polyfit(x_liste, y_liste, grad)

    # Hver iterasjon lager det neste leddet i polynomet
    for i in range(len(_koeff_liste)):

        # - På 1. iterasjon må _uttrykk nulles ut slik at det ikke blir en
        #   egen variabel i uttrykket, f.eks. "_uttrykk + 0.04*x**2 + 17.05*x + 102.7"
        if i == 0: _uttrykk = 0

        # Runder av koeffesienten
        if rund == -1: _koeff = _koeff_liste[i]
        if rund != -1: _koeff = round(_koeff_liste[i], rund)

        # Lager leddene i fra størst til minst grad
        _ledd_grad = grad - i

        # Formaterer leddene
        if _ledd_grad >= 2: _ledd = _koeff * variabel**_ledd_grad
        if _ledd_grad == 1: _ledd = _koeff * variabel
        if _ledd_grad == 0: _ledd = _koeff

        # Legger det nye leddet til polynomet
        _uttrykk += _ledd

    return _uttrykk


# Alias > 1
reggis_cas                  = reggis
regresjon                   = reggis
regresjon_cas               = reggis
regresjon_polynom           = reggis
regresjon_polynom_cas       = reggis

# Alias > 2
cas_regresjon               = reggis
cas_regresjon_polynom       = reggis
regresjon_polynom_cas       = reggis
