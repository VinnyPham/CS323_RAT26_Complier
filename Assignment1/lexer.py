# -------------------------------------------------------------
# lexer.py
# 
# The lexer scans the input source code and returns tokens with their
# corresponding lexemes (keyword, identifier, integer, real, operator, separator).
# -------------------------------------------------------------
import fsm


#----lexer-----------------------------------------------------
# Process the string into tokens. 
#
# Output:
#       Returns Dict: token - indentiy, Int: i 
#--------------------------------------------------------------
def lexer(code, i):
    while i < len(code):
        char = code[i]

        # skip whitespace
        if char.isspace():
            i += 1
            continue

        # skip comments: /* ... */
        if code[i:i+2] == '/*':
            end = code.find('*/', i + 2)
            if end == -1:
                return None, len(code)
            i = end + 2
            continue

        # skip comments: // or #
        if code[i:i+2] == '//' or code[i] == '#':
            end = code.find('\n', i)
            if end == -1:
                return None, len(code)
            i = end + 1
            continue

        # operators (<=, >=, ==, !=)
        if i + 1 < len(code) and fsm.is_operator(code[i:i+2]):
            return {"token": "operator", "lexeme": code[i:i+2]}, i + 2

        # operators (+, -, *, /, %, <, >, =)
        if fsm.is_operator(char): 
            return {"token": "operator", "lexeme": char}, i + 1

        # separator (), {}, [], :, ;, ,
        if fsm.is_separator(char):
            return {"token": "operator", "lexeme": char}, i + 1

        # identifiers / keywords
        if char.isalpha():
            j = i
            while j < len(code) and (code[j].isalnum() or code[j] == '_'):
                j += 1
                
            lexeme = code[i:j]
            
            if fsm.is_keyword(lexeme):
                return {"token": "keyword", "lexeme": lexeme}, j
            else:
                return {"token": "identifier", "lexeme": lexeme}, j

        # numbers (int / real) 
        if char.isdigit():
            j = i
            has_dot = False
            
            while j < len(code) and (code[j].isdigit() or (code[j] == '.' and not has_dot)):
                if code[j] == '.':
                    has_dot = True
                j += 1
                
            lexeme = code[i:j]
            
            if fsm.is_real(lexeme):
                return {"token": "real", "lexeme": lexeme}, j
            elif fsm.is_integer(lexeme):
                return {"token": "integer", "lexeme": lexeme}, j
            else:
                return {"token": "unknown", "lexeme": lexeme}, j

        # unknown
        return {"token": "unknown", "lexeme": char}, i + 1

    # End of file
    return None, i
