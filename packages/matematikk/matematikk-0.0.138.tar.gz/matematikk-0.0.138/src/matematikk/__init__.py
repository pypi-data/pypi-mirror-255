# Versjon: 0.0.133

# Chain 5 mal
from ._ch_1.ch_2.ch_3.ch_4_fil import ch_5_fn

# numpy()
from numpy import(
    polyfit
    )

# sympy()
from sympy import (
    ConditionSet,
    core,
    diff,
    Eq,
    FiniteSet,
    Intersection,
    nsolve,
    Reals,
    solve,
    solveset,
    Symbol
    )

# vekstfaktor_cas()
from .python.funksjoner.matematikk.funksjoner.eksponentialfunksjoner.vekstfaktor.def_vekstfaktor_cas import (
    vekstfaktor_cas
    )

# reggis()
from .python.funksjoner.matematikk.regresjon.polynom.reggis.def_reggis_matematikk_mas import (
    reggis,

    # Alias > 1
    reggis_cas,
    regresjon,
    regresjon_cas,
    regresjon_polynom,
    regresjon_polynom_cas,

    # Alias > 2
    cas_regresjon,
    cas_regresjon_polynom,
    regresjon_polynom_cas
    )

# superlos()
from .python.funksjoner.matematikk.likninger.superlos.def_superlos_matematikk_mas import (
    superløs,

    # Alias > 1
    los,
    losning,
    løs,
    løsning,
    superlos,
    super_los,
    super_løs,

    # Alias > 2
    los_super,
    løs_super
    )

# ekstremalpunkt_max()
from .python.funksjoner.matematikk.funksjoner._drøfting.ekstremalpunkt.def_ekstremalpunkt_max_mas import (
    ekstremalpunkt_max,

    # Alias > 1
    ekstremalpunkt_maks,
    ekstremalpunkt_maksimalt,
    toppunkt

    # Alias > 2 > ...
    )

# overskudd_max()
from .python.funksjoner.matematikk.funksjoner._drøfting.ekstremalpunkt.def_overskudd_max_mas import (
    overskudd_max,

    # Alias > 1
    overskudd_maks,
    overskudd_maksimalt,
    overskudd_mest,
    overskudd_storst,
    overskudd_størst,

    # Alias > 2
    maks_overskudd,
    maksimalt_overskudd,
    mest_overskudd,
    storst_overskudd,
    størst_overskudd
    )
