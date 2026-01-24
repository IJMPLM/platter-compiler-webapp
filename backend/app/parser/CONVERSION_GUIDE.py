"""
Pattern Guide for Converting Parser Methods to Return ParseNodes

PATTERN 1: Simple method with single production
============================================
BEFORE:
    def method_name(self):
        if self.current_tok in PREDICT_SET["<rule>"]:
            self.parse_token("token1")
            self.other_method()

AFTER:
    def method_name(self):
        node = ParseNode("<rule>")
        if self.current_tok in PREDICT_SET["<rule>"]:
            node.add_child(self.parse_token("token1"))
            node.add_child(self.other_method())
        return node


PATTERN 2: Method with multiple alternatives
============================================
BEFORE:
    def method_name(self):
        if self.current_tok in PREDICT_SET["<rule_1>"]:
            self.parse_token("token1")
        if self.current_tok in PREDICT_SET["<rule_2>"]:
            self.parse_token("token2")

AFTER:
    def method_name(self):
        node = ParseNode("<method_name>")
        if self.current_tok in PREDICT_SET["<rule_1>"]:
            node.add_child(self.parse_token("token1"))
        if self.current_tok in PREDICT_SET["<rule_2>"]:
            node.add_child(self.parse_token("token2"))
        return node


PATTERN 3: Method with epsilon/lambda production
============================================
BEFORE:
    def method_name(self):
        if self.current_tok in PREDICT_SET["<rule>"]:
            self.other_method()
        if self.current_tok in PREDICT_SET["<rule_lambda>"]:
            return  # λ

AFTER:
    def method_name(self):
        node = ParseNode("<method_name>")
        if self.current_tok in PREDICT_SET["<rule>"]:
            node.add_child(self.other_method())
        if self.current_tok in PREDICT_SET["<rule_lambda>"]:
            return node  # Return node even if empty (represents λ)
        return node


PATTERN 4: Method with early return
============================================
BEFORE:
    def method_name(self):
        if self.current_tok in PREDICT_SET["<rule_1>"]:
            self.parse_token("literal")
            return
        if self.current_tok in PREDICT_SET["<rule_2>"]:
            self.other_method()

AFTER:
    def method_name(self):
        node = ParseNode("<method_name>")
        if self.current_tok in PREDICT_SET["<rule_1>"]:
            node.add_child(self.parse_token("literal"))
            return node
        if self.current_tok in PREDICT_SET["<rule_2>"]:
            node.add_child(self.other_method())
        return node


PATTERN 5: Tail recursion (like or_tail, and_tail)
============================================
BEFORE:
    def or_tail(self):
        if self.current_tok in PREDICT_SET["<or_tail>"]:
            self.parse_token("or")
            self.and_expr()
            self.or_tail()
        if self.current_tok in PREDICT_SET["<or_tail_1>"]:
            return

AFTER:
    def or_tail(self):
        node = ParseNode("<or_tail>")
        if self.current_tok in PREDICT_SET["<or_tail>"]:
            node.add_child(self.parse_token("or"))
            node.add_child(self.and_expr())
            node.add_child(self.or_tail())  # Recursively add tail
        if self.current_tok in PREDICT_SET["<or_tail_1>"]:
            return node  # Empty tail
        return node


CHECKLIST FOR EACH METHOD:
==========================
1. Create node at start: node = ParseNode("<rule_name>")
2. Replace self.method_call() with node.add_child(self.method_call())
3. Replace self.parse_token() with node.add_child(self.parse_token())
4. Replace all 'return' statements with 'return node'
5. Add 'return node' at the end if not already present

SPECIAL CASES:
==============
- Methods that don't have children (just call one other method):
  Still create a node to maintain CFG structure
  
- Error handling: Keep as-is, errors prevent node return
  
- Logging: Keep as-is, doesn't affect tree building
"""

# Example: Complete transformation of a real method

def decl_data_type_BEFORE(self):
    log.info("Enter: " + self.current_tok)
    if self.current_tok in PREDICT_SET_ERR["<decl_data_type>"]:
        if self.current_tok in PREDICT_SET["<decl_data_type>"]:
            self.parse_token("piece")
            self.decl_type()
        if self.current_tok in PREDICT_SET["<decl_data_type_1>"]:
            self.parse_token("sip")
            self.decl_type()
    else: 
        self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<decl_data_type>"])))
    log.info("Exit: " + self.current_tok)


def decl_data_type_AFTER(self):
    log.info("Enter: " + self.current_tok)
    node = ParseNode("<decl_data_type>")
    
    if self.current_tok in PREDICT_SET_ERR["<decl_data_type>"]:
        if self.current_tok in PREDICT_SET["<decl_data_type>"]:
            node.add_child(self.parse_token("piece"))
            node.add_child(self.decl_type())
        if self.current_tok in PREDICT_SET["<decl_data_type_1>"]:
            node.add_child(self.parse_token("sip"))
            node.add_child(self.decl_type())
    else: 
        self.error_handler("Unexpected_err", (", ".join(f"'{tok}'" for tok in PREDICT_SET_ERR["<decl_data_type>"])))
    
    log.info("Exit: " + self.current_tok)
    return node
