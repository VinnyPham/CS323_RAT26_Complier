# -------------------------------------------------------------
# Project: CPSC 323 – Assignment 1
# -------------------------------------------------------------
# Programmers: Vinny Pham, Brandon Schaefer, Vanna Cervania
# Titan Email: vinnypham327@csu.fullerton.edu
#              schaeferbrandon@csu.fullerton.edu
#              vannaflocervania@csu.fullerton.edu
# Date: March 01, 2026
# -------------------------------------------------------------
import lexer


def main():
    input_file = "test3_input.txt" 
    output_file = "test3_output.txt" 

    # Open and read the file
    try:
        with open(input_file, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return
    
        
    # Write the contents to the output file
    try:
        with open(output_file, "w") as f:
            f.write("Output:\n")
            f.write(f"{'token':<12} {'lexeme'}\n")
            
            # Convert code into token
            token = {}
            i = 0
            while i < len(code):
                token, i = lexer.lexer(code, i)
                # Stops when lexer finishes
                if token is None:
                    break
                f.write(f"{token['token']:<12} {token['lexeme']}\n")
                
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")
        return

    print(f"Contents of {input_file} have been written to {output_file}.")
    
if __name__ == "__main__":
    main()