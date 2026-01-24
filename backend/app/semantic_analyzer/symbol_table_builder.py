"""
Semantic Analysis Pass 1: Symbol Table Builder

Builds two separate symbol tables:
1. Ingredient Table (Variables): Global and local variable declarations
2. Recipe Table (Functions): Function/recipe declarations with parameters

This is the first pass in the semantic analysis phase.
"""

import logging
from .logging_formatter import SemanticLogger, format_ingredient_table, format_recipe_table, format_pass_header

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = SemanticLogger(__name__)


class IngredientTable:
    """
    Symbol table for variable declarations (ingredients).
    Tracks all variables with their types, scopes, and initialization status.
    """
    
    def __init__(self):
        self.ingredients = {}  # name -> [list of declarations in different scopes]
        self.scope_stack = [{'name': 'global', 'level': 0, 'variables': {}}]
        self.current_scope_level = 0
    
    def enter_scope(self, scope_name='local'):
        """Enter a new scope (function, block, etc.)"""
        self.current_scope_level += 1
        new_scope = {
            'name': scope_name,
            'level': self.current_scope_level,
            'variables': {}
        }
        self.scope_stack.append(new_scope)
        logger.debug(f"Entered scope: {scope_name} (level {self.current_scope_level})")
    
    def exit_scope(self):
        """Exit current scope"""
        if len(self.scope_stack) > 1:
            exited = self.scope_stack.pop()
            self.current_scope_level -= 1
            logger.debug(f"Exited scope: {exited['name']} (level {exited['level']})")
    
    def declare(self, name, var_type, line, col, is_array=False, dimensions=None, 
                initialized=False, init_value=None, is_parameter=False):
        """
        Declare a variable in the current scope.
        
        Args:
            name: Variable name
            var_type: Data type (piece, sip, flag, chars, table name)
            line, col: Source location
            is_array: Whether it's an array
            dimensions: Array dimensions if applicable
            initialized: Whether it has an initial value
            init_value: The initial value if available
            is_parameter: Whether it's a function parameter
        """
        current_scope = self.scope_stack[-1]
        
        # Check for redeclaration in current scope
        if name in current_scope['variables']:
            existing = current_scope['variables'][name]
            raise SemanticError(
                f"Redeclaration of variable '{name}' at line {line}, col {col}. "
                f"Previously declared at line {existing['line']}, col {existing['col']}"
            )
        
        # Create symbol entry
        symbol_entry = {
            'name': name,
            'type': var_type,
            'line': line,
            'col': col,
            'scope': current_scope['name'],
            'scope_level': current_scope['level'],
            'is_array': is_array,
            'dimensions': dimensions or [],
            'initialized': initialized,
            'init_value': init_value,
            'is_parameter': is_parameter,
            'is_global': current_scope['level'] == 0,
            'used': False,  # Track if variable is ever used
            'assigned': initialized  # Track assignments
        }
        
        # Add to current scope
        current_scope['variables'][name] = symbol_entry
        
        # Add to global ingredient list
        if name not in self.ingredients:
            self.ingredients[name] = []
        self.ingredients[name].append(symbol_entry)
        
        logger.debug(
            f"Declared ingredient: {name} : {var_type} "
            f"(scope: {current_scope['name']}, line {line})"
        )
    
    def lookup(self, name):
        """
        Look up a variable in current and parent scopes.
        Returns the most recent declaration (from innermost scope).
        """
        for scope in reversed(self.scope_stack):
            if name in scope['variables']:
                return scope['variables'][name]
        return None
    
    def lookup_current_scope(self, name):
        """Look up a variable only in the current scope"""
        current_scope = self.scope_stack[-1]
        return current_scope['variables'].get(name)
    
    def mark_used(self, name):
        """Mark a variable as used (referenced)"""
        symbol = self.lookup(name)
        if symbol:
            symbol['used'] = True
    
    def mark_assigned(self, name):
        """Mark a variable as assigned"""
        symbol = self.lookup(name)
        if symbol:
            symbol['assigned'] = True
    
    def get_all_ingredients(self):
        """Get all ingredient declarations across all scopes"""
        return self.ingredients
    
    def get_current_scope_ingredients(self):
        """Get ingredients in current scope only"""
        return self.scope_stack[-1]['variables']
    
    def __repr__(self):
        total = sum(len(decls) for decls in self.ingredients.values())
        return f"IngredientTable({len(self.ingredients)} unique names, {total} total declarations)"


class RecipeTable:
    """
    Symbol table for function/recipe declarations.
    Tracks all recipes with their signatures, return types, and parameters.
    """
    
    def __init__(self):
        self.recipes = {}  # name -> recipe info
    
    def declare(self, name, line, col, return_type=None, parameters=None, 
                is_builtin=False, is_main=False):
        """
        Declare a recipe (function).
        
        Args:
            name: Recipe name
            line, col: Source location
            return_type: Return type (None for void/no return)
            parameters: List of parameter dictionaries
            is_builtin: Whether it's a built-in function
            is_main: Whether it's the start() function
        """
        # Check for redeclaration
        if name in self.recipes:
            existing = self.recipes[name]
            raise SemanticError(
                f"Redeclaration of recipe '{name}' at line {line}, col {col}. "
                f"Previously declared at line {existing['line']}, col {existing['col']}"
            )
        
        # Create recipe entry
        recipe_entry = {
            'name': name,
            'line': line,
            'col': col,
            'return_type': return_type,
            'parameters': parameters or [],
            'parameter_count': len(parameters) if parameters else 0,
            'is_builtin': is_builtin,
            'is_main': is_main,
            'called': False,  # Track if recipe is ever called
            'recursive': False,  # Track if recipe is recursive
            'body_analyzed': False  # Track analysis status
        }
        
        self.recipes[name] = recipe_entry
        
        logger.debug(
            f"Declared recipe: {name}({recipe_entry['parameter_count']} params) "
            f"-> {return_type or 'void'} (line {line})"
        )
    
    def lookup(self, name):
        """Look up a recipe by name"""
        return self.recipes.get(name)
    
    def mark_called(self, name):
        """Mark a recipe as called"""
        if name in self.recipes:
            self.recipes[name]['called'] = True
    
    def mark_recursive(self, name):
        """Mark a recipe as recursive"""
        if name in self.recipes:
            self.recipes[name]['recursive'] = True
    
    def get_all_recipes(self):
        """Get all recipe declarations"""
        return self.recipes
    
    def __repr__(self):
        return f"RecipeTable({len(self.recipes)} recipes)"


class SemanticError(Exception):
    """Exception raised for semantic errors"""
    pass


class SymbolTableBuilder:
    """
    Pass 1: Build Symbol Tables
    
    Traverses the AST and builds:
    1. Ingredient Table (variables)
    2. Recipe Table (functions)
    
    Also performs basic declaration checks:
    - No duplicate declarations in same scope
    - Proper structure
    """
    
    def __init__(self, ast):
        self.ast = ast
        self.ingredient_table = IngredientTable()
        self.recipe_table = RecipeTable()
        self.errors = []
        self.warnings = []
        self.current_recipe = None  # Track current recipe context
    
    def build(self):
        """Main entry point to build symbol tables"""
        logger.info(format_pass_header(1, "SYMBOL TABLE CONSTRUCTION"))
        
        try:
            self.visit_program(self.ast)
            
            # Log results
            self.log_tables()
            
            if self.errors:
                logger.error(f"\nFound {len(self.errors)} error(s):", to_frontend=True)
                for error in self.errors:
                    logger.error(f"  - {error}", to_frontend=True)
                return False
            
            if self.warnings:
                logger.warning(f"\nFound {len(self.warnings)} warning(s):")
                for warning in self.warnings:
                    logger.warning(f"  - {warning}")
            
            logger.info("\n" + "="*80)
            logger.info("PASS 1 COMPLETE: Symbol tables built successfully", to_frontend=True)
            logger.info("="*80)
            return True
            
        except SemanticError as e:
            self.errors.append(str(e))
            logger.error(f"\nSemantic Error: {e}", to_frontend=True)
            return False
        except Exception as e:
            self.errors.append(f"Internal error: {e}")
            logger.error(f"\nInternal Error: {e}", to_frontend=True)
            import traceback
            traceback.print_exc()
            return False
    
    def log_tables(self):
        """Log the contents of both symbol tables"""
        # Format ingredient table
        ingredients = self.ingredient_table.get_all_ingredients()
        ingredient_table_str = format_ingredient_table(ingredients)
        logger.info("\n" + ingredient_table_str)
        
        # Format recipe table
        recipes = self.recipe_table.get_all_recipes()
        recipe_table_str = format_recipe_table(recipes)
        logger.info("\n" + recipe_table_str)
    
    def visit_program(self, node):
        """Visit <program> node"""
        if node.rule != "<program>":
            raise SemanticError("Expected <program> node at root")
        
        logger.debug("Visiting program node")
        
        for child in node.children:
            if child.is_terminal():
                continue
            
            if child.rule == "<global_decl>":
                self.visit_global_decl(child)
            elif child.rule == "<recipe_decl>":
                self.visit_recipe_decl(child)
            elif child.rule == "<platter>" and not child.is_terminal():
                # This is the main platter (start function body)
                # Register start() as a recipe if not already done
                if 'start' not in self.recipe_table.recipes:
                    # Find line/col from 'start' token
                    for c in node.children:
                        if c.is_terminal() and c.value == 'start':
                            self.recipe_table.declare(
                                'start', c.line, c.col,
                                return_type=None,
                                parameters=[],
                                is_main=True
                            )
                            break
                
                # Visit main platter with start scope
                self.current_recipe = 'start'
                self.ingredient_table.enter_scope('start')
                self.visit_platter(child)
                self.ingredient_table.exit_scope()
                self.current_recipe = None
    
    def visit_global_decl(self, node):
        """Visit <global_decl> node recursively"""
        if not node.children:
            return  # Lambda production
        
        for child in node.children:
            if child.is_terminal():
                continue
            
            if child.rule == "<decl_data_type>":
                self.visit_decl_data_type(child, is_global=True)
            elif child.rule == "<table_prototype>":
                self.visit_table_prototype(child)
            elif child.rule == "<table_decl>":
                # Handle table instance declaration
                pass  # TODO: Implement table handling
            elif child.rule == "<global_decl>":
                # Recursive
                self.visit_global_decl(child)
    
    def visit_decl_data_type(self, node, is_global=False):
        """
        Visit <decl_data_type> node
        
        Structure - may contain MULTIPLE declarations:
        <decl_data_type>
        ├── piece (token)
        ├── <decl_type>
        ├── sip (token)
        ├── <decl_type>
        └── ...
        
        We need to pair each type token with its following decl_type node.
        """
        i = 0
        while i < len(node.children):
            child = node.children[i]
            
            # Look for type tokens
            if child.is_terminal() and child.type in ['piece', 'sip', 'flag', 'chars']:
                type_token = child
                # Find the next <decl_type> node
                for j in range(i + 1, len(node.children)):
                    next_child = node.children[j]
                    if next_child.rule == "<decl_type>":
                        decl_type_node = next_child
                        logger.debug(f"Processing declaration: {type_token.value}")
                        self.visit_decl_type(decl_type_node, type_token.value, is_global)
                        i = j  # Skip to this position
                        break
            
            i += 1
    
    def visit_decl_type(self, node, data_type, is_global):
        """Visit <decl_type> node - handles both simple and array declarations"""
        dims = []
        has_dimensions = False
        
        for child in node.children:
            if child.is_terminal():
                continue
            
            if child.rule == "<dimensions>":
                has_dimensions = True
                dims = self.extract_dimensions(child)
            elif child.rule == "<ingredient_id>":
                # Simple variable declaration
                self.visit_ingredient_id(child, data_type, is_array=False)
            elif child.rule == "<array_declare>":
                # Array declaration
                self.visit_array_declare(child, data_type, dims)
    
    def visit_ingredient_id(self, node, data_type, is_array=False, dimensions=None, is_parameter=False):
        """Visit <ingredient_id> node and extract variable names"""
        for child in node.children:
            if child.is_terminal() and child.type == 'id':
                # Extract initialization if present
                initialized = False
                init_value = None
                
                # Check for initialization in sibling nodes
                for sibling in node.children:
                    if sibling.rule == "<ingredient_init>":
                        initialized, init_value = self.extract_init_value(sibling)
                
                # Declare the ingredient
                self.ingredient_table.declare(
                    name=child.value,
                    var_type=data_type,
                    line=child.line,
                    col=child.col,
                    is_array=is_array,
                    dimensions=dimensions,
                    initialized=initialized,
                    init_value=init_value,
                    is_parameter=is_parameter
                )
            
            elif child.rule == "<ingredient_id_tail>":
                self.visit_ingredient_id_tail(child, data_type, is_array, dimensions, is_parameter)
    
    def visit_ingredient_id_tail(self, node, data_type, is_array, dimensions, is_parameter):
        """
        Visit <ingredient_id_tail> for comma-separated declarations.
        
        Structure:
        <ingredient_id_tail>
        ├── , (token)
        ├── id (token)
        ├── <ingredient_init>
        └── <ingredient_id_tail> (recursive)
        
        or empty (lambda production)
        """
        if not node.children:
            return  # Lambda production
        
        # Extract id token and check for initialization
        id_token = None
        initialized = False
        init_value = None
        
        for child in node.children:
            if child.is_terminal() and child.type == 'id':
                id_token = child
            elif child.rule == "<ingredient_init>":
                initialized, init_value = self.extract_init_value(child)
        
        # Declare if we found an id
        if id_token:
            self.ingredient_table.declare(
                name=id_token.value,
                var_type=data_type,
                line=id_token.line,
                col=id_token.col,
                is_array=is_array,
                dimensions=dimensions,
                initialized=initialized,
                init_value=init_value,
                is_parameter=is_parameter
            )
        
        # Process recursive tail
        for child in node.children:
            if child.rule == "<ingredient_id_tail>":
                self.visit_ingredient_id_tail(child, data_type, is_array, dimensions, is_parameter)
    
    def extract_init_value(self, init_node):
        """Extract initialization value from <ingredient_init> node"""
        # For now, extract simple literals
        # Full expression evaluation will be in later passes
        if not init_node.children:
            return (False, None)
        
        # Look for assignment and expression
        for child in init_node.children:
            if child.rule == "<expression>":
                # Try to extract literal value
                literal = self.extract_literal_from_expr(child)
                if literal is not None:
                    return (True, literal)
                return (True, "<expression>")
        
        return (True, "<expression>")
    
    def extract_literal_from_expr(self, expr_node):
        """Try to extract a literal value from an expression tree"""
        # Traverse down to find terminal values
        if expr_node.is_terminal():
            return expr_node.value
        
        # Recursively search children
        for child in expr_node.children:
            if child.is_terminal() and child.value and child.value not in ['+', '-', '*', '/', '(', ')']:
                return child.value
            if not child.is_terminal():
                result = self.extract_literal_from_expr(child)
                if result is not None:
                    return result
        
        return None
    
    def extract_dimensions(self, dims_node):
        """Extract array dimensions from <dimensions> node"""
        dimensions = []
        
        # Look for <dimension_list> child
        for child in dims_node.children:
            if child.rule == "<dimension_list>":
                dimensions = self.extract_dimension_list(child)
                break
        
        return dimensions
    
    def extract_dimension_list(self, dim_list_node):
        """Recursively extract dimensions from <dimension_list>"""
        dimensions = []
        
        # <dimension_list> can be:
        # <dimension_list> → <numeric> <dimension_list_tail>
        # Look for numeric terminals
        for child in dim_list_node.children:
            if child.is_terminal() and child.type == "NUMERIC":
                dimensions.append(child.value)
            elif child.rule == "<dimension_list_tail>":
                # Recursively get more dimensions
                tail_dims = self.extract_dimension_list(child)
                dimensions.extend(tail_dims)
            elif not child.is_terminal():
                # Recursively search other non-terminals
                nested_dims = self.extract_dimension_list(child)
                dimensions.extend(nested_dims)
        
        return dimensions
    
    def visit_array_declare(self, node, data_type, dimensions):
        """Visit <array_declare> node for array ingredient declarations"""
        # <array_declare> → id <array_table_init> <array_declare_tail>
        # Extract identifier and declare as array
        is_array = True
        id_token = None
        
        logger.debug(f"Visiting array_declare for type: {data_type}, dimensions: {dimensions}")
        
        for child in node.children:
            if child.is_terminal() and child.type == "id":
                id_token = child
                logger.debug(f"Found array identifier: {child.value}")
            elif child.rule == "<dimensions>":
                # Additional dimensions inside array_declare
                extra_dims = self.extract_dimensions(child)
                dimensions.extend(extra_dims)
        
        # Declare the array ingredient
        if id_token:
            logger.debug(f"Declaring array: {id_token.value} : {data_type}[] at line {id_token.line}, col {id_token.col}")
            self.ingredient_table.declare(
                name=id_token.value,
                var_type=data_type,
                line=id_token.line,
                col=id_token.col,
                is_array=True,
                dimensions=dimensions,
                initialized=False,
                init_value=None,
                is_parameter=False
            )
        else:
            logger.warning(f"No identifier found in array_declare node for type {data_type}")
    
    def visit_table_prototype(self, node):
        """Visit <table_prototype> node for struct/table type declarations"""
        # <table_prototype> → table <identifier> { <ingredient_list> }
        # For now, just log that we found a table declaration
        # Full table support will be added in later passes
        table_name = None
        
        for child in node.children:
            if child.is_terminal() and child.type == "IDENTIFIER":
                table_name = child.value
                logger.info(f"Found table declaration: {table_name} at line {child.line}, col {child.col}")
                break
        
        # TODO: Add table types to a separate symbol table
    
    def visit_recipe_decl(self, node):
        """
        Visit <recipe_decl> node
        
        Structure:
        <recipe_decl>
        ├── prepare (token)
        ├── id (token - recipe name)
        ├── ( (token)
        ├── <spice> (parameters)
        ├── ) (token)
        ├── <serve_type> (return type)
        └── <platter> (body)
        """
        recipe_name = None
        recipe_line = None
        recipe_col = None
        parameters = []
        return_type = None
        
        # Extract recipe information
        for i, child in enumerate(node.children):
            if child.is_terminal() and child.type == 'id':
                recipe_name = child.value
                recipe_line = child.line
                recipe_col = child.col
            elif child.rule == "<spice>":
                parameters = self.extract_parameters(child)
            elif child.rule == "<serve_type>":
                return_type = self.extract_return_type(child)
        
        if recipe_name:
            # Declare the recipe
            self.recipe_table.declare(
                name=recipe_name,
                line=recipe_line,
                col=recipe_col,
                return_type=return_type,
                parameters=parameters
            )
            
            # Visit recipe body with new scope
            self.current_recipe = recipe_name
            self.ingredient_table.enter_scope(recipe_name)
            
            # Add parameters to ingredient table
            for param in parameters:
                self.ingredient_table.declare(
                    name=param['name'],
                    var_type=param['type'],
                    line=param['line'],
                    col=param['col'],
                    is_array=param.get('is_array', False),
                    dimensions=param.get('dimensions', []),
                    is_parameter=True
                )
            
            # Visit body
            for child in node.children:
                if child.rule == "<platter>":
                    self.visit_platter(child)
            
            self.ingredient_table.exit_scope()
            self.current_recipe = None
    
    def extract_parameters(self, spice_node):
        """Extract parameter list from <spice> node"""
        # <spice> can be empty or contain <param_list>
        parameters = []
        
        for child in spice_node.children:
            if child.rule == "<param_list>":
                parameters = self.extract_param_list(child)
                break
        
        return parameters
    
    def extract_param_list(self, param_list_node):
        """Recursively extract parameters from <param_list>"""
        parameters = []
        
        # <param_list> → <param> <param_list_tail>
        # or similar recursive structure
        for child in param_list_node.children:
            if child.rule == "<param>":
                param_info = self.extract_param(child)
                if param_info:
                    parameters.append(param_info)
            elif child.rule == "<param_list_tail>":
                # Recursively get more parameters
                tail_params = self.extract_param_list(child)
                parameters.extend(tail_params)
            elif not child.is_terminal() and child.rule in ["<param_list>", "<param>"]:
                # Handle nested structures
                nested_params = self.extract_param_list(child)
                parameters.extend(nested_params)
        
        return parameters
    
    def extract_param(self, param_node):
        """Extract a single parameter from <param> node"""
        # <param> → <ingredient_type> of <identifier>
        # or <ingredient_type> [dimensions] of <identifier>
        param_type = None
        param_name = None
        param_line = None
        param_col = None
        is_array = False
        dimensions = []
        
        for child in param_node.children:
            # Look for type keywords
            if child.is_terminal() and child.type in ["PIECE", "SIP", "FLAG", "CHARS"]:
                param_type = child.value
            # Look for identifier
            elif child.is_terminal() and child.type == "IDENTIFIER":
                param_name = child.value
                param_line = child.line
                param_col = child.col
            # Look for dimensions (array parameter)
            elif child.rule == "<dimensions>":
                is_array = True
                dimensions = self.extract_dimensions(child)
        
        if param_name and param_type:
            return {
                'name': param_name,
                'type': param_type,
                'line': param_line,
                'col': param_col,
                'is_array': is_array,
                'dimensions': dimensions
            }
        
        return None
    
    def extract_return_type(self, serve_type_node):
        """Extract return type from <serve_type> node"""
        for child in serve_type_node.children:
            if child.is_terminal() and child.type in ['piece', 'sip', 'flag', 'chars']:
                return child.value
        return None  # void/no return
    
    def visit_platter(self, node):
        """Visit <platter> (block) node"""
        for child in node.children:
            if child.is_terminal():
                continue
            
            if child.rule == "<local_decl>":
                self.visit_local_decl(child)
            elif child.rule == "<statements>":
                # Will be fully handled in later passes
                pass
    
    def visit_local_decl(self, node):
        """Visit <local_decl> node for local variable declarations"""
        if not node.children:
            return
        
        for child in node.children:
            if child.is_terminal():
                continue
            
            if child.rule == "<decl_data_type>":
                self.visit_decl_data_type(child, is_global=False)
            elif child.rule == "<local_decl>":
                # Recursive
                self.visit_local_decl(child)
    
    def get_tables(self):
        """Return both symbol tables"""
        return {
            'ingredients': self.ingredient_table,
            'recipes': self.recipe_table
        }
