# -------------------------------------------------------------
# parser.py
# 
# Contains the Syntax Analyzer which checks if the token stream
# from the lexical analyzer adheres to the language’s formal 
# grammar rules.
# -------------------------------------------------------------
import sys
import lexer 

# -------------------------------------------------------------
# Parser Class
# -------------------------------------------------------------
class Parser:
    def __init__(self, source_code, output_file, print_rules=True):
        self.code        = source_code
        self.pos         = 0
        self.token       = None
        self.output      = output_file
        self.print_rules = print_rules
 
        self._advance()
 
    # -- Internal helpers -------------------------------------- 
    
    # Pulls the next token from lexer
    def _advance(self):
        tok, self.pos = lexer.lexer(self.code, self.pos)
        self.token = tok
    
    # Gets current lexeme
    def _current_lexeme(self):
        return self.token["lexeme"] if self.token else "EOF"
    
    # Gets current token
    def _current_token(self):
        return self.token["token"] if self.token else "EOF"
    
    # Writes a line to output file
    def _write(self, text):
        print(text)
        self.output.write(text + "\n")
    
    # Print current token/lexeme pair
    def _print_token(self):
        if self.token:
            self._write(f"\tToken: {self._current_token():<12}  Lexeme: {self._current_lexeme()}")
    
    # Print production rule
    def _print_rule(self, rule):
        if self.print_rules:
            self._write(f"\t{rule}")
    
    # Report sytnax error
    def _error(self, expected):
        tok = self._current_token()
        lex = self._current_lexeme()
        msg = (
            f"\n*** Syntax Error ***\n"
            f"  Expected : {expected}\n"
            f"  Found    : token='{tok}'  lexeme='{lex}'\n"
        )
        self._write(msg)
        sys.exit(1)
    
    # Consumes current token if lexeme matches
    def _match(self, expected_lexeme):
        if self.token and self._current_lexeme() == expected_lexeme:
            self._print_token()
            self._advance()
        else:
            self._error(f"'{expected_lexeme}'")
    
    # Consumes current token if token matches
    def _match_token(self, expected_token):
        if self.token and self._current_token() == expected_token:
            self._print_token()
            self._advance()
        else:
            self._error(expected_token)
 
    # -- First-set helpers -------------------------------------
    
    def _is_qualifier(self):
        return self.token and self._current_lexeme() in ("integer", "real", "boolean")
 
    def _is_statement_start(self):
        if not self.token:
            return False
        lex = self._current_lexeme()
        tok = self._current_token()
        return (lex in ("{", "if", "return", "write", "read", "while")
                or tok == "identifier")
 
    # ---------------------------------------------------------
    # Grammar productions
    # ---------------------------------------------------------
 
    # Syntax Parser
    def parse(self):
        self._print_rule("<Rat26S> -> @ <Opt Function Definitions> @ <Opt Declaration List> @ <Statement List> @")
        self._match("@")
        self.parse_opt_function_definitions()
        self._match("@")
        self.parse_opt_declaration_list()
        self._match("@")
        self.parse_statement_list()
        self._match("@")
 
    # -- Function definitions ---------------------------------
 
    # <Opt Function Definitions> -> <Function Definitions> | <Empty>
    def parse_opt_function_definitions(self):
        self._print_rule("<Opt Function Definitions> -> <Function Definitions> | <Empty>")
        if self.token and self._current_lexeme() == "function":
            self.parse_function_definitions()
        else:
            self.parse_empty()
    
    # <Function Definitions> -> <Function> <Function Definitions Prime>
    def parse_function_definitions(self):
        self._print_rule("<Function Definitions> -> <Function> <Function Definitions Prime>")
        self.parse_function()
        self.parse_function_definitions_prime()
 
    # <Function Definitions Prime> -> <Function Definitions> | <Empty>
    def parse_function_definitions_prime(self):
        self._print_rule("<Function Definitions Prime> -> <Function Definitions> | <Empty>")
        if self.token and self._current_lexeme() == "function":
            self.parse_function_definitions()
        else:
            self.parse_empty()
    
    # <Function> -> function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>
    def parse_function(self):
        self._print_rule("<Function> -> function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>")
        self._match("function")
        self._match_token("identifier")
        self._match("(")
        self.parse_opt_parameter_list()
        self._match(")")
        self.parse_opt_declaration_list()
        self.parse_body()
 
    # -- Parameters --------------------------------------------

    # <Opt Parameter List> -> <Parameter List> | <Empty>
    def parse_opt_parameter_list(self):
        self._print_rule("<Opt Parameter List> -> <Parameter List> | <Empty>")
        if self.token and self._current_token() == "identifier":
            self.parse_parameter_list()
        else:
            self.parse_empty()

    # <Parameter List> -> <Parameter> <Parameter List Prime>
    def parse_parameter_list(self):
        self._print_rule("<Parameter List> -> <Parameter> <Parameter List Prime>")
        self.parse_parameter()
        self.parse_parameter_list_prime()
 
    # <Parameter List Prime> -> , <Parameter List> | <Empty>
    def parse_parameter_list_prime(self):
        self._print_rule("<Parameter List Prime> -> , <Parameter List> | <Empty>")
        if self.token and self._current_lexeme() == ",":
            self._match(",")
            self.parse_parameter_list()
        else:
            self.parse_empty()

    # <Parameter> -> <IDs> <Qualifier>
    def parse_parameter(self):
        self._print_rule("<Parameter> -> <IDs> <Qualifier>")
        self.parse_ids()
        self.parse_qualifier()
 
    # -- Qualifier ---------------------------------------------
 
    # <Qualifier> -> integer | boolean | real
    def parse_qualifier(self):
        self._print_rule("<Qualifier> -> integer | boolean | real")
        if self._is_qualifier():
            self._print_token()
            self._advance()
        else:
            self._error("qualifier (integer | boolean | real)")
 
    # -- Body --------------------------------------------------
 
    # <Body> -> { <Statement List> }
    def parse_body(self):
        self._print_rule("<Body> -> { <Statement List> }")
        self._match("{")
        self.parse_statement_list()
        self._match("}")
 
    # -- Declarations ------------------------------------------

    # <Opt Declaration List> -> <Declaration List> | <Empty>
    def parse_opt_declaration_list(self):
        self._print_rule("<Opt Declaration List> -> <Declaration List> | <Empty>")
        if self._is_qualifier():
            self.parse_declaration_list()
        else:
            self.parse_empty()
 
    # <Declaration List> -> <Declaration> <Declaration List Prime>
    def parse_declaration_list(self):
        self._print_rule("<Declaration List> -> <Declaration> <Declaration List Prime>")
        self.parse_declaration()
        self.parse_declaration_list_prime()

    # <Declaration List Prime> -> <Declaration List> | <Empty>
    def parse_declaration_list_prime(self):
        self._print_rule("<Declaration List Prime> -> <Declaration List> | <Empty>")
        if self._is_qualifier():
            self.parse_declaration_list()
        else:
            self.parse_empty()
 
    # <Declaration> -> <Qualifier> <IDs> ;
    def parse_declaration(self):
        self._print_rule("<Declaration> -> <Qualifier> <IDs> ;")
        self.parse_qualifier()
        self.parse_ids()
        self._match(";")
 
    # -- IDs ---------------------------------------------------
    
    # <IDs> -> <Identifier> <IDs Prime>
    def parse_ids(self):
        self._print_rule("<IDs> -> <Identifier> <IDs Prime>")
        self._match_token("identifier")
        self.parse_ids_prime()
 
    # <IDs Prime> -> , <IDs> | <Empty>
    def parse_ids_prime(self):
        self._print_rule("<IDs Prime> -> , <IDs> | <Empty>")
        if self.token and self._current_lexeme() == ",":
            self._match(",")
            self.parse_ids()
        else:
            self.parse_empty()
 
    # -- Statements --------------------------------------------

    # <Statement List> -> <Statement> <Statement List Prime>
    def parse_statement_list(self):
        self._print_rule("<Statement List> -> <Statement> <Statement List Prime>")
        self.parse_statement()
        self.parse_statement_list_prime()
 
    # <Statement List Prime> -> <Statement List> | <Empty>
    def parse_statement_list_prime(self):
        self._print_rule("<Statement List Prime> -> <Statement List> | <Empty>")
        if self._is_statement_start():
            self.parse_statement_list()
        else:
            self.parse_empty()
    
    # <Statement> -> <Compound> | <Assign> | <If> | <Return> | <Print> | <Scan> | <While>
    def parse_statement(self):
        self._print_rule("<Statement> -> <Compound> | <Assign> | <If> | <Return> | <Print> | <Scan> | <While>")
        if not self.token:
            self._error("statement")
 
        lex = self._current_lexeme()
        tok = self._current_token()
 
        if lex == "{":
            self.parse_compound()
        elif tok == "identifier":
            self.parse_assign()
        elif lex == "if":
            self.parse_if()
        elif lex == "return":
            self.parse_return()
        elif lex == "write":
            self.parse_print()
        elif lex == "read":
            self.parse_scan()
        elif lex == "while":
            self.parse_while()
        else:
            self._error("statement (compound, assign, if, return, write, read, while)")
 
    # <Compound> -> { <Statement List> }
    def parse_compound(self):
        self._print_rule("<Compound> -> { <Statement List> }")
        self._match("{")
        self.parse_statement_list()
        self._match("}")
 
    # <Assign> -> <Identifier> = <Expression> ;
    def parse_assign(self):
        self._print_rule("<Assign> -> <Identifier> = <Expression> ;")
        self._match_token("identifier")
        self._match("=")
        self.parse_expression()
        self._match(";")
 
    # <If> -> if ( <Condition> ) <Statement> <If Prime>
    def parse_if(self):
        self._print_rule("<If> -> if ( <Condition> ) <Statement> <If Prime>")
        self._match("if")
        self._match("(")
        self.parse_condition()
        self._match(")")
        self.parse_statement()
        self.parse_if_prime()
 
    # <If Prime> -> otherwise <Statement> fi | fi
    def parse_if_prime(self):
        self._print_rule("<If Prime> -> otherwise <Statement> fi | fi")
        if self.token and self._current_lexeme() == "otherwise":
            self._match("otherwise")
            self.parse_statement()
            self._match("fi")
        elif self.token and self._current_lexeme() == "fi":
            self._match("fi")
        else:
            self._error("'fi' or 'otherwise'")
 
    # <Return> -> return <Return Prime>
    def parse_return(self):
        self._print_rule("<Return> -> return <Return Prime>")
        self._match("return")
        self.parse_return_prime()
 
    # <Return Prime> -> ; | <Expression> ;
    def parse_return_prime(self):
        self._print_rule("<Return Prime> -> ; | <Expression> ;")
        if self.token and self._current_lexeme() == ";":
            self._match(";")
        else:
            self.parse_expression()
            self._match(";")
 
    # <Print> -> write ( <Expression> ) ;
    def parse_print(self):
        self._print_rule("<Print> -> write ( <Expression> ) ;")
        self._match("write")
        self._match("(")
        self.parse_expression()
        self._match(")")
        self._match(";")
 
    # <Scan> -> read ( <IDs> ) ;
    def parse_scan(self):
        self._print_rule("<Scan> -> read ( <IDs> ) ;")
        self._match("read")
        self._match("(")
        self.parse_ids()
        self._match(")")
        self._match(";")
 
    # <While> -> while ( <Condition> ) <Statement>
    def parse_while(self):
        self._print_rule("<While> -> while ( <Condition> ) <Statement>")
        self._match("while")
        self._match("(")
        self.parse_condition()
        self._match(")")
        self.parse_statement()
 
    # -- Condition / Relational OP------------------------------

    # <Condition> -> <Expression> <Relop> <Expression>
    def parse_condition(self):
        self._print_rule("<Condition> -> <Expression> <Relop> <Expression>")
        self.parse_expression()
        self.parse_relop()
        self.parse_expression()
 
    # <Relop> -> == | != | > | < | <= | >=
    def parse_relop(self):
        self._print_rule("<Relop> -> == | != | > | < | <= | >=")
        if self.token and self._current_lexeme() in ("==", "!=", ">", "<", "<=", ">="):
            self._print_token()
            self._advance()
        else:
            self._error("relational operator (== != > < <= >=)")
 
    # -- Expressions -------------------------------------------
    
    # <Expression> -> <Term> <Expression Prime>
    def parse_expression(self):
        self._print_rule("<Expression> -> <Term> <Expression Prime>")
        self.parse_term()
        self.parse_expression_prime()
 
    # <Expression Prime> -> + <Term> <Expression Prime> | - <Term> <Expression Prime> | <Empty>
    def parse_expression_prime(self):
        self._print_rule("<Expression Prime> -> + <Term> <Expression Prime> | - <Term> <Expression Prime> | <Empty>")
        if self.token and self._current_lexeme() in ("+", "-"):
            self._print_token()
            self._advance()
            self.parse_term()
            self.parse_expression_prime()
        else:
            self.parse_empty()
    
    # <Term> -> <Factor> <Term Prime>
    def parse_term(self):
        self._print_rule("<Term> -> <Factor> <Term Prime>")
        self.parse_factor()
        self.parse_term_prime()
 
    # <Term Prime> -> * <Factor> <Term Prime> | / <Factor> <Term Prime> | <Empty>
    def parse_term_prime(self):
        self._print_rule("<Term Prime> -> * <Factor> <Term Prime> | / <Factor> <Term Prime> | <Empty>")
        if self.token and self._current_lexeme() in ("*", "/"):
            self._print_token()
            self._advance()
            self.parse_factor()
            self.parse_term_prime()
        else:
            self.parse_empty()
 
    # <Factor> -> - <Primary> | <Primary>
    def parse_factor(self):
        self._print_rule("<Factor> -> - <Primary> | <Primary>")
        if self.token and self._current_lexeme() == "-":
            self._match("-")
        self.parse_primary()
        
    # <Primary> -> <Identifier> <Primary Prime> | <Integer> | <Real> | ( <Expression> ) | true | false
    def parse_primary(self):
        self._print_rule("<Primary> -> <Identifier> <Primary Prime> | <Integer> | <Real> | ( <Expression> ) | true | false")
        if not self.token:
            self._error("primary expression")
 
        tok = self._current_token()
        lex = self._current_lexeme()
 
        if tok == "identifier":
            self._print_token()
            self._advance()
            self.parse_primary_prime()
        elif tok == "integer":
            self._print_token()
            self._advance()
        elif tok == "real":
            self._print_token()
            self._advance()
        elif lex == "(":
            self._match("(")
            self.parse_expression()
            self._match(")")
        elif lex in ("true", "false"):
            self._print_token()
            self._advance()
        else:
            self._error("primary (identifier, integer, real, '(', true, false)")
    
    # <Primary Prime> -> ( <IDs> ) | <Empty>
    def parse_primary_prime(self):
        self._print_rule("<Primary Prime> -> ( <IDs> ) | <Empty>")
        if self.token and self._current_lexeme() == "(":
            self._match("(")
            self.parse_ids()
            self._match(")")
        else:
            self.parse_empty()
 
    # -- Epsilon -----------------------------------------------
    
    # <Empty> -> e
    def parse_empty(self):
        self._print_rule("<Empty> -> e")
 