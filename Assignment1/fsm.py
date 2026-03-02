# -------------------------------------------------------------
# fsm.py
# 
# Contains the Finite State Machine (FSM) functions used by the lexer to
# recognize identifiers, integers, and real numbers.
# -------------------------------------------------------------
import utils


#----is_identifier--------------------------------------------
# Determines whether the token is an indentifier.
#
# Output:
#       Return Boolean: 1 = True, -1 = False
#--------------------------------------------------------------
def is_identifier(token):
    #[a-zA-Z][a-zA-Z0-9_]*
    # Initial state
    state = 0
    # Goes through each character
    for char in token:
        # State -1, the check has already failed so no need to check the rest of the token
        if state == -1:
            break
        # State 0, looking for [a-zA-Z]
        elif state == 0:
            if char.isalpha():
                state = 1
            else:
                state = -1
        # State 1, looking for [a-zA-Z0-9_]*
        elif state == 1:
            if char.isalpha() or char.isdigit() or char == '_':
                state = 1
            else:
                state = -1
    # Accepting state
    return state == 1
#--------------------------------------------------------------


#----is_integer------------------------------------------------
# Determines whether the token is an integer.
#
# Output:
#       Return Boolean: 1 = True, -1 = False  
#--------------------------------------------------------------
def is_integer(token):
    #[0-9]+
    # Initial state
    state = 0
    # Goes through each character
    for char in token:
        # State -1, the check has already failed so no need to check the rest of the token
        if state == -1:
            break
        # State 0, looking for [0-9]
        elif state == 0:
            if char.isdigit():
                state = 1
            else:
                state = -1
        # State 1, looking for [0-9]+
        elif state == 1:
            if char.isdigit():
                state = 1
            else:
                state = -1
    # Accepting state
    return state == 1

#--------------------------------------------------------------


#----is_real------------------------------------------------
# Determines whether the token is a real/double/float.
#
# Output:
#       Return Boolean: 3 = True 
#--------------------------------------------------------------
def is_real(token):
    #[0-9]+/.[0-9]+
    # Initial state
    state = 0
    # Goes through each character
    for char in token:
        # State -1, the check has already failed so no need to check the rest of the token
        if state == -1:
            break
        # State 0, looking for [0-9]
        elif state == 0:
            if char.isdigit():
                state = 1
            else:
                state = -1
        # State 1, looking for [0-9]+ or .
        elif state == 1:
            if char.isdigit():
                state = 1
            elif char == '.':
                state = 2
            else:
                state = -1
        # State 2, looking for [0-9]
        elif state == 2:
            if char.isdigit():
                state = 3
            else:
                state = -1
        # State 3, looking for [0-9]+
        elif state == 3:
            if char.isdigit():
                state = 3
            else:
                state = -1
    # Accepting state
    return state == 3

#--------------------------------------------------------------


#----is_keyword------------------------------------------------
# Determines whether the token is a keyword.
#
# Output:
#       Return Boolean: True/False  
#--------------------------------------------------------------
def is_keyword(token):
    # Checks if given token is in KEYWORDS list from utils
    return token in utils.KEYWORDS
#--------------------------------------------------------------


#----is_operator-----------------------------------------------
# Determines whether the token is an operator.
#
# Output:
#       Return Boolean: True/False  
#--------------------------------------------------------------
def is_operator(token):
    # Checks if given token is in KEYWORDS list from utils
    return token in utils.OPERATORS
#--------------------------------------------------------------


#----is_separator----------------------------------------------
# Determines whether the token is a separator.
#
# Output:
#       Return Boolean: True/False  
#--------------------------------------------------------------
def is_separator(token):
    # Checks if given token is in KEYWORDS list from utils
    return token in utils.SEPARATORS
#--------------------------------------------------------------