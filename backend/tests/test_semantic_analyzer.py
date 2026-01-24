"""
Test script for the multi-pass semantic analyzer.

Tests Pass 1 (Symbol Table Builder) with:
- Arrays with dimensions
- Recipe parameters
- Multiple variable declarations
"""

import sys
sys.path.insert(0, 'D:/Repositories/platter-compiler-webapp/backend')

from app.lexer.lexer import Lexer
from app.parser.parser import Parser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer


def run_test(name, code):
    """Run a single semantic analyzer test"""
    print("\n" + "=" * 80)
    print(f"TEST: {name}")
    print("=" * 80)
    print("\nSource Code:")
    print("-" * 80)
    print(code)
    print("-" * 80)
    
    # Step 1: Lexical Analysis
    print("\n[1/3] Lexical Analysis...")
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    print(f"  Generated {len(tokens)} tokens")
    
    # Step 2: Parsing (Build AST)
    print("\n[2/3] Parsing (Building AST)...")
    parser = Parser(tokens)
    ast = parser.parse()
    
    if not ast:
        print("  ERROR: Parsing failed")
        return False
    
    print(f"  AST built successfully")
    
    # Step 3: Semantic Analysis
    print("\n[3/3] Semantic Analysis...")
    analyzer = SemanticAnalyzer(ast)
    success = analyzer.analyze()
    
    return success


def test_basic():
    """Test basic variable declarations"""
    code = """
    piece of x, y, z;
    sip of temperature = 98.6;
    flag of isReady;
    
    start() {
        piece of count;
        bill(x);
    }
    """
    return run_test("Basic Variables", code)


def test_arrays():
    """Test array declarations"""
    code = """
    piece[] of numbers;
    piece[] of matrix;
    sip[] of temperatures;
    
    start() {
        bill("test");
    }
    """
    return run_test("Array Declarations", code)


def test_recipe_parameters():
    """Test recipe declarations with parameters"""
    code = """
    prepare piece of add(piece of x, piece of y) {
        serve x;
    }
    
    prepare sip of calculate(piece of a, sip of b, flag of c) {
        sip of result;
        serve result;
    }
    
    start() {
        bill("test");
    }
    """
    return run_test("Recipe Parameters", code)


def test_complex_program():
    """Test a complex program combining arrays, parameters, and variables"""
    code = """
    piece of globalCount;
    piece[] of data;
    piece[] of grid;
    
    prepare piece of process(piece of input, piece[] of arr) {
        piece of local1, local2;
        sip of temp = 3.14;
        serve local1;
    }
    
    start() {
        piece of x;
        piece of result;
    }
    """
    return run_test("Complex Program", code)


if __name__ == "__main__":
    print("\n" + "#" * 80)
    print("# SEMANTIC ANALYZER TEST SUITE")
    print("#" * 80)
    
    results = []
    
    # Run all tests
    results.append(("Basic Variables", test_basic()))
    results.append(("Array Declarations", test_arrays()))
    results.append(("Recipe Parameters", test_recipe_parameters()))
    results.append(("Complex Program", test_complex_program()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status:<12} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 80)

