# -------------------------------------------------------------
# symbol_table.py
# 
# Contains the symbol table and functions to check if a lexeme
# exists within it, adding to the symbol table, and printing
# the symbol table to the output file 
# -------------------------------------------------------------

import sys

memory_address = 10000
# Empty dictionary for storing all symbols
symbol_table = {}

# Returns if a specific lexeme exists in the symbol_table
def lookup_identifier(lexeme):
    return lexeme in symbol_table

# Adds an idenitifer to the table
def add_identifier(lexeme, data_type):
    global memory_address
    # Checks if lexeme was already declared and gives an error if it has
    if lexeme in symbol_table:
        print(f"Error: '{lexeme}' was already declared.")
        sys.exit(1)
    # Otherwise, adds it to the table
    symbol_table[lexeme] = {
        "memory_location": memory_address,
        "type": data_type
    }
    memory_address += 1

# Prints entire table to output file
def print_symbol_table(output):
   output.write("\nSymbol Table\n")
   output.write("Identifier\tMemoryLocation\tType\n")

   for lexeme, info in symbol_table.items():
       output.write(f"{lexeme:<12}{info['memory_location']:<16}{info['type']:<10}\n")