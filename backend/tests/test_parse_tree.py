"""
Test the parse tree generation with a simple Platter program
"""

from app.lexer.lexer import Lexer
from app.parser.parser import Parser
from app.parser.ast_nodes import ParseNode
import json

# Simple test program
test_code = """
piece of x = 5;
start() {
    bill(x);
}
"""

print("=" * 70)
print("TESTING PARSE TREE GENERATION")
print("=" * 70)
print("\nSource Code:")
print("-" * 70)
print(test_code)
print("-" * 70)

# Tokenize
print("\n1. Lexical Analysis...")
lexer = Lexer(test_code)
tokens = lexer.tokenize()
print(f"   Generated {len(tokens)} tokens")

# Parse
print("\n2. Syntax Analysis...")
parser = Parser(tokens)

try:
    ast = parser.parse()
    
    if ast:
        print("   ✓ Parse successful!")
        print("\n3. Parse Tree Structure:")
        print("-" * 70)
        ast.print_tree()
        print("-" * 70)
        
        print("\n4. Tree Statistics:")
        def count_nodes(node):
            if node.is_terminal():
                return 1
            return 1 + sum(count_nodes(child) for child in node.children)
        
        def count_terminals(node):
            if node.is_terminal():
                return 1
            return sum(count_terminals(child) for child in node.children)
        
        total_nodes = count_nodes(ast)
        terminal_nodes = count_terminals(ast)
        nonterminal_nodes = total_nodes - terminal_nodes
        
        print(f"   Total nodes: {total_nodes}")
        print(f"   Terminal nodes: {terminal_nodes}")
        print(f"   Non-terminal nodes: {nonterminal_nodes}")
        
        print("\n5. JSON Representation (first level):")
        print("-" * 70)
        tree_dict = ast.to_dict()
        print(f"   Root: {tree_dict['rule']}")
        print(f"   Direct children: {len(tree_dict.get('children', []))}")
        
        # Show first few children
        if 'children' in tree_dict:
            print("\n   Children:")
            for i, child in enumerate(tree_dict['children'][:5]):
                print(f"     {i+1}. {child['rule']}")
        
        print("\n6. Accessing Tokens from Tree:")
        print("-" * 70)
        
        def find_all_tokens(node, token_type=None):
            """Find all tokens of a specific type in the tree"""
            tokens = []
            if node.is_terminal():
                if token_type is None or node.type == token_type:
                    tokens.append({
                        'type': node.type,
                        'value': node.value,
                        'line': node.line,
                        'col': node.col
                    })
            else:
                for child in node.children:
                    tokens.extend(find_all_tokens(child, token_type))
            return tokens
        
        # Find all identifiers
        identifiers = find_all_tokens(ast, 'id')
        print(f"   Identifiers found: {len(identifiers)}")
        for id_token in identifiers:
            print(f"     - '{id_token['value']}' at line {id_token['line']}, col {id_token['col']}")
        
        # Find all literals
        literals = [tok for tok in find_all_tokens(ast) 
                   if tok['type'] in ['piece_lit', 'sip_lit', 'flag_lit', 'chars_lit']]
        print(f"\n   Literals found: {len(literals)}")
        for lit_token in literals:
            print(f"     - {lit_token['type']}: {lit_token['value']} at line {lit_token['line']}")
        
        print("\n" + "=" * 70)
        print("NEXT STEPS FOR SEMANTIC ANALYSIS:")
        print("=" * 70)
        print("""
1. Symbol Table Construction:
   - Traverse the tree looking for declarations
   - Extract identifier names and types from token values
   - Build symbol table with scoping information

2. Type Checking:
   - Walk the tree and check expression types
   - Use token info to get variable names and resolve their types
   - Verify type compatibility in operations

3. Code Generation:
   - Traverse the tree in post-order
   - Generate code for each node type
   - Use token values for identifiers, literals, operators
        """)
        
    else:
        print("   ✗ Parse failed!")
        
except SyntaxError as e:
    print(f"\n   ✗ Syntax Error: {e}")
except Exception as e:
    print(f"\n   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
