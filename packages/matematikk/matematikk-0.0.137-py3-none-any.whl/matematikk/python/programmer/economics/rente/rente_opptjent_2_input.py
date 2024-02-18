# 🚀 programmering.no | 🤓 matematikk.as
# - Regn ut opptjent rente med vekstfaktor

# Verdier
belop_start = input("Startbeløp: ")   # Startbeløp
perioder_ant = input("Antall perioder: ")     # Antall perioder
rente_prosent = input("Rente (%): ")    # Rente (%)

# Vekstfaktor
vekstfaktor = 1 + (float(rente_prosent) / 100)
belop_total = float(belop_start) * vekstfaktor**float(perioder_ant)

# Opptjent rente
rente_opptjent = belop_total - float(belop_start)

# Print
print(f"Startbeløp      : {belop_start}")
print(f"Antall perioder : {perioder_ant}")
print(f"Rente (%)       : {rente_prosent} %")
print(f"Vekstfaktor     : {vekstfaktor}")
print(f"Opptjent rente  : {rente_opptjent}")
