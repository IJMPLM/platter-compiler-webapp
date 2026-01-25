import sys
sys.path.insert(0, 'D:/Repositories/platter-compiler-webapp/backend')

from app.lexer.lexer import Lexer
from app.parser.parser import Parser

# Quick test to see the parse tree structure for arrays
code = """
piece[] of data;

start() {
    bill("test");
}
"""

print("Parsing array declaration to see AST structure...")
lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

def print_tree(node, indent=0):
    """Recursively print the parse tree"""
    if node.is_terminal():
        print("  " * indent + f"TERMINAL: {node.type} = '{node.value}'")
    else:
        print("  " * indent + f"NON-TERMINAL: {node.rule}")
        for child in node.children:
            print_tree(child, indent + 1)

print_tree(ast)
