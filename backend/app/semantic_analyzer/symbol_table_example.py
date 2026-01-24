"""
Example: Building a Symbol Table from the Parse Tree

This demonstrates how the token-based parse tree enables
clean separation of semantic analysis from parsing.
"""

from app.parser.ast_nodes import ParseNode

class SymbolTable:
    """Simple symbol table for demonstration"""
    
    def __init__(self):
        self.symbols = {}
        self.scopes = [{}]  # Stack of scopes
    
    def enter_scope(self):
        """Enter a new scope (e.g., function body)"""
        self.scopes.append({})
    
    def exit_scope(self):
        """Exit current scope"""
        if len(self.scopes) > 1:
            self.scopes.pop()
    
    def declare(self, name, symbol_type, line, col):
        """Declare a symbol in current scope"""
        current_scope = self.scopes[-1]
        
        if name in current_scope:
            raise Exception(f"Redeclaration of '{name}' at line {line}, col {col}")
        
        current_scope[name] = {
            'type': symbol_type,
            'line': line,
            'col': col,
            'scope_level': len(self.scopes) - 1
        }
        
        # Also add to global symbols dict
        if name not in self.symbols:
            self.symbols[name] = []
        self.symbols[name].append(current_scope[name])
    
    def lookup(self, name):
        """Look up a symbol in current and parent scopes"""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def __repr__(self):
        return f"SymbolTable({len(self.symbols)} symbols)"


class SemanticAnalyzer:
    """
    Semantic analyzer that traverses the parse tree.
    
    Key advantage of token-based tree:
    - All token information (value, line, col) is preserved
    - Can extract identifier names, literal values, etc.
    - Clean separation from parsing logic
    """
    
    def __init__(self, parse_tree):
        self.tree = parse_tree
        self.symbol_table = SymbolTable()
        self.errors = []
    
    def analyze(self):
        """Main entry point for semantic analysis"""
        try:
            self.visit_program(self.tree)
            return self.symbol_table
        except Exception as e:
            self.errors.append(str(e))
            return None
    
    def visit_program(self, node):
        """Visit the <program> node"""
        if node.rule != "<program>":
            raise Exception("Expected <program> node")
        
        for child in node.children:
            if child.rule == "<global_decl>":
                self.visit_global_decl(child)
            elif child.rule == "<recipe_decl>":
                self.visit_recipe_decl(child)
            elif child.rule == "<platter>":
                # Visit main platter
                self.symbol_table.enter_scope()
                self.visit_platter(child)
                self.symbol_table.exit_scope()
    
    def visit_global_decl(self, node):
        """Visit global declarations"""
        if not node.children:
            return  # Empty (lambda) production
        
        for child in node.children:
            if child.rule == "<decl_data_type>":
                self.visit_decl_data_type(child)
            elif child.rule == "<global_decl>":
                # Recursive call
                self.visit_global_decl(child)
    
    def visit_decl_data_type(self, node):
        """
        Visit data type declaration.
        
        Example tree structure:
        <decl_data_type>
        ├── piece (token)
        └── <decl_type>
            ├── of (token)
            ├── <ingredient_id>
            │   ├── id (token with value="x")
            │   └── ...
            └── ; (token)
        """
        # Extract the type (first child is the type token)
        type_token = None
        decl_type_node = None
        
        for child in node.children:
            if child.is_terminal() and child.type in ['piece', 'sip', 'flag', 'chars']:
                type_token = child
            elif child.rule == "<decl_type>":
                decl_type_node = child
        
        if type_token and decl_type_node:
            # Find the ingredient_id node in decl_type
            self.visit_decl_type(decl_type_node, type_token.value)
    
    def visit_decl_type(self, node, data_type):
        """Visit declaration type and extract identifiers"""
        for child in node.children:
            if child.rule == "<ingredient_id>":
                self.visit_ingredient_id(child, data_type)
    
    def visit_ingredient_id(self, node, data_type):
        """
        Visit ingredient_id and register variables.
        
        This is where we extract the actual identifier NAME
        from the token stored in the tree!
        """
        for child in node.children:
            if child.is_terminal() and child.type == 'id':
                # HERE: We access the original token!
                var_name = child.value  # Get the actual identifier name
                line = child.line
                col = child.col
                
                # Declare in symbol table
                self.symbol_table.declare(var_name, data_type, line, col)
                print(f"   Declared: {var_name} : {data_type} (line {line}, col {col})")
            
            elif child.rule == "<ingredient_id_tail>":
                # Handle additional identifiers (comma-separated)
                self.visit_ingredient_id_tail(child, data_type)
    
    def visit_ingredient_id_tail(self, node, data_type):
        """Visit tail of identifier list"""
        for child in node.children:
            if child.is_terminal() and child.type == 'id':
                var_name = child.value
                self.symbol_table.declare(var_name, data_type, child.line, child.col)
                print(f"   Declared: {var_name} : {data_type} (line {child.line}, col {child.col})")
            elif child.rule == "<ingredient_id_tail>":
                self.visit_ingredient_id_tail(child, data_type)
    
    def visit_recipe_decl(self, node):
        """Visit recipe (function) declaration"""
        # Enter new scope for function
        self.symbol_table.enter_scope()
        
        # Extract recipe name, parameters, body...
        # (Implementation similar to above)
        
        self.symbol_table.exit_scope()
    
    def visit_platter(self, node):
        """Visit platter (block of statements)"""
        # Visit statements, handle local scoping
        pass


# Example usage
def example_semantic_analysis():
    """
    This shows how you'd use the semantic analyzer
    after parsing is complete.
    """
    from app.lexer.lexer import Lexer
    from app.parser.parser import Parser
    
    code = """
    piece of x, y;
    sip of temperature = 98.6;
    flag of isReady = true;
    
    start() {
        bill(x);
    }
    """
    
    print("=" * 70)
    print("SEMANTIC ANALYSIS EXAMPLE")
    print("=" * 70)
    
    # Step 1: Lex
    print("\n1. Lexical Analysis...")
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    # Step 2: Parse (builds tree)
    print("2. Syntax Analysis (building parse tree)...")
    parser = Parser(tokens)
    parse_tree = parser.parse()
    
    if parse_tree:
        print("   ✓ Parse tree built successfully")
        
        # Step 3: Semantic Analysis (separate pass!)
        print("\n3. Semantic Analysis (building symbol table)...")
        analyzer = SemanticAnalyzer(parse_tree)
        symbol_table = analyzer.analyze()
        
        if symbol_table:
            print(f"\n   ✓ Symbol table built: {len(symbol_table.symbols)} unique symbols")
            print("\n   Symbol Table:")
            print("   " + "-" * 50)
            for name, entries in symbol_table.symbols.items():
                for entry in entries:
                    print(f"   {name:<15} : {entry['type']:<10} (line {entry['line']}, scope {entry['scope_level']})")
            print("   " + "-" * 50)
        else:
            print("   ✗ Semantic analysis failed")
            for error in analyzer.errors:
                print(f"      Error: {error}")
    else:
        print("   ✗ Parse failed")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    print(__doc__)
    print("\nKey Benefits of Token-Based Parse Tree:")
    print("-" * 70)
    print("""
    1. CLEAN SEPARATION:
       - Parsing: Just builds the tree structure
       - Semantic: Separate pass over the tree
       - No coupling between phases
    
    2. TOKEN PRESERVATION:
       - Original token values available (identifier names, literals)
       - Line/column info for error reporting
       - Token type for validation
    
    3. FLEXIBLE ANALYSIS:
       - Multiple passes possible (symbol table, type check, etc.)
       - Can analyze tree in any order
       - Easy to extend with new analysis passes
    
    4. DEBUGGING:
       - Can print/visualize the tree
       - Can inspect at any point
       - Clear structure mirrors grammar
    """)
    
    print("\nRun the example:")
    print("-" * 70)
    # Uncomment to run:
    # example_semantic_analysis()
