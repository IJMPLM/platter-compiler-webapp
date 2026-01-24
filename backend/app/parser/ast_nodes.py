"""
Generic Parse Tree Node Structure
Each node represents either:
- A non-terminal (grammar rule) with children
- A terminal (token) with token information
"""

class ParseNode:
    """
    Generic node for parse tree that mirrors CFG structure.
    Preserves all token information for semantic analysis passes.
    """
    
    def __init__(self, rule_name, token=None, children=None):
        """
        Args:
            rule_name: Grammar rule name (e.g., "<expr>", "id", "+")
            token: Original Token object (for terminals only)
            children: List of child ParseNode objects
        """
        self.rule = rule_name
        self.token = token
        self.children = children or []
        
        # Extract position info from token if available
        if token:
            self.line = token.line
            self.col = token.col
            self.value = token.value
            self.type = token.type
        else:
            self.line = None
            self.col = None
            self.value = None
            self.type = None
    
    def add_child(self, node):
        """Add a child node. Ignores None values (for optional productions)."""
        if node is not None:
            self.children.append(node)
        return self
    
    def is_terminal(self):
        """Check if this node represents a terminal token."""
        return self.token is not None
    
    def is_nonterminal(self):
        """Check if this node represents a non-terminal grammar rule."""
        return self.token is None
    
    def __repr__(self):
        if self.is_terminal():
            return f"ParseNode({self.rule}, value='{self.value}', line={self.line}, col={self.col})"
        else:
            return f"ParseNode({self.rule}, children={len(self.children)})"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        result = {
            "rule": self.rule,
            "is_terminal": self.is_terminal()
        }
        
        if self.is_terminal():
            result.update({
                "value": self.value,
                "type": self.type,
                "line": self.line,
                "col": self.col
            })
        else:
            result["children"] = [child.to_dict() for child in self.children]
        
        return result
    
    def print_tree(self, indent=0, prefix=""):
        """Pretty print the parse tree."""
        if self.is_terminal():
            print(f"{prefix}└── {self.rule}: '{self.value}' (line {self.line}, col {self.col})")
        else:
            print(f"{prefix}└── {self.rule}")
            for i, child in enumerate(self.children):
                is_last = i == len(self.children) - 1
                extension = "    " if is_last else "│   "
                child.print_tree(indent + 1, prefix + extension)
