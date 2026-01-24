"""
Automated converter to update all parser methods to return ParseNodes.
This script analyzes the parser.py file and generates the updated version.

Run this script to see a preview of all changes, then apply them.
"""

import re

def convert_method_to_parse_node(method_code, method_name):
    """
    Convert a parser method to return ParseNode.
    
    Strategy:
    1. Add node creation at start
    2. Replace method calls with node.add_child(...)
    3. Add return node at end
    4. Handle early returns
    """
    
    # Skip if already converted or is a utility method
    if 'ParseNode' in method_code:
        return method_code
    
    if method_name in ['__init__', 'parse_token', 'advance', 'upd_tok_attr', 
                       'error_handler', 'parse']:
        return method_code
    
    lines = method_code.split('\n')
    new_lines = []
    indent_level = None
    
    for i, line in enumerate(lines):
        # First line is def
        if i == 0:
            new_lines.append(line)
            continue
        
        # Find indent level from first non-empty line
        if indent_level is None and line.strip():
            indent_level = len(line) - len(line.lstrip())
        
        # Add node creation after log.info("Enter...")
        if 'log.info("Enter:' in line:
            new_lines.append(line)
            # Add node creation with proper indent
            node_line = ' ' * indent_level + f'node = ParseNode("<{method_name}>")'
            new_lines.append(node_line)
            new_lines.append('')  # Empty line for readability
            continue
        
        # Convert method calls to add_child
        # Pattern: self.method_call() or self.parse_token(...)
        if 'self.' in line and '(' in line and not any(skip in line for skip in 
            ['log.', 'error_handler', 'advance', 'upd_tok_attr', 'current_tok', 
             'tokenlist', 'PREDICT_SET', 'add_child']):
            
            # Extract the method call
            indent = len(line) - len(line.lstrip())
            stripped = line.strip()
            
            # Check if it's already a standalone method call
            if re.match(r'^self\.\w+\([^)]*\)$', stripped):
                # Wrap in node.add_child()
                new_line = ' ' * indent + f'node.add_child({stripped})'
                new_lines.append(new_line)
                continue
        
        # Handle return statements
        if line.strip().startswith('return') and line.strip() == 'return' or line.strip() == 'return # λ':
            indent = len(line) - len(line.lstrip())
            comment = ' # λ' if '# λ' in line else ''
            new_line = ' ' * indent + f'return node{comment}'
            new_lines.append(new_line)
            continue
        
        # Keep line as-is
        new_lines.append(line)
    
    # Add return node at the end if not present
    last_meaningful_line = None
    for line in reversed(new_lines):
        if line.strip() and not line.strip().startswith('#'):
            last_meaningful_line = line
            break
    
    if last_meaningful_line and 'return' not in last_meaningful_line:
        # Find proper indent (same as other statements in method)
        for line in reversed(new_lines):
            if line.strip() and 'log.info("Exit:' in line:
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + 'return node')
                break
    
    return '\n'.join(new_lines)


# Instructions for manual conversion
MANUAL_CONVERSION_TEMPLATE = """
For method: {method_name}
==========================

Add at start (after log.info("Enter:")):
    node = ParseNode("<{method_name}>")

Replace all:
    self.other_method()  →  node.add_child(self.other_method())
    self.parse_token(x)  →  node.add_child(self.parse_token(x))
    return  →  return node
    return # λ  →  return node # λ

Add at end (before log.info("Exit:")):
    return node

"""

if __name__ == "__main__":
    print("=" * 70)
    print("PARSER METHOD CONVERSION GUIDE")
    print("=" * 70)
    print()
    print("SYSTEMATIC APPROACH:")
    print("1. Work through methods in order they appear")
    print("2. Follow the pattern for each method type")
    print("3. Test after converting each section")
    print()
    print("METHOD CATEGORIES TO CONVERT:")
    print()
    print("✓ DONE:")
    print("  - parse_token")
    print("  - parse")
    print("  - program")
    print("  - global_decl")
    print("  - expr")
    print()
    print("TODO (in order):")
    categories = [
        ("Declarations", ["decl_data_type", "decl_type", "ingredient_id", 
                         "ingredient_init", "ingredient_id_tail"]),
        ("Expressions", ["or_expr", "and_expr", "eq_expr", "rel_expr", 
                        "add_expr", "mult_expr", "unary_expr", "primary_val"]),
        ("Expression Tails", ["or_tail", "and_tail", "eq_tail", "rel_tail", 
                             "add_tail", "mult_tail"]),
        ("Identifiers & Access", ["id_tail", "call_tailopt", "accessor_tail",
                                 "array_accessor", "table_accessor"]),
        ("Values", ["flavor", "value", "notation_val", "array_element", 
                   "element_value_tail", "array_element_id"]),
        ("Tables & Arrays", ["table_prototype", "table_decl", "dimensions",
                            "array_declare", "array_or_table", "field_assignments"]),
        ("Recipes", ["recipe_decl", "parameter_list", "platter"]),
        ("Statements", ["statements", "statement", "local_decl", 
                       "assignment_st", "recipe_call_st"]),
        ("Conditionals", ["conditional_st", "cond_check", "alt_clause",
                         "instead_clause", "cond_menu", "choice_clause"]),
        ("Loops", ["looping_st", "loop_pass", "loop_repeat", "loop_order"]),
        ("Jumps", ["jump_st", "jump_next", "jump_stop", "jump_serve"]),
        ("Built-in Functions", ["built_in_rec_call", "built_in_rec", "tail1"])
    ]
    
    for category, methods in categories:
        print(f"\n  {category}:")
        for method in methods:
            print(f"    - {method}")
    
    print("\n" + "=" * 70)
    print("Use the CONVERSION_GUIDE.py patterns for each method!")
    print("=" * 70)
