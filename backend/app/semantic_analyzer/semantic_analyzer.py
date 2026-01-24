"""
Semantic Analyzer - Multi-Pass Orchestrator

Orchestrates all semantic analysis passes on the AST:
1. Pass 1: Symbol Table Builder (ingredients and recipes)
2. Pass 2: Type Checking
3. Pass 3: Expression Validation  
4. Pass 4: Control Flow Analysis
5. Pass 5: Recipe Call Validation

Usage:
    analyzer = SemanticAnalyzer(ast)
    success = analyzer.analyze()
"""

import logging
from .symbol_table_builder import SymbolTableBuilder

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class SemanticAnalyzer:
    """
    Main semantic analyzer orchestrating all passes.
    
    Coordinates multi-pass semantic analysis ensuring:
    - Symbol tables are built before type checking
    - Type information available for expression validation
    - All declarations validated before usage checks
    - Clear separation of concerns across passes
    """
    
    def __init__(self, ast):
        self.ast = ast
        self.ingredient_table = None
        self.recipe_table = None
        self.errors = []
        self.warnings = []
        
    def analyze(self):
        """
        Execute all semantic analysis passes in sequence.
        
        Returns:
            bool: True if all passes succeed, False otherwise
        """
        logger.info("\n" + "="*80)
        logger.info("SEMANTIC ANALYSIS - MULTI-PASS")
        logger.info("="*80)
        
        # Pass 1: Build Symbol Tables
        if not self.pass1_symbol_tables():
            logger.error("\n✗ SEMANTIC ANALYSIS FAILED: Pass 1 (Symbol Tables) failed")
            return False
        
        # Pass 2: Type Checking
        if not self.pass2_type_checking():
            logger.error("\n✗ SEMANTIC ANALYSIS FAILED: Pass 2 (Type Checking) failed")
            return False
        
        # Pass 3: Expression Validation
        if not self.pass3_expression_validation():
            logger.error("\n✗ SEMANTIC ANALYSIS FAILED: Pass 3 (Expression Validation) failed")
            return False
        
        # Pass 4: Control Flow Analysis
        if not self.pass4_control_flow():
            logger.error("\n✗ SEMANTIC ANALYSIS FAILED: Pass 4 (Control Flow) failed")
            return False
        
        # Pass 5: Recipe Call Validation
        if not self.pass5_recipe_validation():
            logger.error("\n✗ SEMANTIC ANALYSIS FAILED: Pass 5 (Recipe Validation) failed")
            return False
        
        # Summary
        self.print_summary()
        
        logger.info("\n" + "="*80)
        logger.info("✓ SEMANTIC ANALYSIS COMPLETE: All passes succeeded")
        logger.info("="*80)
        
        return True
    
    def pass1_symbol_tables(self):
        """
        Pass 1: Build Symbol Tables
        
        Creates two separate symbol tables:
        - Ingredient Table: All variable declarations (global and local)
        - Recipe Table: All function/recipe declarations
        
        Validates:
        - No duplicate declarations in same scope
        - Proper declaration structure
        
        Returns:
            bool: True if symbol tables built successfully
        """
        logger.info("\n" + "▶"*40)
        logger.info("PASS 1: Symbol Table Construction")
        logger.info("▶"*40)
        
        try:
            builder = SymbolTableBuilder(self.ast)
            success = builder.build()
            
            if success:
                tables = builder.get_tables()
                self.ingredient_table = tables['ingredients']
                self.recipe_table = tables['recipes']
                
                # Collect any warnings
                self.warnings.extend(builder.warnings)
                
                logger.info("✓ Pass 1 Complete: Symbol tables built")
                return True
            else:
                self.errors.extend(builder.errors)
                logger.error("✗ Pass 1 Failed: Symbol table construction errors")
                return False
                
        except Exception as e:
            self.errors.append(f"Pass 1 internal error: {e}")
            logger.error(f"✗ Pass 1 Failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def pass2_type_checking(self):
        """
        Pass 2: Type Checking
        
        Validates type consistency:
        - Variable assignments match declared types
        - Function return types match declarations
        - Operator compatibility with operand types
        - Implicit type conversions (if allowed)
        
        Requires: Pass 1 complete (symbol tables available)
        
        Returns:
            bool: True if all type checks pass
        """
        logger.info("\n" + "▶"*40)
        logger.info("PASS 2: Type Checking")
        logger.info("▶"*40)
        logger.info("(Placeholder - Not yet implemented)")
        
        # TODO: Implement type checking
        # - Check assignments: lhs type == rhs type
        # - Check function calls: arg types match param types
        # - Check return statements: return type matches function signature
        # - Check array accesses: indices are integers
        # - Check operators: operands have compatible types
        
        logger.info("✓ Pass 2 Complete (placeholder)")
        return True
    
    def pass3_expression_validation(self):
        """
        Pass 3: Expression Validation
        
        Validates expression semantics:
        - All referenced variables are declared
        - Array indices are valid
        - Function calls reference existing functions
        - Correct number of arguments in calls
        - No use of uninitialized variables (flow-sensitive)
        
        Requires: Pass 1, 2 complete
        
        Returns:
            bool: True if all expressions are valid
        """
        logger.info("\n" + "▶"*40)
        logger.info("PASS 3: Expression Validation")
        logger.info("▶"*40)
        logger.info("(Placeholder - Not yet implemented)")
        
        # TODO: Implement expression validation
        # - Check variable references exist in symbol table
        # - Validate array access expressions
        # - Check function call arguments
        # - Detect use of uninitialized variables
        # - Validate operator usage
        
        logger.info("✓ Pass 3 Complete (placeholder)")
        return True
    
    def pass4_control_flow(self):
        """
        Pass 4: Control Flow Analysis
        
        Validates control flow:
        - All paths in non-void functions return a value
        - No unreachable code after return/break/continue
        - Break/continue only in loops
        - Proper loop structure
        - No infinite loops (if detectable)
        
        Requires: Pass 1-3 complete
        
        Returns:
            bool: True if control flow is valid
        """
        logger.info("\n" + "▶"*40)
        logger.info("PASS 4: Control Flow Analysis")
        logger.info("▶"*40)
        logger.info("(Placeholder - Not yet implemented)")
        
        # TODO: Implement control flow analysis
        # - Check return statements in all paths
        # - Detect unreachable code
        # - Validate break/continue placement
        # - Check for missing return in non-void functions
        # - Analyze loop termination
        
        logger.info("✓ Pass 4 Complete (placeholder)")
        return True
    
    def pass5_recipe_validation(self):
        """
        Pass 5: Recipe Call Validation
        
        Validates recipe/function usage:
        - Main function (start) exists
        - All called recipes are declared
        - Recursive calls are properly handled
        - No circular dependencies (if not allowed)
        - Unused function warnings
        
        Requires: Pass 1-4 complete
        
        Returns:
            bool: True if all recipe calls are valid
        """
        logger.info("\n" + "▶"*40)
        logger.info("PASS 5: Recipe Call Validation")
        logger.info("▶"*40)
        logger.info("(Placeholder - Not yet implemented)")
        
        # TODO: Implement recipe validation
        # - Check start() function exists
        # - Validate all recipe calls
        # - Check for undefined recipe calls
        # - Detect unused recipes (warning)
        # - Check for recursive calls
        
        logger.info("✓ Pass 5 Complete (placeholder)")
        return True
    
    def print_summary(self):
        """Print overall semantic analysis summary"""
        logger.info("\n" + "-"*80)
        logger.info("SEMANTIC ANALYSIS SUMMARY")
        logger.info("-"*80)
        
        if self.ingredient_table:
            ingredients = self.ingredient_table.get_all_ingredients()
            total_vars = sum(len(decls) for decls in ingredients.values())
            logger.info(f"  Ingredients: {len(ingredients)} unique names, {total_vars} total declarations")
        
        if self.recipe_table:
            recipes = self.recipe_table.get_all_recipes()
            logger.info(f"  Recipes: {len(recipes)} functions")
        
        if self.errors:
            logger.info(f"  Errors: {len(self.errors)}")
        else:
            logger.info("  Errors: 0")
        
        if self.warnings:
            logger.info(f"  Warnings: {len(self.warnings)}")
        else:
            logger.info("  Warnings: 0")
        
        logger.info("-"*80)
    
    def get_ingredient_table(self):
        """Get the ingredient symbol table"""
        return self.ingredient_table
    
    def get_recipe_table(self):
        """Get the recipe symbol table"""
        return self.recipe_table
    
    def get_errors(self):
        """Get all collected errors"""
        return self.errors
    
    def get_warnings(self):
        """Get all collected warnings"""
        return self.warnings
