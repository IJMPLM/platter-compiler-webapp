"""
Logging Formatter for Semantic Analyzer

Provides comprehensive logging with formatted output for symbol tables.
Separates backend logging from frontend messages.
"""

import logging
from typing import Dict, List, Any


class SemanticLogger:
    """
    Custom logger for semantic analysis with formatted table output.
    Keeps detailed logs in backend terminal, sends minimal messages to frontend.
    """
    
    def __init__(self, name: str = "semantic_analyzer"):
        self.logger = logging.getLogger(name)
        self.frontend_messages = []  # Messages to send to frontend
        
    def info(self, message: str, to_frontend: bool = False):
        """Log info message. Set to_frontend=True to also send to frontend."""
        self.logger.info(message)
        if to_frontend:
            self.frontend_messages.append({"level": "info", "message": message})
    
    def error(self, message: str, to_frontend: bool = True):
        """Log error message. Automatically sent to frontend unless to_frontend=False."""
        self.logger.error(message)
        if to_frontend:
            self.frontend_messages.append({"level": "error", "message": message})
    
    def warning(self, message: str, to_frontend: bool = False):
        """Log warning message."""
        self.logger.warning(message)
        if to_frontend:
            self.frontend_messages.append({"level": "warning", "message": message})
    
    def debug(self, message: str):
        """Log debug message (backend only)."""
        self.logger.debug(message)
    
    def get_frontend_messages(self):
        """Get messages to send to frontend."""
        return self.frontend_messages
    
    def clear_frontend_messages(self):
        """Clear frontend message buffer."""
        self.frontend_messages = []


def format_ingredient_table(ingredients: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Format ingredient table with columns for all metadata fields.
    
    Returns formatted string suitable for terminal output.
    """
    if not ingredients:
        return "  (no ingredients)\n"
    
    # Collect all ingredients
    all_vars = []
    for name, declarations in ingredients.items():
        all_vars.extend(declarations)
    
    if not all_vars:
        return "  (no ingredients)\n"
    
    # Separate global and local
    global_vars = [v for v in all_vars if v['is_global']]
    local_vars = [v for v in all_vars if not v['is_global']]
    
    output = []
    
    # Format global variables
    if global_vars:
        output.append("\n  GLOBAL INGREDIENTS:")
        output.append("  " + "-" * 140)
        output.append(f"  {'Name':<20} {'Type':<10} {'Array':<8} {'Dims':<15} {'Init':<6} {'InitVal':<15} {'Line':<6} {'Col':<6}")
        output.append("  " + "-" * 140)
        
        for var in global_vars:
            name = var['name']
            vtype = var['type']
            is_array = 'Yes' if var['is_array'] else 'No'
            dims = str(var['dimensions']) if var['dimensions'] else '-'
            initialized = 'Yes' if var['initialized'] else 'No'
            init_val = str(var['init_value']) if var['init_value'] else '-'
            line = str(var['line'])
            col = str(var['col'])
            
            output.append(f"  {name:<20} {vtype:<10} {is_array:<8} {dims:<15} {initialized:<6} {init_val:<15} {line:<6} {col:<6}")
    
    # Format local variables
    if local_vars:
        output.append("\n  LOCAL INGREDIENTS:")
        output.append("  " + "-" * 160)
        output.append(f"  {'Name':<20} {'Type':<10} {'Scope':<15} {'Level':<7} {'Array':<8} {'Dims':<15} {'Param':<7} {'Line':<6} {'Col':<6}")
        output.append("  " + "-" * 160)
        
        for var in local_vars:
            name = var['name']
            vtype = var['type']
            scope = var['scope']
            level = str(var['scope_level'])
            is_array = 'Yes' if var['is_array'] else 'No'
            dims = str(var['dimensions']) if var['dimensions'] else '-'
            is_param = 'Yes' if var['is_parameter'] else 'No'
            line = str(var['line'])
            col = str(var['col'])
            
            output.append(f"  {name:<20} {vtype:<10} {scope:<15} {level:<7} {is_array:<8} {dims:<15} {is_param:<7} {line:<6} {col:<6}")
    
    return "\n".join(output)


def format_recipe_table(recipes: Dict[str, Dict[str, Any]]) -> str:
    """
    Format recipe table with columns for all metadata fields.
    
    Returns formatted string suitable for terminal output.
    """
    if not recipes:
        return "  (no recipes)\n"
    
    output = []
    output.append("\n  RECIPES (FUNCTIONS):")
    output.append("  " + "-" * 160)
    output.append(f"  {'Name':<20} {'Return Type':<15} {'Params':<7} {'Main':<6} {'Builtin':<9} {'Line':<6} {'Col':<6} {'Parameter Details':<50}")
    output.append("  " + "-" * 160)
    
    for name, recipe in recipes.items():
        recipe_name = name
        return_type = recipe['return_type'] if recipe['return_type'] else 'void'
        param_count = str(recipe['parameter_count'])
        is_main = 'Yes' if recipe['is_main'] else 'No'
        is_builtin = 'Yes' if recipe['is_builtin'] else 'No'
        line = str(recipe['line'])
        col = str(recipe['col'])
        
        # Format parameters
        if recipe['parameters']:
            param_details = ", ".join([f"{p['name']}:{p['type']}" for p in recipe['parameters']])
        else:
            param_details = '-'
        
        output.append(f"  {recipe_name:<20} {return_type:<15} {param_count:<7} {is_main:<6} {is_builtin:<9} {line:<6} {col:<6} {param_details:<50}")
    
    return "\n".join(output)


def format_pass_header(pass_num: int, pass_name: str) -> str:
    """Format a pass header."""
    return f"\n{'='*80}\nPASS {pass_num}: {pass_name}\n{'='*80}"


def format_section_header(title: str, width: int = 80) -> str:
    """Format a section header."""
    return f"\n{'-'*width}\n{title}\n{'-'*width}"


def format_summary(ingredient_count: int, recipe_count: int, error_count: int, warning_count: int) -> str:
    """Format analysis summary."""
    output = []
    output.append("\n" + "="*80)
    output.append("SEMANTIC ANALYSIS SUMMARY")
    output.append("="*80)
    output.append(f"  Ingredients: {ingredient_count}")
    output.append(f"  Recipes: {recipe_count}")
    output.append(f"  Errors: {error_count}")
    output.append(f"  Warnings: {warning_count}")
    output.append("="*80)
    return "\n".join(output)
