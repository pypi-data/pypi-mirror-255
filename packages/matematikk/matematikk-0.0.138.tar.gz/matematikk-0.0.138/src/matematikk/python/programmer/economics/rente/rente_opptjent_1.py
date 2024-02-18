# 🚀 programmering.no | 🤓 matematikk.as
# - Regn ut opptjent rente med vekstfaktor

# Verdier
belop_start   = 200   # Startbeløp
perioder_ant  = 3     # Antall perioder
rente_prosent = 10    # Rente (%)

# Vekstfaktor
vekstfaktor = 1 + (rente_prosent / 100)
belop_total = belop_start * vekstfaktor**perioder_ant

# Opptjent rente
rente_opptjent = belop_total - belop_start

# Print
print(f"Startbeløp      : {belop_start}")
print(f"Antall perioder : {perioder_ant}")
print(f"Rente (%)       : {rente_prosent} %")
print(f"Vekstfaktor     : {vekstfaktor}")
print(f"Opptjent rente  : {rente_opptjent}")
