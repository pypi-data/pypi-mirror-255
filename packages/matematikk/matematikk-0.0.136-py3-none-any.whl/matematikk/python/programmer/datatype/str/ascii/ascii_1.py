# 🚀 programmering.no | 🤓 matematikk.as
# - Se ascii-symbolene til hver char i en string

# Verdier
string = "Apple"

# Funksjon som printer ascii-symbolene til hver char i stringen
def ascii_print(string):

    # Print
    print("--------------")
    print("Char <-> ASCII")
    print("--------------")

    # Loop gjennom chars i stringen
    for char in string:
        ascii = ord(char)
        print(f"{char} <-> {ascii}")

# Print ascii-symboler
ascii_print(string)
