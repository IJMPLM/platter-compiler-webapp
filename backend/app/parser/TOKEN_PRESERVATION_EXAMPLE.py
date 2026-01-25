"""
Visual Example: How Token-Based Parse Tree Preserves Information

This demonstrates why keeping tokens in the tree is essential
for semantic analysis like symbol table creation.
"""

# Example Platter code:
example_code = """
piece of counter = 0;
"""

# What the lexer produces:
tokens = [
    Token(type='piece',     value='piece',   line=2, col=1),
    Token(type='of',        value='of',      line=2, col=7),
    Token(type='id',        value='counter', line=2, col=10),  # ← NAME!
    Token(type='=',         value='=',       line=2, col=18),
    Token(type='piece_lit', value='0',       line=2, col=20),  # ← VALUE!
    Token(type=';',         value=';',       line=2, col=21),
]

# What the parse tree looks like WITH token preservation:
parse_tree_WITH_tokens = """
<program>
└── <global_decl>
    └── <decl_data_type>
        ├── piece (token: value='piece', line=2, col=1)          ← TYPE
        └── <decl_type>
            ├── of (token: value='of', line=2, col=7)
            ├── <ingredient_id>
            │   ├── id (token: value='counter', line=2, col=10)  ← NAME!
            │   └── <ingredient_init>
            │       ├── = (token: value='=', line=2, col=18)
            │       └── <expr>
            │           └── <or_expr>
            │               └── ...
            │                   └── piece_lit (token: value='0', line=2, col=20)  ← VALUE!
            └── ; (token: value=';', line=2, col=21)
"""

# How semantic analyzer extracts information:
def build_symbol_table(tree):
    """
    With token-based tree, we can extract:
    1. Variable name from token.value
    2. Type from parent context
    3. Initial value from expression
    4. Line/col for error reporting
    """
    
    # Navigate to <decl_data_type>
    decl_node = find_node(tree, "<decl_data_type>")
    
    # Get type from first child token
    type_token = decl_node.children[0]  # 'piece' token
    var_type = type_token.value  # ✓ "piece"
    
    # Navigate to identifier
    id_node = find_node(decl_node, lambda n: n.is_terminal() and n.type == 'id')
    var_name = id_node.value  # ✓ "counter" - the actual variable name!
    var_line = id_node.line   # ✓ 2
    var_col = id_node.col     # ✓ 10
    
    # Find initialization value
    lit_node = find_node(decl_node, lambda n: n.is_terminal() and n.type == 'piece_lit')
    init_value = lit_node.value  # ✓ "0"
    
    # Add to symbol table
    symbol_table.add({
        'name': var_name,      # "counter" ← from token!
        'type': var_type,      # "piece"
        'value': init_value,   # "0" ← from token!
        'line': var_line,      # 2 ← from token!
        'col': var_col         # 10 ← from token!
    })
    
    return symbol_table


# What would happen WITHOUT token preservation:
parse_tree_WITHOUT_tokens = """
<program>
└── <global_decl>
    └── <decl_data_type>
        ├── piece                    ← Just the rule name, no value!
        └── <decl_type>
            ├── of
            ├── <ingredient_id>
            │   ├── id               ← No name! Can't build symbol table!
            │   └── <ingredient_init>
            │       ├── =
            │       └── <expr>
            │           └── piece_lit  ← No value! Can't evaluate!
            └── ;
"""

# Result:
"""
❌ WITHOUT tokens:
   - Can't get variable name "counter"
   - Can't get initial value "0"
   - Can't get line/col for errors
   - Would need to re-scan token stream (inefficient!)

✅ WITH tokens:
   - All information in one place
   - Clean tree traversal
   - One pass for analysis
   - Line/col preserved for error messages
"""


# Real-world example: Type checking an expression
type_checking_example = """
Code: x + y

Parse Tree (with tokens):
<expr>
└── <add_expr>
    ├── <mult_expr>
    │   └── <primary_val>
    │       └── id (token: value='x', line=1, col=1)  ← Look up 'x' in symbol table!
    ├── + (token: value='+', line=1, col=3)
    └── <mult_expr>
        └── <primary_val>
            └── id (token: value='y', line=1, col=5)  ← Look up 'y' in symbol table!

Type Checking Algorithm:
1. Visit left operand (id 'x')
   - Extract name from token.value → "x"
   - Look up in symbol table → type: "piece"
   
2. Visit right operand (id 'y')
   - Extract name from token.value → "y"
   - Look up in symbol table → type: "piece"
   
3. Check operator '+'
   - Both operands are "piece" ✓
   - Result type: "piece" ✓
   
4. If types mismatch:
   - Report error with line/col from tokens ✓

All possible because tokens are preserved in the tree!
"""


# Summary comparison:
comparison = """
┌─────────────────────────┬──────────────────────┬─────────────────────┐
│ Requirement             │ With Tokens          │ Without Tokens      │
├─────────────────────────┼──────────────────────┼─────────────────────┤
│ Get variable name       │ ✓ node.token.value   │ ✗ Must re-scan      │
│ Get literal value       │ ✓ node.token.value   │ ✗ Must re-scan      │
│ Get line/col for errors │ ✓ node.token.line    │ ✗ Lost after parse  │
│ Symbol table building   │ ✓ One tree pass      │ ✗ Complex workaround│
│ Type checking           │ ✓ Direct access      │ ✗ Need side data    │
│ Code generation         │ ✓ Names/values ready │ ✗ Must track extra  │
│ Error messages          │ ✓ Precise location   │ ✗ Generic only      │
│ Multi-pass analysis     │ ✓ Clean & simple     │ ✗ Complicated       │
└─────────────────────────┴──────────────────────┴─────────────────────┘

Conclusion: Token preservation is ESSENTIAL for semantic analysis!
"""


if __name__ == "__main__":
    print("=" * 70)
    print("WHY TOKEN-BASED PARSE TREE?")
    print("=" * 70)
    print()
    print("Example Code:")
    print(example_code)
    print()
    print("Parse Tree WITH Token Preservation:")
    print(parse_tree_WITH_tokens)
    print()
    print("What Semantic Analyzer Can Extract:")
    print("-" * 70)
    print("  • Variable name: 'counter' (from token.value)")
    print("  • Variable type: 'piece' (from context + token)")
    print("  • Initial value: '0' (from token.value)")
    print("  • Location: line 2, col 10 (from token.line/col)")
    print()
    print("=" * 70)
    print()
    print(comparison)
    print()
    print("This is exactly what you need for:")
    print("  1. Symbol table creation ✓")
    print("  2. Type checking ✓")
    print("  3. Code generation ✓")
    print("  4. Semantic validation ✓")
    print()
    print("=" * 70)
