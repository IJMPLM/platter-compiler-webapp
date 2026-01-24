from app.lexer.lexer import Lexer
from app.parser.predict_set import PREDICT_SET
from app.parser.predict_set_err import PREDICT_SET_ERR
from app.parser.ast_nodes import ParseNode
from tests.test_parser_util import run_file
import logging as log                                      

# To disable logs, set level=log.CRITICAL. 
# To enable logs, set level=log.DEBUG
log.basicConfig(level=log.DEBUG, format='%(levelname)s: <%(funcName)s> | %(message)s')

class Parser:

    def __init__(self, tokens):
        """ Token Stream """
        self.tokenlist = [t for t in tokens if t.type not in ("space", "tab", "newline", "comment_single", "comment_multi")] # filter out ws and comments
        self.result = True
        self.ast = None  # Root of the parse tree

        """ Properties """
        self.tokens = [t.type for t in self.tokenlist]
        self.tokens_length = len(self.tokens)-1
        self.pos = 0

        """ Token Attributes """
        if self.tokens: # catch for empty tokens
            self.current_tok = self.tokens[self.pos] 
            self.current_line = self.tokenlist[self.pos].line 
            self.current_col = (self.tokenlist[self.pos].col) 
        else:
            self.current_tok = None
            self.current_line = None
            self.current_col = None


    def parse_token(self, tok):
        if self.current_tok == tok: 
            log.warning(f"Expected: {tok} | Current: {self.current_tok} | Remark: MATCH!")
            # print(f"├──Expected: {tok} | Current: {self.current_tok} | Remark: MATCH!")
            
            # Create node with current token info before advancing
            token_obj = self.tokenlist[self.pos]
            node = ParseNode(tok, token=token_obj)
            
            self.advance(tok)
            return node
        else:
            log.warning(f"Expected: {tok} | Current: {self.current_tok} | Remark: INVALID!\n")
            # print(f"└──Expected: {tok} | Current: {self.current_tok} | Remark: INVALID!")
            self.result = False
            self.error_handler("Unexpected_err", tok)

    def advance(self, tok): 
        if self.pos < self.tokens_length:
            self.pos += 1
            self.upd_tok_attr()
            log.warning(f"Consuming: {tok} -> {self.current_tok}\n")
            # print(f"└──Consuming: {tok} -> {self.current_tok}")
        else: 
            self.current_tok = "EOF" # end of token list, EOF reached
            # print(f"└──Consuming: {tok} -> {self.current_tok}")
            log.warning(f"Consuming: {tok} -> EOF\n")
            # raise SyntaxError (f"Syntax Error: Expected '{tok}' but got {self.current_tok}")

    def upd_tok_attr(self):
        self.current_tok = self.tokens[self.pos] 
        self.current_line = self.tokenlist[self.pos].line
        self.current_col = self.tokenlist[self.pos].col

    def error_handler(self, error_type, tok, expected_toklist=None):        
        errors = {
            "Parse_err": f"Syntax Error: Program empty. Expected {tok}.",
            "Unexpected_err": f"Syntax Error: Unexpected '{self.current_tok}' at line {self.current_line}, col {self.current_col}. Expected {tok}.",
            
            "Program_err": f"Syntax Error: Program cannot begin with token '{self.current_tok}'. Expected a declaration or 'prepare/start'",
            "ExpectedEOF_err": f"Syntax Error: Unexpected token '{self.current_tok}' after start platter, Expected EOF (line {self.current_line}, col {self.current_col})",
            "Invalid_err": f"Syntax Error: Invalid {tok} at line {self.current_line}, col {self.current_col}.",
            "Invalid_err1": f"Syntax Error: Invalid {tok} at line {self.current_line}, col {self.current_col}. Expected {expected_toklist}",
            "Missing_err": f"Syntax Error: Missing {tok} at line {self.current_line}, col {self.current_col}",
            "Custom_err": f"Syntax Error: {tok} (line {self.current_line}, col {self.current_col})",
        }
        self.result = False
        raise SyntaxError(errors[error_type])

    # CFG Parsing Methods 

    def parse(self):
        if self.tokenlist:
            self.ast = self.program()
        else: self.error_handler("Parse_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<program>"])))
        return self.ast

    def program(self):
        log.info("Enter: " + self.current_tok)
        node = ParseNode("<program>")
        
        if self.current_tok in PREDICT_SET_ERR["<program>"]:
            if self.current_tok in PREDICT_SET["<program>"]:
                node.add_child(self.global_decl())
            if self.current_tok in PREDICT_SET["<recipe_decl>"]:
                node.add_child(self.recipe_decl())
            node.add_child(self.parse_token("start"))
            node.add_child(self.parse_token("("))
            node.add_child(self.parse_token(")"))
            node.add_child(self.platter())
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<program>"])))

        # Ensure EOF after parsing
        if self.current_tok != "EOF": self.error_handler("ExpectedEOF_err", None) 
        log.info("Exit: " + self.current_tok)
        return node

    def global_decl(self):
        log.info("Enter: " + self.current_tok)
        node = ParseNode("<global_decl>")
        
        if self.current_tok in PREDICT_SET_ERR["<global_decl>"]:
            if self.current_tok in PREDICT_SET["<global_decl>"]: # if has null in set
                node.add_child(self.decl_data_type())
                node.add_child(self.global_decl())
            if self.current_tok in PREDICT_SET["<global_decl_1>"]:
                node.add_child(self.table_prototype())
                node.add_child(self.global_decl())
            if self.current_tok in PREDICT_SET["<global_decl_2>"]:
                node.add_child(self.parse_token("id"))
                node.add_child(self.table_decl())
                node.add_child(self.global_decl())
            if self.current_tok in PREDICT_SET["<global_decl_3>"]:
                log.info("Exit: " + self.current_tok)
                return node # λ - return node even if empty
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<global_decl>"])))
        log.info("Exit: " + self.current_tok)
        return node

    def decl_data_type(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<decl_data_type>"]: # if no null in set
            if self.current_tok in PREDICT_SET["<decl_data_type>"]:
                self.parse_token("piece")
                self.decl_type()
            if self.current_tok in PREDICT_SET["<decl_data_type_1>"]:
                self.parse_token("sip")
                self.decl_type()
            if self.current_tok in PREDICT_SET["<decl_data_type_2>"]:
                self.parse_token("flag")
                self.decl_type()
            if self.current_tok in PREDICT_SET["<decl_data_type_3>"]:
                self.parse_token("chars")
                self.decl_type()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<decl_data_type>"])))
        log.info("Exit: " + self.current_tok)

    def decl_type(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<decl_type>"]:
            if self.current_tok in PREDICT_SET["<decl_type>"]:
                self.parse_token("of")
                self.ingredient_id()
                self.parse_token(";")
            if self.current_tok in PREDICT_SET["<decl_type_1>"]:
                self.dimensions()
                self.parse_token("of")
                self.array_declare()
                self.parse_token(";")
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<decl_type>"])))
        log.info("Exit: " + self.current_tok)

    def ingredient_id(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<ingredient_id>"]:
            if self.current_tok in PREDICT_SET["<ingredient_id>"]:
                self.parse_token("id")
                self.ingredient_init()
                self.ingredient_id_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<ingredient_id>"])))
        log.info("Exit: " + self.current_tok)
        
    def ingredient_init(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<ingredient_init>"]:
            if self.current_tok in PREDICT_SET["<ingredient_init>"]:
                self.parse_token("=")
                self.expr()
            if self.current_tok in PREDICT_SET["<ingredient_init_1>"]:
                log.info("Exit: " + self.current_tok)
                return # λ
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<ingredient_init>"])))
        log.info("Exit: " + self.current_tok)

    def ingredient_id_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<ingredient_id_tail>"]:
            if self.current_tok in PREDICT_SET["<ingredient_id_tail>"]:
                self.parse_token(",")
                self.parse_token("id")
                self.ingredient_init()
                self.ingredient_id_tail()
            if self.current_tok in PREDICT_SET["<ingredient_id_tail_1>"]:
                log.info("Exit: " + self.current_tok)
                return # λ
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<ingredient_id_tail>"])))
        log.info("Exit: " + self.current_tok)
    
    def expr(self):
        log.info("Enter: " + self.current_tok)
        node = ParseNode("<expr>")
        
        if self.current_tok in PREDICT_SET_ERR["<expr>"]:
            if self.current_tok in PREDICT_SET["<expr>"]:
                node.add_child(self.or_expr())
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<expr>"])))
        log.info("Exit: " + self.current_tok)
        return node
    
    def or_expr(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<or_expr>"]:
            if self.current_tok in PREDICT_SET["<or_expr>"]:
                self.and_expr()
                self.or_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<or_expr>"])))
        log.info("Exit: " + self.current_tok)
    
    def and_expr(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<and_expr>"]:
            if self.current_tok in PREDICT_SET["<and_expr>"]:
                self.eq_expr()
                self.and_tail() 
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<and_expr>"])))
        log.info("Exit: " + self.current_tok)
    
    def or_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET["<or_tail>"]:
            self.parse_token("or")
            self.and_expr()
            self.or_tail()
        if self.current_tok in PREDICT_SET["<or_tail_1>"]:
            log.info("Exit: " + self.current_tok)
            return
        log.info("Exit: " + self.current_tok)
        
    def eq_expr(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<eq_expr>"]:
            if self.current_tok in PREDICT_SET["<eq_expr>"]:
                self.rel_expr()
                self.eq_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<eq_expr>"])))
        log.info("Exit: " + self.current_tok)

    def and_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET["<and_tail>"]:
            self.parse_token("and")
            self.eq_expr()
            self.and_tail()
        if self.current_tok in PREDICT_SET["<and_tail_1>"]:
            log.info("Exit: " + self.current_tok)
            return
        log.info("Exit: " + self.current_tok)
    
    def rel_expr(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<rel_expr>"]:
            if self.current_tok in PREDICT_SET["<rel_expr>"]:
                self.add_expr()
                self.rel_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<rel_expr>"])))
        log.info("Exit: " + self.current_tok)

    def eq_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET["<eq_tail>"]:
            self.parse_token("==")
            self.rel_expr()
            self.eq_tail()
        if self.current_tok in PREDICT_SET["<eq_tail_1>"]:
            self.parse_token("!=")
            self.rel_expr()
            self.eq_tail()
        if self.current_tok in PREDICT_SET["<eq_tail_2>"]:
            log.info("Exit: " + self.current_tok)
            return
        log.info("Exit: " + self.current_tok)

    def add_expr(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<add_expr>"]:
            if self.current_tok in PREDICT_SET["<add_expr>"]:
                self.mult_expr()
                self.add_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<add_expr>"])))
        log.info("Exit: " + self.current_tok)
            
    def rel_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET["<rel_tail>"]:
            self.parse_token(">")
            self.add_expr()
            self.rel_tail()
        if self.current_tok in PREDICT_SET["<rel_tail_1>"]:
            self.parse_token("<")
            self.add_expr()
            self.rel_tail()
        if self.current_tok in PREDICT_SET["<rel_tail_2>"]:
            self.parse_token(">=")
            self.add_expr()
            self.rel_tail()
        if self.current_tok in PREDICT_SET["<rel_tail_3>"]:
            self.parse_token("<=")
            self.add_expr()
            self.rel_tail()
        if self.current_tok in PREDICT_SET["<rel_tail_4>"]:        
            log.info("Exit: " + self.current_tok)
            return
        log.info("Exit: " + self.current_tok)
        
    def mult_expr(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<mult_expr>"]:
            if self.current_tok in PREDICT_SET["<mult_expr>"]:
                self.unary_expr()
                self.mult_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<mult_expr>"])))
        log.info("Exit: " + self.current_tok)

    def add_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET["<add_tail>"]:
            self.parse_token("+")
            self.mult_expr()
            self.add_tail()
        if self.current_tok in PREDICT_SET["<add_tail_1>"]:
            self.parse_token("-")
            self.mult_expr()
            self.add_tail()
        if self.current_tok in PREDICT_SET["<add_tail_2>"]:        
            log.info("Exit: " + self.current_tok)
            return
        log.info("Exit: " + self.current_tok)

    def unary_expr(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<unary_expr>"]:
            if self.current_tok in PREDICT_SET["<unary_expr>"]:
                self.parse_token("not")
                self.unary_expr()
            if self.current_tok in PREDICT_SET["<unary_expr_1>"]:
                self.primary_val()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<unary_expr>"])))
        log.info("Exit: " + self.current_tok)

    def mult_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET["<mult_tail>"]:
            self.parse_token("*")
            self.unary_expr()
            self.mult_tail()
        if self.current_tok in PREDICT_SET["<mult_tail_1>"]:
            self.parse_token("/")
            self.unary_expr()
            self.mult_tail()
        if self.current_tok in PREDICT_SET["<mult_tail_2>"]:
            self.parse_token("%")
            self.unary_expr()
            self.mult_tail()
        if self.current_tok in PREDICT_SET["<mult_tail_3>"]:        
            log.info("Exit: " + self.current_tok)
            return
        log.info("Exit: " + self.current_tok)

    def primary_val(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<primary_val>"]:
            if self.current_tok in PREDICT_SET["<primary_val>"]:
                self.parse_token("(")
                self.expr()
                self.parse_token(")")
            if self.current_tok in PREDICT_SET["<primary_val_1>"]:
                self.parse_token("piece_lit")
                return
            if self.current_tok in PREDICT_SET["<primary_val_2>"]:
                self.parse_token("sip_lit")
                return
            if self.current_tok in PREDICT_SET["<primary_val_3>"]:
                self.parse_token("flag_lit")
                return
            if self.current_tok in PREDICT_SET["<primary_val_4>"]:
                self.parse_token("chars_lit")
                return
            if self.current_tok in PREDICT_SET["<primary_val_5>"]:
                self.parse_token("id")
                self.id_tail()
                return
            if self.current_tok in PREDICT_SET["<primary_val_6>"]:
                self.built_in_rec_call()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<primary_val>"])))
        log.info("Exit: " + self.current_tok)

    def id_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<id_tail>"]:
            if self.current_tok in PREDICT_SET["<id_tail>"]:
                self.call_tailopt()
                self.accessor_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<id_tail>"])))
        log.info("Exit: " + self.current_tok)
        
    def call_tailopt(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<call_tailopt>"]:
            if self.current_tok in PREDICT_SET["<call_tailopt>"]:
                self.parse_token("(")
                self.flavor()
                self.parse_token(")")
            if self.current_tok in PREDICT_SET["<call_tailopt_1>"]:
                log.info("Exit: " + self.current_tok)
                return        
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<call_tailopt>"])))
        log.info("Exit: " + self.current_tok)
        
    def accessor_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<accessor_tail>"]:
            if self.current_tok in PREDICT_SET["<accessor_tail>"]:
                self.array_accessor()
            if self.current_tok in PREDICT_SET["<accessor_tail_1>"]:
                self.table_accessor()
            if self.current_tok in PREDICT_SET["<accessor_tail_2>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<accessor_tail>"])))
        log.info("Exit: " + self.current_tok)
        
    def array_accessor(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<array_accessor>"]:
            if self.current_tok in PREDICT_SET["<array_accessor>"]:
                self.parse_token("[")
                self.expr()
                self.parse_token("]")
                self.accessor_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<array_accessor>"])))
        log.info("Exit: " + self.current_tok)

    def table_accessor(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<table_accessor>"]:
            if self.current_tok in PREDICT_SET["<table_accessor>"]:
                self.parse_token(":")
                self.parse_token("id")
                self.accessor_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<table_accessor>"])))
        log.info("Exit: " + self.current_tok)

    def flavor(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<flavor>"]:
            if self.current_tok in PREDICT_SET["<flavor>"]:
                self.value()
                self.flavor_tail()
            if self.current_tok in PREDICT_SET["<flavor_1>"]:    
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<flavor>"])))
        log.info("Exit: " + self.current_tok)

    def value(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<value>"]:
            if self.current_tok in PREDICT_SET["<value>"]:
                self.expr()
                return
            if self.current_tok in PREDICT_SET["<value_1>"]:
                self.parse_token("[")
                self.notation_val()
                self.parse_token("]")
                self.accessor_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<value>"])))
        log.info("Exit: " + self.current_tok)

    def notation_val(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<notation_val>"]:
            if self.current_tok in PREDICT_SET["<notation_val>"]:
                self.array_element()
                return
            if self.current_tok in PREDICT_SET["<notation_val_1>"]:
                self.parse_token("id")
                self.array_or_table()
            if self.current_tok in PREDICT_SET["<notation_val_2>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<notation_val>"])))
        log.info("Exit: " + self.current_tok)

    def array_element(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<array_element>"]:
            if self.current_tok in PREDICT_SET["<array_element>"]:
                self.parse_token("piece_lit")
                self.element_value_tail()
            if self.current_tok in PREDICT_SET["<array_element_1>"]:
                self.parse_token("sip_lit")
                self.element_value_tail()
            if self.current_tok in PREDICT_SET["<array_element_2>"]:
                self.parse_token("flag_lit")
                self.element_value_tail()
            if self.current_tok in PREDICT_SET["<array_element_3>"]:
                self.parse_token("chars_lit")
                self.element_value_tail()
            if self.current_tok in PREDICT_SET["<array_element_4>"]:
                self.parse_token("[")
                self.notation_val()
                self.parse_token("]")
                self.element_value_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<array_element>"])))
        log.info("Exit: " + self.current_tok)

    def element_value_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<element_value_tail>"]:
            if self.current_tok in PREDICT_SET["<element_value_tail>"]:
                self.parse_token(",")
                self.array_element_id()
            if self.current_tok in PREDICT_SET["<element_value_tail_1>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<element_value_tail>"])))
        log.info("Exit: " + self.current_tok)

    def array_element_id(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<array_element_id>"]:
            if self.current_tok in PREDICT_SET["<array_element_id>"]:
                self.parse_token("id")
                self.element_value_tail()
            if self.current_tok in PREDICT_SET["<array_element_id_1>"]:
                self.array_element()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<array_element_id>"])))
        log.info("Exit: " + self.current_tok)

    def array_or_table(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<array_or_table>"]:
            if self.current_tok in PREDICT_SET["<array_or_table>"]:
                self.parse_token(",")
                self.array_element_id()
            if self.current_tok in PREDICT_SET["<array_or_table_1>"]:
                self.parse_token("=")
                self.value()
                self.parse_token(";")
                self.field_assignments()
            if self.current_tok in PREDICT_SET["<array_or_table_2>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<array_or_table>"])))
        log.info("Exit: " + self.current_tok)

    def field_assignments(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<field_assignments>"]:
            if self.current_tok in PREDICT_SET["<field_assignments>"]:
                self.parse_token("id")
                self.parse_token("=")
                self.value()
                self.parse_token(";")
                self.field_assignments()
            if self.current_tok in PREDICT_SET["<field_assignments_1>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<field_assignments>"])))
        log.info("Exit: " + self.current_tok)

    def flavor_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<flavor_tail>"]:
            if self.current_tok in PREDICT_SET["<flavor_tail>"]:
                self.parse_token(",")
                self.value()
                self.flavor_tail()
            if self.current_tok in PREDICT_SET["<flavor_tail_1>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<flavor_tail>"])))
        log.info("Exit: " + self.current_tok)
        
    def built_in_rec_call(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<built-in_rec_call>"]:
            if self.current_tok in PREDICT_SET["<built-in_rec_call>"]:
                self.built_in_rec()
                self.tail1()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<built-in_rec_call>"])))
        log.info("Exit: " + self.current_tok)

    def built_in_rec(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<built-in_rec>"]:
            if self.current_tok in PREDICT_SET["<built-in_rec>"]:
                self.parse_token("append")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_1>"]:
                self.parse_token("bill")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_2>"]:
                self.parse_token("copy")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_3>"]:
                self.parse_token("cut")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_4>"]:
                self.parse_token("fact")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_5>"]:
                self.parse_token("matches")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_6>"]:
                self.parse_token("pow")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_7>"]:
                self.parse_token("rand")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_8>"]:
                self.parse_token("remove")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_9>"]:
                self.parse_token("reverse")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_10>"]:
                self.parse_token("search")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_11>"]:
                self.parse_token("size")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_12>"]:
                self.parse_token("sort")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_13>"]:
                self.parse_token("sqrt")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_14>"]:
                self.parse_token("take")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_15>"]:
                self.parse_token("tochars")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_16>"]:
                self.parse_token("topiece")
                return
            if self.current_tok in PREDICT_SET["<built-in_rec_17>"]:
                self.parse_token("tosip")
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<built-in_rec>"])))
        log.info("Exit: " + self.current_tok)

    def tail1(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<tail1>"]:
            if self.current_tok in PREDICT_SET["<tail1>"]:
                self.call_tail()
                self.accessor_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<tail1>"])))
        log.info("Exit: " + self.current_tok)

    def call_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<call_tail>"]:
            if self.current_tok in PREDICT_SET["<call_tail>"]:
                self.parse_token("(")
                self.flavor()
                self.parse_token(")")
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<call_tail>"])))
        log.info("Exit: " + self.current_tok)
        
    def dimensions(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<dimensions>"]:
            if self.current_tok in PREDICT_SET["<dimensions>"]:
                self.parse_token("[")
                self.parse_token("]")
                self.dimensions_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<dimensions>"])))
        log.info("Exit: " + self.current_tok)

    def dimensions_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<dimensions_tail>"]:
            if self.current_tok in PREDICT_SET["<dimensions_tail>"]:
                self.dimensions()
            if self.current_tok in PREDICT_SET["<dimensions_tail_1>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<dimensions_tail>"])))
        log.info("Exit: " + self.current_tok)

    def array_declare(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<array_declare>"]:
            if self.current_tok in PREDICT_SET["<array_declare>"]:
                self.parse_token("id")
                self.array_table_init()
                self.array_declare_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<array_declare>"])))
        log.info("Exit: " + self.current_tok)

    def array_table_init(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<array_table_init>"]:
            if self.current_tok in PREDICT_SET["<array_table_init>"]:
                self.parse_token("=")
                self.value()
            if self.current_tok in PREDICT_SET["<array_table_init_1>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<array_table_init>"])))
        log.info("Exit: " + self.current_tok)

    def array_declare_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<array_declare_tail>"]:
            if self.current_tok in PREDICT_SET["<array_declare_tail>"]:
                self.parse_token(",")
                self.array_declare()
            if self.current_tok in PREDICT_SET["<array_declare_tail_1>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<array_declare_tail>"])))
        log.info("Exit: " + self.current_tok)

    def table_prototype(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<table_prototype>"]:
            if self.current_tok in PREDICT_SET["<table_prototype>"]:
                self.parse_token("table")
                self.parse_token("of")
                self.parse_token("id")
                self.parse_token("=")
                self.parse_token("[")
                self.required_decl()
                self.parse_token("]")
                self.parse_token(";")
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<table_prototype>"])))
        log.info("Exit: " + self.current_tok)

    def required_decl(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<required_decl>"]:
            if self.current_tok in PREDICT_SET["<required_decl>"]:
                self.decl_head()
                self.parse_token(";")
                self.required_decl_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<required_decl>"])))
        log.info("Exit: " + self.current_tok)

    def decl_head(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<decl_head>"]:
            if self.current_tok in PREDICT_SET["<decl_head>"]:
                self.primitive_types_dims()
                self.parse_token("of")
                self.parse_token("id")
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<decl_head>"])))
        log.info("Exit: " + self.current_tok)

    def primitive_types_dims(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<primitive_types_dims>"]:
            if self.current_tok in PREDICT_SET["<primitive_types_dims>"]:
                self.parse_token("piece")
                self.dimensions_tail()
            if self.current_tok in PREDICT_SET["<primitive_types_dims_1>"]:
                self.parse_token("sip")
                self.dimensions_tail()
            if self.current_tok in PREDICT_SET["<primitive_types_dims_2>"]:
                self.parse_token("flag")
                self.dimensions_tail()
            if self.current_tok in PREDICT_SET["<primitive_types_dims_3>"]:
                self.parse_token("chars")
                self.dimensions_tail()
            if self.current_tok in PREDICT_SET["<primitive_types_dims_4>"]:
                self.parse_token("id")
                self.dimensions_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<primitive_types_dims>"])))
        log.info("Exit: " + self.current_tok)
        
    def required_decl_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<required_decl_tail>"]:
            if self.current_tok in PREDICT_SET["<required_decl_tail>"]:
                self.required_decl()
            if self.current_tok in PREDICT_SET["<required_decl_tail_1>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<required_decl_tail>"])))
        log.info("Exit: " + self.current_tok)
        
    def table_decl(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<table_decl>"]:
            if self.current_tok in PREDICT_SET["<table_decl>"]:
                self.dimensions_tail()
                self.parse_token("of")
                self.table_declare()
                self.parse_token(";")
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<table_decl>"])))
        log.info("Exit: " + self.current_tok)

    def table_declare(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<table_declare>"]:
            if self.current_tok in PREDICT_SET["<table_declare>"]:
                self.parse_token("id")
                self.array_table_init()
                self.table_declare_tail()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<table_declare>"])))
        log.info("Exit: " + self.current_tok)

    def table_declare_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<table_declare_tail>"]:
            if self.current_tok in PREDICT_SET["<table_declare_tail>"]:
                self.parse_token(",")
                self.table_declare()
            if self.current_tok in PREDICT_SET["<table_declare_tail_1>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<table_declare_tail>"])))
        log.info("Exit: " + self.current_tok)

    def recipe_decl(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<recipe_decl>"]:
            if self.current_tok in PREDICT_SET["<recipe_decl>"]:
                self.parse_token("prepare")
                self.serve_type()
                self.parse_token("(")
                self.spice()
                self.parse_token(")")
                self.platter()
                self.recipe_decl()
            if self.current_tok in PREDICT_SET["<recipe_decl_1>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<recipe_decl>"])))
        log.info("Exit: " + self.current_tok)

    def serve_type(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<serve_type>"]:
            if self.current_tok in PREDICT_SET["<serve_type>"]:
                self.decl_head()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<serve_type>"])))
        log.info("Exit: " + self.current_tok)

    def spice(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<spice>"]:
            if self.current_tok in PREDICT_SET["<spice>"]:
                self.decl_head()
                self.spice_tail()
            if self.current_tok in PREDICT_SET["<spice_1>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<spice>"])))
        log.info("Exit: " + self.current_tok)
    
    def spice_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<spice_tail>"]:
            if self.current_tok in PREDICT_SET["<spice_tail>"]:
                self.parse_token(",")
                self.decl_head()
                self.spice_tail()
            if self.current_tok in PREDICT_SET["<spice_tail_1>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<spice_tail>"])))
        log.info("Exit: " + self.current_tok)

    def platter(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<platter>"]:
            self.parse_token("{")
            self.local_decl()
            self.statements()
            self.parse_token("}")
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<platter>"])))
        log.info("Exit: " + self.current_tok)

    def local_decl(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<local_decl>"]:
            if self.current_tok in PREDICT_SET["<local_decl>"]:
                self.decl_data_type()
                self.local_decl()
            if self.current_tok in PREDICT_SET["<local_decl_1>"]:
                self.parse_token("id")
                self.local_id_tail()
            if self.current_tok in PREDICT_SET["<local_decl_2>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<local_decl>"])))
        log.info("Exit: " + self.current_tok)

    def statements(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<statements>"]:
            if self.current_tok in PREDICT_SET["<statements>"]:
                self.id_statements()
                self.statements()
            if self.current_tok in PREDICT_SET["<statements_1>"]:
                self.built_in_rec_call()
                self.parse_token(";")
                self.statements()
            if self.current_tok in PREDICT_SET["<statements_2>"]:
                self.conditional_st()
                self.statements()
            if self.current_tok in PREDICT_SET["<statements_3>"]:
                self.looping_st()
                self.statements()
            if self.current_tok in PREDICT_SET["<statements_4>"]:
                self.jump_st()
                self.statements()
            if self.current_tok in PREDICT_SET["<statements_5>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<statements>"])))
        log.info("Exit: " + self.current_tok)

    def local_id_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<local_id_tail>"]:
            if self.current_tok in PREDICT_SET["<local_id_tail>"]:
                self.parse_token("of")
                self.table_declare()
                self.parse_token(";")
                self.local_decl()
            if self.current_tok in PREDICT_SET["<local_id_tail_1>"]:
                self.parse_token("[")
                self.endb_tail()
            if self.current_tok in PREDICT_SET["<local_id_tail_2>"]:
                self.table_accessor()
                self.assignment_op()
                self.value()
                self.parse_token(";")
                self.statements()
            if self.current_tok in PREDICT_SET["<local_id_tail_3>"]:
                self.assignment_op()
                self.value()
                self.parse_token(";")
                self.statements()
            if self.current_tok in PREDICT_SET["<local_id_tail_4>"]:
                self.tail1()
                self.parse_token(";")
                self.statements()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<local_id_tail>"])))
        log.info("Exit: " + self.current_tok)

    def endb_tail(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<]_tail>"]:
            if self.current_tok in PREDICT_SET["<]_tail>"]:
                self.parse_token("]")
                self.dimensions_tail()
                self.parse_token("of")
                self.table_declare()
                self.parse_token(";")
                self.local_decl()
            if self.current_tok in PREDICT_SET["<]_tail_1>"]:
                self.expr()
                self.parse_token("]")
                self.accessor_tail()
                self.assignment_op()
                self.value()
                self.parse_token(";")
                self.statements()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<]_tail>"])))
        log.info("Exit: " + self.current_tok)

    def id_statements(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<id_statements>"]:
            if self.current_tok in PREDICT_SET["<id_statements>"]:
                self.parse_token("id")
                self.id_statements_ext()
                self.statements()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<id_statements>"])))
        log.info("Exit: " + self.current_tok)

    def id_statements_ext(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<id_statements_ext>"]:
            if self.current_tok in PREDICT_SET["<id_statements_ext>"]:
                self.tail1()
                self.parse_token(";")
            if self.current_tok in PREDICT_SET["<id_statements_ext_1>"]:
                self.assignment_st()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<id_statements_ext>"])))
        log.info("Exit: " + self.current_tok)

    def assignment_st(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<assignment_st>"]:
            if self.current_tok in PREDICT_SET["<assignment_st>"]:
                self.accessor_tail()
                self.assignment_op()
                self.value()
                self.parse_token(";")
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<assignment_st>"])))
        log.info("Exit: " + self.current_tok)

    def assignment_op(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<assignment_op>"]:
            if self.current_tok in PREDICT_SET["<assignment_op>"]:
                self.parse_token("=")
            if self.current_tok in PREDICT_SET["<assignment_op_1>"]:
                self.parse_token("+=")
            if self.current_tok in PREDICT_SET["<assignment_op_2>"]:
                self.parse_token("-=")
            if self.current_tok in PREDICT_SET["<assignment_op_3>"]:
                self.parse_token("*=")
            if self.current_tok in PREDICT_SET["<assignment_op_4>"]:
                self.parse_token("/=")
            if self.current_tok in PREDICT_SET["<assignment_op_5>"]:
                self.parse_token("%=")
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<assignment_op>"])))
        log.info("Exit: " + self.current_tok)
    
    def conditional_st(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<conditional_st>"]:
            if self.current_tok in PREDICT_SET["<conditional_st>"]:
                self.cond_check()
            if self.current_tok in PREDICT_SET["<conditional_st_1>"]:
                self.cond_menu()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<conditional_st>"])))
        log.info("Exit: " + self.current_tok)

    def cond_check(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<cond_check>"]:
            if self.current_tok in PREDICT_SET["<cond_check>"]:
                self.parse_token("check")
                self.parse_token("(")
                self.expr()
                self.parse_token(")")
                self.platter()
                self.alt_clause()
                self.instead_clause()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<cond_check>"])))
        log.info("Exit: " + self.current_tok)

    def alt_clause(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<alt_clause>"]:
            if self.current_tok in PREDICT_SET["<alt_clause>"]:
                self.parse_token("alt")
                self.parse_token("(")
                self.expr()
                self.parse_token(")")
                self.platter()
                self.alt_clause()
            if self.current_tok in PREDICT_SET["<alt_clause_1>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<alt_clause>"])))
        log.info("Exit: " + self.current_tok)        

    def instead_clause(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<instead_clause>"]:
            if self.current_tok in PREDICT_SET["<instead_clause>"]:
                self.parse_token("instead")
                self.platter()
            if self.current_tok in PREDICT_SET["<instead_clause_1>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<instead_clause>"])))
        log.info("Exit: " + self.current_tok)

    def cond_menu(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<cond_menu>"]:
            if self.current_tok in PREDICT_SET["<cond_menu>"]:
                self.parse_token("menu")
                self.parse_token("(")
                self.expr()
                self.parse_token(")")
                self.menu_platter()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<cond_menu>"])))
        log.info("Exit: " + self.current_tok)

    def menu_platter(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<menu_platter>"]:
            if self.current_tok in PREDICT_SET["<menu_platter>"]:
                self.parse_token("{")
                self.choice_clause()
                self.usual_clause()
                self.parse_token("}")
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<menu_platter>"])))
        log.info("Exit: " + self.current_tok)

    def choice_clause(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<choice_clause>"]:
            if self.current_tok in PREDICT_SET_ERR["<choice_clause>"]:
                self.parse_token("choice")
                self.choice_val()
                self.parse_token(":")
                self.statements()
                self.choice_clause()
            if self.current_tok in PREDICT_SET["<choice_clause_1>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<choice_clause>"])))
        log.info("Exit: " + self.current_tok)

    def choice_val(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<choice_val>"]:
            if self.current_tok in PREDICT_SET["<choice_val>"]:
                self.parse_token("piece_lit")
            if self.current_tok in PREDICT_SET["<choice_val_1>"]:
                self.parse_token("chars_lit")
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<choice_val>"])))
        log.info("Exit: " + self.current_tok)


    def usual_clause(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<usual_clause>"]:
            if self.current_tok in PREDICT_SET["<usual_clause>"]:
                self.parse_token("usual")
                self.parse_token(":")
                self.statements()
            if self.current_tok in PREDICT_SET["<usual_clause_1>"]:
                log.info("Exit: " + self.current_tok)
                return
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<usual_clause>"])))
        log.info("Exit: " + self.current_tok)

    def looping_st(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<looping_st>"]:
            if self.current_tok in PREDICT_SET["<looping_st>"]:
                self.loop_pass()
            if self.current_tok in PREDICT_SET["<looping_st_1>"]:
                self.loop_repeat()
            if self.current_tok in PREDICT_SET["<looping_st_2>"]:
                self.loop_order()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<looping_st>"])))
        log.info("Exit: " + self.current_tok)

    def loop_pass(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<loop_pass>"]:
            if self.current_tok in PREDICT_SET["<loop_pass>"]:
                self.parse_token("pass")
                self.parse_token("(")
                self.initialization()
                self.update()
                self.expr()
                self.parse_token(")")
                self.platter()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<loop_pass>"])))
        log.info("Exit: " + self.current_tok)

    def initialization(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<initialization>"]:
            if self.current_tok in PREDICT_SET["<initialization>"]:
                self.parse_token("id")
                self.ingredient_init()
                self.parse_token(";")
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<initialization>"])))
        log.info("Exit: " + self.current_tok)

    def update(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<update>"]:
            if self.current_tok in PREDICT_SET["<update>"]:
                self.parse_token("id")
                self.assignment_st()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<update>"])))
        log.info("Exit: " + self.current_tok)

    def loop_repeat(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<loop_repeat>"]:
            if self.current_tok in PREDICT_SET["<loop_repeat>"]:
                self.parse_token("repeat")
                self.parse_token("(")
                self.expr()
                self.parse_token(")")
                self.platter()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<loop_repeat>"])))
        log.info("Exit: " + self.current_tok)

    def loop_order(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<loop_order>"]:
            if self.current_tok in PREDICT_SET["<loop_order>"]:
                self.parse_token("order")
                self.platter()
                self.parse_token("repeat")
                self.parse_token("(")
                self.expr()
                self.parse_token(")")
                self.parse_token(";")
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<loop_order>"])))
        log.info("Exit: " + self.current_tok)

    def jump_st(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<jump_st>"]:
            if self.current_tok in PREDICT_SET["<jump_st>"]:
                self.jump_next()
            if self.current_tok in PREDICT_SET["<jump_st_1>"]:
                self.jump_stop()
            if self.current_tok in PREDICT_SET["<jump_st_2>"]:
                self.jump_serve()
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<jump_st>"])))
        log.info("Exit: " + self.current_tok)

    def jump_next(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<jump_next>"]:
            if self.current_tok in PREDICT_SET["<jump_next>"]:
                self.parse_token("next")
                self.parse_token(";")
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<jump_next>"])))
        log.info("Exit: " + self.current_tok)

    def jump_stop(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<jump_stop>"]:
            if self.current_tok in PREDICT_SET["<jump_stop>"]:
                self.parse_token("stop")
                self.parse_token(";")
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<jump_stop>"])))
        log.info("Exit: " + self.current_tok)

    def jump_serve(self):
        log.info("Enter: " + self.current_tok)
        if self.current_tok in PREDICT_SET_ERR["<jump_serve>"]:
            if self.current_tok in PREDICT_SET["<jump_serve>"]:
                self.parse_token("serve")
                self.value()
                self.parse_token(";")
        else: self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<jump_serve>"])))
        log.info("Exit: " + self.current_tok)


if __name__ == "__main__":
    # for debugging
    # code = """start();"""
    filename = "parser.platter"
    code = run_file(filename)
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    try:
        if parser.parse(): print("Syntax OK")
    except SyntaxError as e:
        print(str(e))
