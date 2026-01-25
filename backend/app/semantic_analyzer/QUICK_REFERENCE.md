# Semantic Analyzer Quick Reference

## Quick Start

```python
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

# After parsing:
analyzer = SemanticAnalyzer(ast)
success = analyzer.analyze()

if success:
    # Get symbol tables
    ingredients = analyzer.get_ingredient_table()
    recipes = analyzer.get_recipe_table()
```

## Symbol Table Queries

### Ingredient Table (Variables)

```python
# Look up a variable (searches all scopes)
symbol = ingredients.lookup('temperature')
if symbol:
    print(f"{symbol['name']}: {symbol['type']}")
    print(f"Line {symbol['line']}, Scope: {symbol['scope']}")
    print(f"Initialized: {symbol['initialized']}")
    print(f"Is parameter: {symbol['is_parameter']}")

# Look up in current scope only
local_symbol = ingredients.lookup_current_scope('count')

# Get all variables
all_vars = ingredients.get_all_ingredients()
for name, declarations in all_vars.items():
    for decl in declarations:
        print(f"{name}: {decl['type']} (line {decl['line']})")

# Filter global variables
global_vars = [decl for decls in all_vars.values() 
               for decl in decls if decl['is_global']]

# Filter local variables
local_vars = [decl for decls in all_vars.values() 
              for decl in decls if not decl['is_global']]
```

### Recipe Table (Functions)

```python
# Look up a function
recipe = recipes.lookup('calculateTotal')
if recipe:
    print(f"{recipe['name']}({recipe['parameter_count']} params)")
    print(f"Returns: {recipe['return_type']}")
    print(f"Is main: {recipe['is_main']}")
    
    # Get parameters
    for param in recipe['parameters']:
        print(f"  Parameter: {param['name']}: {param['type']}")

# Get all functions
all_recipes = recipes.get_all_recipes()
for name, recipe in all_recipes.items():
    print(f"{name}() at line {recipe['line']}")

# Mark functions as called (for later passes)
recipes.mark_called('myFunction')
recipes.mark_recursive('fibonacci')
```

## Scope Management (IngredientTable)

```python
# Enter a new scope
ingredients.enter_scope('myFunction')

# Declare variable in current scope
ingredients.declare(
    name='localVar',
    var_type='piece',
    line=10,
    col=5,
    is_array=False,
    dimensions=[],
    initialized=True,
    init_value='42',
    is_parameter=False
)

# Exit scope (removes local variables)
ingredients.exit_scope()
```

## Symbol Entry Structure

### Ingredient (Variable) Entry

```python
{
    'name': 'temperature',           # Variable name
    'type': 'sip',                   # Data type
    'line': 5,                       # Line number
    'col': 12,                       # Column number
    'scope': 'myFunction',           # Scope name
    'scope_level': 1,                # Scope depth (0=global)
    'is_array': False,               # Array flag
    'dimensions': [],                # Array dimensions
    'initialized': True,             # Has initial value
    'init_value': '98.6',           # Initialization value
    'is_parameter': False,           # Function parameter
    'is_global': False,              # Global scope
    'used': False,                   # Ever referenced
    'assigned': True                 # Ever assigned
}
```

### Recipe (Function) Entry

```python
{
    'name': 'calculate',             # Function name
    'line': 15,                      # Line number
    'col': 8,                        # Column number
    'return_type': 'piece',          # Return type (None=void)
    'parameters': [                  # Parameter list
        {
            'name': 'x',
            'type': 'piece',
            'line': 15,
            'col': 19
        }
    ],
    'parameter_count': 1,            # Number of parameters
    'is_builtin': False,             # Built-in function
    'is_main': False,                # start() function
    'called': False,                 # Ever called
    'recursive': False,              # Self-recursive
    'body_analyzed': False           # Body analyzed
}
```

## Error Handling

```python
success = analyzer.analyze()

if not success:
    # Get errors
    for error in analyzer.get_errors():
        print(f"ERROR: {error}")
    
    # Get warnings
    for warning in analyzer.get_warnings():
        print(f"WARNING: {warning}")
```

## Common Error Messages

```
Redeclaration of variable 'x' at line 5, col 10. 
Previously declared at line 2, col 14

Redeclaration of recipe 'myFunc' at line 20, col 8.
Previously declared at line 10, col 8
```

## Pass Status

- ✅ **Pass 1**: Symbol Tables - COMPLETE
- ⏳ **Pass 2**: Type Checking - PLACEHOLDER
- ⏳ **Pass 3**: Expression Validation - PLACEHOLDER
- ⏳ **Pass 4**: Control Flow - PLACEHOLDER
- ⏳ **Pass 5**: Recipe Validation - PLACEHOLDER

## Testing

```bash
# Basic test
python backend/tests/test_semantic_analyzer.py

# Comprehensive test
python backend/tests/test_semantic_comprehensive.py

# Debug AST structure
python backend/tests/debug_ast_structure.py
```

## Common Patterns

### Find all global variables of a type

```python
global_pieces = [
    decl for decls in ingredients.get_all_ingredients().values()
    for decl in decls
    if decl['is_global'] and decl['type'] == 'piece'
]
```

### Check if variable is declared

```python
if ingredients.lookup('myVar') is None:
    print("Variable not declared")
```

### Get main function

```python
start_func = recipes.lookup('start')
if start_func and start_func['is_main']:
    print("Main function found")
```

### Count parameters in all functions

```python
total_params = sum(
    recipe['parameter_count'] 
    for recipe in recipes.get_all_recipes().values()
)
```

## Next Steps

1. Implement Pass 2 (Type Checking)
2. Implement Pass 3 (Expression Validation)
3. Implement Pass 4 (Control Flow Analysis)
4. Implement Pass 5 (Recipe Call Validation)

## Files

- `semantic_analyzer.py` - Main orchestrator
- `symbol_table_builder.py` - Pass 1 implementation
- `README.md` - Full documentation
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
