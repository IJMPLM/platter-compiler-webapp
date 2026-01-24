"""
Automated Parser Method Converter
Converts all parser methods to return ParseNode objects.

Usage:
    python convert_parser.py

This will:
1. Backup parser.py to parser.py.backup
2. Convert all methods to build parse tree
3. Save updated parser.py
"""

import re
import os
from pathlib import Path

def convert_method(method_text, method_name):
    """
    Convert a single method to return ParseNode.
    
    Returns: (converted_text, was_converted)
    """
    # Skip if already has ParseNode or is a utility method
    skip_methods = ['__init__', 'advance', 'upd_tok_attr', 'error_handler']
    if method_name in skip_methods:
        return method_text, False
    
    # Already converted
    if 'ParseNode' in method_text and 'node = ParseNode' in method_text:
        return method_text, False
    
    # Already has parse_token returning node
    if method_name == 'parse_token' and 'return node' in method_text:
        return method_text, False
    
    # Already has parse() returning ast
    if method_name == 'parse' and 'self.ast = self.program()' in method_text:
        return method_text, False
    
    lines = method_text.split('\n')
    new_lines = []
    indent = None
    node_added = False
    
    for i, line in enumerate(lines):
        # Keep method definition
        if i == 0:
            new_lines.append(line)
            continue
        
        # Detect indent level
        if indent is None and line.strip() and not line.strip().startswith('#'):
            indent = len(line) - len(line.lstrip())
        
        # Add node creation after first log.info("Enter:
        if not node_added and 'log.info("Enter:' in line:
            new_lines.append(line)
            if indent:
                node_line = ' ' * indent + f'node = ParseNode("<{method_name}>")'
                new_lines.append(node_line)
                new_lines.append('')
                node_added = True
            continue
        
        # Convert self.method() calls to node.add_child(self.method())
        if node_added and 'self.' in line and '(' in line:
            # Skip certain lines
            if any(skip in line for skip in ['log.', 'error_handler', 'advance', 'upd_tok_attr', 
                                              'current_tok', 'PREDICT_SET', 'add_child', 'pos',
                                              'tokens', 'tokenlist', 'result']):
                new_lines.append(line)
                continue
            
            # Check if it's a method call that should be wrapped
            stripped = line.strip()
            if re.match(r'^self\.\w+\([^)]*\)$', stripped):
                current_indent = len(line) - len(line.lstrip())
                new_line = ' ' * current_indent + f'node.add_child({stripped})'
                new_lines.append(new_line)
                continue
        
        # Convert return statements
        if node_added and line.strip().startswith('return'):
            stripped = line.strip()
            current_indent = len(line) - len(line.lstrip())
            
            if stripped == 'return' or stripped.startswith('return #'):
                comment = ' # λ' if '#' in stripped else ''
                new_lines.append(' ' * current_indent + f'return node{comment}')
                continue
        
        # Keep line as-is
        new_lines.append(line)
    
    # Add return node at the end if needed and node was added
    if node_added:
        # Check if last meaningful line has return
        last_code_line = None
        for line in reversed(new_lines):
            if line.strip() and not line.strip().startswith('#'):
                last_code_line = line
                break
        
        if last_code_line and 'return' not in last_code_line:
            # Find indent from last log.info or similar
            for line in reversed(new_lines):
                if line.strip() and ('log.info' in line or 'if ' in line):
                    indent_level = len(line) - len(line.lstrip())
                    new_lines.append(' ' * indent_level + 'return node')
                    break
    
    converted_text = '\n'.join(new_lines)
    return converted_text, node_added


def extract_methods(content):
    """Extract all methods from the Parser class."""
    # Find Parser class
    class_match = re.search(r'^class Parser:', content, re.MULTILINE)
    if not class_match:
        return []
    
    # Get everything after class definition
    class_start = class_match.end()
    class_content = content[class_start:]
    
    # Find all method definitions
    methods = []
    method_pattern = r'^    def (\w+)\(self[^)]*\):'
    
    for match in re.finditer(method_pattern, class_content, re.MULTILINE):
        method_name = match.group(1)
        method_start = match.start()
        
        # Find method end (next method or end of class)
        next_method = re.search(method_pattern, class_content[match.end():], re.MULTILINE)
        if next_method:
            method_end = match.end() + next_method.start()
        else:
            # Find end of class (if __name__ or end of file)
            if_main = re.search(r'^if __name__', class_content[match.end():], re.MULTILINE)
            if if_main:
                method_end = match.end() + if_main.start()
            else:
                method_end = len(class_content)
        
        method_text = class_content[method_start:method_end].rstrip()
        methods.append((method_name, method_text, method_start + class_start))
    
    return methods


def convert_parser_file(input_file, output_file=None, backup=True):
    """
    Convert entire parser.py file.
    
    Args:
        input_file: Path to parser.py
        output_file: Path for output (default: overwrites input)
        backup: Whether to create .backup file
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: {input_file} not found")
        return False
    
    # Read original file
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    if backup:
        backup_path = input_path.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Backup created: {backup_path}")
    
    # Check if ParseNode import exists
    if 'from app.parser.ast_nodes import ParseNode' not in content:
        # Add import after other parser imports
        import_pattern = r'(from app\.parser\.predict_set_err import PREDICT_SET_ERR\n)'
        content = re.sub(
            import_pattern,
            r'\1from app.parser.ast_nodes import ParseNode\n',
            content
        )
        print("✓ Added ParseNode import")
    
    # Add self.ast to __init__ if not present
    if 'self.ast = None' not in content:
        init_pattern = r'(self\.result = True\n)'
        content = re.sub(
            init_pattern,
            r'\1        self.ast = None  # Root of the parse tree\n',
            content
        )
        print("✓ Added self.ast to __init__")
    
    # Extract and convert methods
    methods = extract_methods(content)
    print(f"\n Found {len(methods)} methods to process...")
    
    converted_count = 0
    skipped_count = 0
    
    # Convert methods in reverse order (to preserve positions)
    for method_name, method_text, position in reversed(methods):
        converted, was_converted = convert_method(method_text, method_name)
        
        if was_converted:
            # Replace in content
            content = content[:position] + converted + content[position + len(method_text):]
            converted_count += 1
            print(f"  ✓ Converted: {method_name}")
        else:
            skipped_count += 1
            if 'ParseNode' in method_text:
                print(f"  → Skipped (already converted): {method_name}")
            else:
                print(f"  → Skipped (utility method): {method_name}")
    
    # Update parse() method to return ast
    if 'return self.result' in content:
        content = content.replace(
            'self.program()\n        else: self.error_handler("Parse_err"',
            'self.ast = self.program()\n        else: self.error_handler("Parse_err"'
        )
        content = content.replace(
            'return self.result',
            'return self.ast'
        )
        print("  ✓ Updated parse() to return AST")
    
    # Update parse_token to return node
    if 'def parse_token(self, tok):' in content and 'return node' not in content.split('def advance(self')[0]:
        parse_token_pattern = r'(def parse_token\(self, tok\):.*?)(self\.advance\(tok\))'
        replacement = r'\1# Create node with current token info before advancing\n            token_obj = self.tokenlist[self.pos]\n            node = ParseNode(tok, token=token_obj)\n            \n            \2\n            return node'
        content = re.sub(parse_token_pattern, replacement, content, flags=re.DOTALL)
        print("  ✓ Updated parse_token() to return node")
    
    # Write output
    output_path = Path(output_file) if output_file else input_path
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n{'='*70}")
    print(f"Conversion Complete!")
    print(f"{'='*70}")
    print(f"  Converted: {converted_count} methods")
    print(f"  Skipped: {skipped_count} methods")
    print(f"  Output: {output_path}")
    if backup:
        print(f"  Backup: {backup_path}")
    print(f"{'='*70}")
    
    return True


if __name__ == "__main__":
    import sys
    
    # Get parser.py path
    script_dir = Path(__file__).parent
    parser_file = script_dir / "parser.py"
    
    if not parser_file.exists():
        print(f"Error: Cannot find parser.py at {parser_file}")
        print("Please run this script from the app/parser/ directory")
        sys.exit(1)
    
    print("=" * 70)
    print("AUTOMATED PARSER CONVERTER")
    print("=" * 70)
    print(f"\nTarget file: {parser_file}")
    print("\nThis will:")
    print("  1. Create backup (parser.py.backup)")
    print("  2. Add ParseNode import")
    print("  3. Add self.ast attribute")
    print("  4. Convert all methods to return ParseNode")
    print("  5. Update parse_token() and parse()")
    print()
    
    response = input("Proceed? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    success = convert_parser_file(parser_file, backup=True)
    
    if success:
        print("\n✓ Conversion successful!")
        print("\nNext steps:")
        print("  1. Review the changes")
        print("  2. Test with: python backend/tests/test_parse_tree.py")
        print("  3. If issues, restore from backup: mv parser.py.backup parser.py")
    else:
        print("\n✗ Conversion failed!")
        sys.exit(1)
