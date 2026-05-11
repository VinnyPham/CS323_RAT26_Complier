# -------------------------------------------------------------
# parser.py
# 
# Contains the Syntax Analyzer which checks if the token stream
# from the lexical analyzer adheres to the language's formal 
# grammar rules. Also performs semantic actions to generate
# machine instructions and populate the symbol table.
# -------------------------------------------------------------
import sys
import lexer
from symbol_table import add_identifier, lookup_identifier, symbol_table

# -------------------------------------------------------------
# Instruction Table
# -------------------------------------------------------------
instruction_table = []
instr_address     = 1

def gen_instr(op, operand=None):
    """Append one instruction; return its address."""
    global instr_address
    addr = instr_address
    instruction_table.append((addr, op, operand if operand is not None else "nil"))
    instr_address += 1
    return addr

def back_patch(jump_addr, target):
    """Fill in an unresolved jump target."""
    for i, (a, op, _) in enumerate(instruction_table):
        if a == jump_addr:
            instruction_table[i] = (a, op, target)
            return

def print_instruction_table(output):
    output.write("\nInstruction Table\n")
    output.write(f"{'Address':<10}{'Operator':<14}{'Operand'}\n")
    for addr, op, operand in instruction_table:
        output.write(f"{addr:<10}{op:<14}{operand}\n")


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

        # Stack of unresolved JUMPZ addresses for if/while back-patching
        self._jump_stack = []

        self._advance()

    # -- Internal helpers -------------------------------------- 
    
    def _advance(self):
        tok, self.pos = lexer.lexer(self.code, self.pos)
        self.token = tok
    
    def _current_lexeme(self):
        return self.token["lexeme"] if self.token else "EOF"
    
    def _current_token(self):
        return self.token["token"] if self.token else "EOF"
    
    def _write(self, text):
        print(text)
        self.output.write(text + "\n")
    
    def _print_token(self):
        if self.token:
            self._write(f"\tToken: {self._current_token():<12}  Lexeme: {self._current_lexeme()}")
    
    def _print_rule(self, rule):
        if self.print_rules:
            self._write(f"\t{rule}")
    
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
    
    def _match(self, expected_lexeme):
        if self.token and self._current_lexeme() == expected_lexeme:
            self._print_token()
            self._advance()
        else:
            self._error(f"'{expected_lexeme}'")
    
    def _match_token(self, expected_token):
        if self.token and self._current_token() == expected_token:
            self._print_token()
            self._advance()
        else:
            self._error(expected_token)

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

    def parse(self):
        self._print_rule("<Rat26S> -> @ <Opt Function Definitions> @ <Opt Declaration List> @ <Statement List> @")
        self._match("@")
        self.parse_opt_function_definitions()
        self._match("@")
        self.parse_opt_declaration_list()
        self._match("@")
        self.parse_statement_list()
        self._match("@")

        # Print the generated instruction table
        print_instruction_table(self.output)

    # -- Function definitions ---------------------------------

    def parse_opt_function_definitions(self):
        self._print_rule("<Opt Function Definitions> -> <Function Definitions> | <Empty>")
        if self.token and self._current_lexeme() == "function":
            self.parse_function_definitions()
        else:
            self.parse_empty()
    
    def parse_function_definitions(self):
        self._print_rule("<Function Definitions> -> <Function> <Function Definitions Prime>")
        self.parse_function()
        self.parse_function_definitions_prime()

    def parse_function_definitions_prime(self):
        self._print_rule("<Function Definitions Prime> -> <Function Definitions> | <Empty>")
        if self.token and self._current_lexeme() == "function":
            self.parse_function_definitions()
        else:
            self.parse_empty()
    
    def parse_function(self):
        self._print_rule("<Function> -> function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>")
        self._match("function")
        # Register the function name so call sites can reference it
        func_name = self._current_lexeme()
        add_identifier(func_name, "function")
        self._match_token("identifier")
        self._match("(")
        self.parse_opt_parameter_list()
        self._match(")")
        self.parse_opt_declaration_list()
        self.parse_body()

    # -- Parameters --------------------------------------------

    def parse_opt_parameter_list(self):
        self._print_rule("<Opt Parameter List> -> <Parameter List> | <Empty>")
        if self.token and self._current_token() == "identifier":
            self.parse_parameter_list()
        else:
            self.parse_empty()

    def parse_parameter_list(self):
        self._print_rule("<Parameter List> -> <Parameter> <Parameter List Prime>")
        self.parse_parameter()
        self.parse_parameter_list_prime()

    def parse_parameter_list_prime(self):
        self._print_rule("<Parameter List Prime> -> , <Parameter List> | <Empty>")
        if self.token and self._current_lexeme() == ",":
            self._match(",")
            self.parse_parameter_list()
        else:
            self.parse_empty()

    def parse_parameter(self):
        self._print_rule("<Parameter> -> <IDs> <Qualifier>")
        # Peek at the qualifier that follows the identifier(s) so we can
        # declare each parameter in the symbol table with the correct type.
        # We collect the identifier lexeme(s) first, then consume the qualifier.
        param_lex = self._current_lexeme()
        self.parse_ids()                        # consumes identifier(s)
        data_type = self._current_lexeme()      # qualifier is now current token
        self.parse_qualifier()                  # consumes qualifier
        add_identifier(param_lex, data_type)    # declare in symbol table

    # -- Qualifier ---------------------------------------------

    def parse_qualifier(self):
        self._print_rule("<Qualifier> -> integer | boolean | real")
        if self._is_qualifier():
            self._print_token()
            self._advance()
        else:
            self._error("qualifier (integer | boolean | real)")

    # -- Body --------------------------------------------------

    def parse_body(self):
        self._print_rule("<Body> -> { <Statement List> }")
        self._match("{")
        self.parse_statement_list()
        self._match("}")

    # -- Declarations ------------------------------------------

    def parse_opt_declaration_list(self):
        self._print_rule("<Opt Declaration List> -> <Declaration List> | <Empty>")
        if self._is_qualifier():
            self.parse_declaration_list()
        else:
            self.parse_empty()

    def parse_declaration_list(self):
        self._print_rule("<Declaration List> -> <Declaration> <Declaration List Prime>")
        self.parse_declaration()
        self.parse_declaration_list_prime()

    def parse_declaration_list_prime(self):
        self._print_rule("<Declaration List Prime> -> <Declaration List> | <Empty>")
        if self._is_qualifier():
            self.parse_declaration_list()
        else:
            self.parse_empty()

    def parse_declaration(self):
        self._print_rule("<Declaration> -> <Qualifier> <IDs> ;")
        data_type = self._current_lexeme()
        self.parse_qualifier()
        self.parse_ids(declare=True, data_type=data_type)
        self._match(";")

    # -- IDs ---------------------------------------------------
    
    def parse_ids(self, declare=False, data_type=None):
        self._print_rule("<IDs> -> <Identifier> <IDs Prime>")
        if declare:
            add_identifier(self._current_lexeme(), data_type)
        self._match_token("identifier")
        self.parse_ids_prime(declare, data_type=data_type)

    def parse_ids_prime(self, declare=False, data_type=None):
        self._print_rule("<IDs Prime> -> , <IDs> | <Empty>")
        if self.token and self._current_lexeme() == ",":
            self._match(",")
            self.parse_ids(declare, data_type)
        else:
            self.parse_empty()

    # -- Statements --------------------------------------------

    def parse_statement_list(self):
        self._print_rule("<Statement List> -> <Statement> <Statement List Prime>")
        self.parse_statement()
        self.parse_statement_list_prime()

    def parse_statement_list_prime(self):
        self._print_rule("<Statement List Prime> -> <Statement List> | <Empty>")
        if self._is_statement_start():
            self.parse_statement_list()
        else:
            self.parse_empty()
    
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

    def parse_compound(self):
        self._print_rule("<Compound> -> { <Statement List> }")
        self._match("{")
        self.parse_statement_list()
        self._match("}")

    # Semantic: after expression is on the stack, POPM into the variable's address.
    def parse_assign(self):
        self._print_rule("<Assign> -> <Identifier> = <Expression> ;")
        lex = self._current_lexeme()
        if not lookup_identifier(lex):
            self._write(f"\n*** Semantic Error ***\n  '{lex}' was not declared.\n")
            sys.exit(1)
        self._match_token("identifier")
        self._match("=")
        self.parse_expression()
        addr = symbol_table[lex]["memory_location"]
        gen_instr("POPM", addr)
        self._match(";")

    # Semantic: condition emits compare + JUMPZ (unresolved); back-patched in parse_if_prime.
    def parse_if(self):
        self._print_rule("<If> -> if ( <Condition> ) <Statement> <If Prime>")
        self._match("if")
        self._match("(")
        self.parse_condition()
        self._match(")")
        self.parse_statement()
        self.parse_if_prime()

    def parse_if_prime(self):
        self._print_rule("<If Prime> -> otherwise <Statement> fi | fi")
        if self.token and self._current_lexeme() == "otherwise":
            # Emit JUMP to skip the else-branch after the then-branch runs
            jump_over_else = gen_instr("JUMP", None)
            # JUMPZ from condition lands at the start of the else-branch
            back_patch(self._jump_stack.pop(), instr_address)
            self._match("otherwise")
            self.parse_statement()
            self._match("fi")
            # JUMP from end of then-branch lands after the else-branch
            back_patch(jump_over_else, instr_address)
        elif self.token and self._current_lexeme() == "fi":
            # No else — JUMPZ lands right after the then-branch
            back_patch(self._jump_stack.pop(), instr_address)
            self._match("fi")
        else:
            self._error("'fi' or 'otherwise'")

    def parse_return(self):
        self._print_rule("<Return> -> return <Return Prime>")
        self._match("return")
        self.parse_return_prime()

    def parse_return_prime(self):
        self._print_rule("<Return Prime> -> ; | <Expression> ;")
        if self.token and self._current_lexeme() == ";":
            self._match(";")
        else:
            self.parse_expression()
            self._match(";")
        gen_instr("RET")

    # Semantic: expression result on stack -> STDOUT prints it.
    def parse_print(self):
        self._print_rule("<Print> -> write ( <Expression> ) ;")
        self._match("write")
        self._match("(")
        self.parse_expression()
        gen_instr("STDOUT")
        self._match(")")
        self._match(";")

    # Semantic: STDIN reads a value; POPM stores it in the variable.
    def parse_scan(self):
        self._print_rule("<Scan> -> read ( <IDs> ) ;")
        self._match("read")
        self._match("(")
        self._parse_ids_read()
        self._match(")")
        self._match(";")

    def _parse_ids_read(self):
        """Like parse_ids but emits STDIN + POPM for each variable."""
        lex = self._current_lexeme()
        if not lookup_identifier(lex):
            self._write(f"\n*** Semantic Error ***\n  '{lex}' was not declared.\n")
            sys.exit(1)
        self._match_token("identifier")
        addr = symbol_table[lex]["memory_location"]
        gen_instr("STDIN")
        gen_instr("POPM", addr)
        if self.token and self._current_lexeme() == ",":
            self._match(",")
            self._parse_ids_read()

    # Semantic: save loop-top address; JUMP back at end; JUMPZ exits loop.
    def parse_while(self):
        self._print_rule("<While> -> while ( <Condition> ) <Statement>")
        self._match("while")
        loop_top = instr_address
        self._match("(")
        self.parse_condition()
        self._match(")")
        self.parse_statement()
        gen_instr("JUMP", loop_top)
        back_patch(self._jump_stack.pop(), instr_address)

    # -- Condition / Relational OP------------------------------

    # Semantic: pushes both operands, emits compare instr, then unresolved JUMPZ.
    def parse_condition(self):
        self._print_rule("<Condition> -> <Expression> <Relop> <Expression>")
        self.parse_expression()
        relop = self._current_lexeme()
        self.parse_relop()
        self.parse_expression()
        op_map = {"==": "EQL", "!=": "NEQ", ">": "GRT", "<": "LES", ">=": "GEQ", "<=": "LEQ"}
        gen_instr(op_map.get(relop, "EQL"))
        self._jump_stack.append(gen_instr("JUMPZ", None))

    def parse_relop(self):
        self._print_rule("<Relop> -> == | != | > | < | <= | >=")
        if self.token and self._current_lexeme() in ("==", "!=", ">", "<", "<=", ">="):
            self._print_token()
            self._advance()
        else:
            self._error("relational operator (== != > < <= >=)")

    # -- Expressions -------------------------------------------
    
    def parse_expression(self):
        self._print_rule("<Expression> -> <Term> <Expression Prime>")
        self.parse_term()
        self.parse_expression_prime()

    # Semantic: emit ADD or SUB after each additional term.
    def parse_expression_prime(self):
        self._print_rule("<Expression Prime> -> + <Term> <Expression Prime> | - <Term> <Expression Prime> | <Empty>")
        if self.token and self._current_lexeme() in ("+", "-"):
            op = self._current_lexeme()
            self._print_token()
            self._advance()
            self.parse_term()
            gen_instr("ADD" if op == "+" else "SUB")
            self.parse_expression_prime()
        else:
            self.parse_empty()
    
    def parse_term(self):
        self._print_rule("<Term> -> <Factor> <Term Prime>")
        self.parse_factor()
        self.parse_term_prime()

    # Semantic: emit MUL or DIV after each additional factor.
    def parse_term_prime(self):
        self._print_rule("<Term Prime> -> * <Factor> <Term Prime> | / <Factor> <Term Prime> | <Empty>")
        if self.token and self._current_lexeme() in ("*", "/"):
            op = self._current_lexeme()
            self._print_token()
            self._advance()
            self.parse_factor()
            gen_instr("MUL" if op == "*" else "DIV")
            self.parse_term_prime()
        else:
            self.parse_empty()

    # Semantic: unary minus -> emit PUSHI -1 + MUL after the primary.
    def parse_factor(self):
        self._print_rule("<Factor> -> - <Primary> | <Primary>")
        negate = self.token and self._current_lexeme() == "-"
        if negate:
            self._match("-")
        self.parse_primary()
        if negate:
            gen_instr("PUSHI", -1)
            gen_instr("MUL")
        
    # Semantic: push the value onto the stack.
    def parse_primary(self):
        self._print_rule("<Primary> -> <Identifier> <Primary Prime> | <Integer> | <Real> | ( <Expression> ) | true | false")
        if not self.token:
            self._error("primary expression")

        tok = self._current_token()
        lex = self._current_lexeme()

        if tok == "identifier":
            if not lookup_identifier(lex):
                self._write(f"\n*** Semantic Error ***\n  '{lex}' was not declared.\n")
                sys.exit(1)
            addr = symbol_table[lex]["memory_location"]
            self._print_token()
            self._advance()
            gen_instr("PUSHM", addr)
            self.parse_primary_prime()
        elif tok == "integer":
            self._print_token()
            self._advance()
            gen_instr("PUSHI", int(lex))
        elif tok == "real":
            self._print_token()
            self._advance()
            gen_instr("PUSHR", float(lex))
        elif lex == "(":
            self._match("(")
            self.parse_expression()
            self._match(")")
        elif lex in ("true", "false"):
            self._print_token()
            self._advance()
            gen_instr("PUSHI", 1 if lex == "true" else 0)
        else:
            self._error("primary (identifier, integer, real, '(', true, false)")
    
    def parse_primary_prime(self):
        self._print_rule("<Primary Prime> -> ( <IDs> ) | <Empty>")
        if self.token and self._current_lexeme() == "(":
            self._match("(")
            self.parse_ids()
            self._match(")")
        else:
            self.parse_empty()

    # -- Epsilon -----------------------------------------------
    
    def parse_empty(self):
        self._print_rule("<Empty> -> e")