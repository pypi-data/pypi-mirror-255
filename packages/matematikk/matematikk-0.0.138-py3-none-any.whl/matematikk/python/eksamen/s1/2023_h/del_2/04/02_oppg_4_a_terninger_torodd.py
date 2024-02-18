# 🚀 programmering.no | 🤓 matematikk.as
# S1 - Eksamen - 2023 Høst (Torodd)
# Oppgave 5 a) Sannsynlighet med 5 terninger - Sannsynligheten for minst 2 av 5 terningene er like 

# gunstige / moglege utfall
ingen_like = (6*5*4*3*2) / (6**5)

minst_to_like = 1 - ingen_like

print(f"P(minst to like) = {minst_to_like:.4f}")
