"""
Simple test to trace symbol table building
"""

import sys
sys.path.insert(0, 'D:/Repositories/platter-compiler-webapp/backend')

from app.lexer.lexer import Lexer
from app.parser.parser import Parser
from app.semantic_analyzer.symbol_table_builder import SymbolTableBuilder
import logging

# Enable DEBUG logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

def main():
    code = """
    piece of x, y, z;
    sip of temperature = 98.6;
    
    start() {
    }
    """
    
    print("Code:", code.strip())
    print("\n" + "=" * 80)
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    # Temporarily disable parser logging
    import app.parser.parser as parser_module
    parser_logger = logging.getLogger('app.parser.parser')
    parser_logger.setLevel(logging.ERROR)
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    if ast:
        print("\n" + "=" * 80)
        print("Building Symbol Tables...")
        print("=" * 80)
        builder = SymbolTableBuilder(ast)
        builder.build()


if __name__ == "__main__":
    main()
