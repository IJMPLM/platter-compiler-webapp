"""
Comprehensive test of the semantic analyzer with a more complex program.
Tests global/local variables, multiple functions, and initialization.
"""

import sys
sys.path.insert(0, 'D:/Repositories/platter-compiler-webapp/backend')

from app.lexer.lexer import Lexer
from app.parser.parser import Parser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

def test_complex_program():
    """Test with a more realistic Platter program"""
    
    code = """
    piece of globalCounter, maxValue = 100;
    sip of PI = 3.14159;
    flag of debugMode = true;
    
    start() {
        piece of result;
        sip of temperature = 98.6;
        
        bill(globalCounter);
    }
    """
    
    print("=" * 80)
    print("COMPREHENSIVE SEMANTIC ANALYZER TEST")
    print("=" * 80)
    print("\nSource Code:")
    print("-" * 80)
    print(code)
    print("-" * 80)
    
    # Lexing
    print("\n[1/3] Lexical Analysis...")
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    print(f"  ✓ Generated {len(tokens)} tokens")
    
    # Parsing
    print("\n[2/3] Parsing (Building AST)...")
    parser = Parser(tokens)
    ast = parser.parse()
    
    if not ast:
        print("  ✗ ERROR: Parsing failed")
        return False
    
    print(f"  ✓ AST built successfully")
    
    # Semantic Analysis
    print("\n[3/3] Semantic Analysis (Multi-Pass)...")
    analyzer = SemanticAnalyzer(ast)
    success = analyzer.analyze()
    
    # Results
    print("\n" + "=" * 80)
    if success:
        print("✓ TEST PASSED: All semantic analysis passes completed")
        print("=" * 80)
        
        # Detailed analysis
        print("\nDetailed Symbol Table Analysis:")
        print("-" * 80)
        
        ingredient_table = analyzer.get_ingredient_table()
        recipe_table = analyzer.get_recipe_table()
        
        # Analyze global variables
        all_ingredients = ingredient_table.get_all_ingredients()
        global_vars = []
        local_vars = []
        
        for name, declarations in all_ingredients.items():
            for decl in declarations:
                if decl['is_global']:
                    global_vars.append(decl)
                else:
                    local_vars.append(decl)
        
        print(f"\nGlobal Variables: {len(global_vars)}")
        for var in global_vars:
            init_str = f" = {var['init_value']}" if var['initialized'] else ""
            print(f"  • {var['name']:<20} : {var['type']}{init_str}")
        
        print(f"\nLocal Variables: {len(local_vars)}")
        for var in local_vars:
            print(f"  • {var['name']:<20} : {var['type']} (in {var['scope']})")
        
        print(f"\nRecipes/Functions: {len(recipe_table.get_all_recipes())}")
        for name, recipe in recipe_table.get_all_recipes().items():
            main_marker = " [MAIN ENTRY POINT]" if recipe['is_main'] else ""
            print(f"  • {name}(){main_marker}")
        
        return True
    else:
        print("✗ TEST FAILED: Semantic analysis errors found")
        print("=" * 80)
        
        errors = analyzer.get_errors()
        for i, error in enumerate(errors, 1):
            print(f"  {i}. ERROR: {error}")
        
        warnings = analyzer.get_warnings()
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. WARNING: {warning}")
        
        return False


def test_error_detection():
    """Test error detection with duplicate declarations"""
    
    code = """
    piece of x;
    piece of x;  # Duplicate!
    
    start() {
    }
    """
    
    print("\n\n" + "=" * 80)
    print("ERROR DETECTION TEST (Duplicate Variable)")
    print("=" * 80)
    print("\nSource Code:")
    print("-" * 80)
    print(code)
    print("-" * 80)
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    if ast:
        analyzer = SemanticAnalyzer(ast)
        success = analyzer.analyze()
        
        if not success:
            print("\n✓ Correctly detected semantic error:")
            for error in analyzer.get_errors():
                print(f"  • {error}")
            return True
        else:
            print("\n✗ Failed to detect duplicate declaration error")
            return False
    
    return False


if __name__ == "__main__":
    # Suppress parser INFO/WARNING logs for clean output
    import logging
    parser_logger = logging.getLogger('app.parser.parser')
    parser_logger.setLevel(logging.ERROR)
    
    test1_passed = test_complex_program()
    test2_passed = test_error_detection()
    
    print("\n\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"Complex Program Test: {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"Error Detection Test: {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    print("=" * 80)
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Semantic analyzer is working correctly.")
    else:
        print("\n⚠ Some tests failed. Review the output above.")
