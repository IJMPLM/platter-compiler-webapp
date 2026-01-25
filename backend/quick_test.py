import sys
sys.path.insert(0, 'D:/Repositories/platter-compiler-webapp/backend')

from app.lexer.lexer import Lexer
from app.parser.parser import Parser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

# Quick test to verify array detection works
code = """
piece[] of data;
piece of count;

start() {
    bill("test");
}
"""

print("Testing array detection...")
lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

analyzer = SemanticAnalyzer(ast)
result = analyzer.analyze()

print("\n" + "="*80)
if result:
    print("✓ TEST PASSED - Arrays detected successfully!")
else:
    print("✗ TEST FAILED")
print("="*80)
