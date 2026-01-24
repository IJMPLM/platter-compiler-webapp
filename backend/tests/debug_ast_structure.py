"""
Debug script to see the AST structure for variable declarations
"""

import sys
sys.path.insert(0, 'D:/Repositories/platter-compiler-webapp/backend')

from app.lexer.lexer import Lexer
from app.parser.parser import Parser
from app.parser.ast_nodes import ParseNode

def print_tree_detailed(node, indent=0, max_depth=15):
    """Print tree with detailed info about each node"""
    if indent > max_depth:
        print("  " * indent + "...")
        return
    
    prefix = "  " * indent
    
    if node.is_terminal():
        print(f"{prefix}TOKEN: {node.type} = '{node.value}' (line {node.line}, col {node.col})")
    else:
        print(f"{prefix}NODE: {node.rule}")
        for child in node.children:
            print_tree_detailed(child, indent + 1, max_depth)


def main():
    code = """
    piece of x, y, z;
    sip of temperature = 98.6;
    
    start() {
    }
    """
    
    print("Code:", code)
    print("\n" + "=" * 80)
    print("AST STRUCTURE (full tree)")
    print("=" * 80)
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    if ast:
        print_tree_detailed(ast, max_depth=15)
    else:
        print("Parse failed")


if __name__ == "__main__":
    main()
