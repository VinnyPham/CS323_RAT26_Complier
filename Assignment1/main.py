# -------------------------------------------------------------
# Project: CPSC 323 – Assignment 3
# -------------------------------------------------------------
# Programmers: Vinny Pham, Brandon Schaefer, Vanna Cervania
# Titan Email: vinnypham327@csu.fullerton.edu
#              schaeferbrandon@csu.fullerton.edu
#              vannaflocervania@csu.fullerton.edu
# Date: May 10, 2026
# -------------------------------------------------------------
import parser
from symbol_table import print_symbol_table


def main():
    input_file  = "test1_input.txt"
    output_file = "test1_output.txt"
 
    # Read source code
    try:
        with open(input_file, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return
 
    # Run the parser 
    with open(output_file, "w") as out:
        p = parser.Parser(code, out, print_rules=False)
        p.parse()
 
        out.write("=" * 60 + "\n")
        out.write("Parsing completed successfully.\n")

        print_symbol_table(out)
        out.write("=" * 60 + "\n")
        out.write("Machine code completed successfully.\n")

 
    print(f"Parsing complete. Output written to '{output_file}'.")
 
if __name__ == "__main__":
    main()