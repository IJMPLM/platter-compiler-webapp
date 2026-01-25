from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.lexer.lexer import Lexer
from app.parser.parser import Parser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeInput(BaseModel):
    code: str

@app.get("/")
async def root():
    return {"message": "Platter Compiler Backend is running"}

@app.post("/analyzeLexical")
async def analyze_code(input_data: CodeInput):
    """Analyze Platter code and return lexemes"""
    try:
        lexer = Lexer(input_data.code)
        tokenize = lexer.tokenize()
        tokens = []
        
        for token in tokenize:
            if token is None:
                break
            tokens.append({
                "type": token.type,
                "value": token.value or '\\0',
                "line": token.line,
                "col": token.col
            })
        
        return {"tokens": tokens, "success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lexical analysis failed: {str(e)}")
    

@app.post("/analyzeSyntax")
async def analyze_syntax(input_data: CodeInput):
    """Analyze syntax of Platter code"""
    try:
        lexer = Lexer(input_data.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        parser.parse()
        
        return {"message": "No Syntax Error", "success": True}
    except SyntaxError as e:
        error_msg = str(e)
        # Try to extract line and col from error message
        # Format: "Syntax Error: ... (line X, col Y)"
        import re
        match = re.search(r'line (\d+), col (\d+)', error_msg)
        if match:
            line = int(match.group(1))
            col = int(match.group(2))
            return {
                "message": error_msg,
                "success": False,
                "error": {
                    "line": line,
                    "col": col,
                    "message": error_msg
                }
            }
        return {"message": error_msg, "success": False}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Syntax analysis failed: {str(e)}")
    

@app.post("/analyzeSemantic")
async def analyze_semantic(input_data: CodeInput):
    """Analyze semantics of Platter code"""
    try:
        # Step 1: Lexical analysis
        lexer = Lexer(input_data.code)
        tokens = lexer.tokenize()
        
        # Step 2: Syntax analysis (get AST)
        parser = Parser(tokens)
        ast = parser.parse()
        
        if not ast:
            return {
                "message": "Parsing failed - cannot perform semantic analysis",
                "success": False
            }
        
        # Step 3: Semantic analysis
        analyzer = SemanticAnalyzer(ast)
        success = analyzer.analyze()
        
        if success:
            # Get symbol tables
            ingredient_table = analyzer.get_ingredient_table()
            recipe_table = analyzer.get_recipe_table()
            
            # Format ingredient table data
            ingredients_data = []
            if ingredient_table:
                all_ingredients = ingredient_table.get_all_ingredients()
                for name, declarations in all_ingredients.items():
                    for decl in declarations:
                        ingredients_data.append({
                            "name": decl["name"],
                            "type": decl["type"],
                            "line": decl["line"],
                            "col": decl["col"],
                            "scope": decl["scope"],
                            "is_global": decl["is_global"],
                            "initialized": decl["initialized"],
                            "is_parameter": decl["is_parameter"]
                        })
            
            # Format recipe table data
            recipes_data = []
            if recipe_table:
                all_recipes = recipe_table.get_all_recipes()
                for name, recipe in all_recipes.items():
                    recipes_data.append({
                        "name": recipe["name"],
                        "line": recipe["line"],
                        "col": recipe["col"],
                        "return_type": recipe["return_type"],
                        "parameter_count": recipe["parameter_count"],
                        "is_main": recipe["is_main"]
                    })
            
            return {
                "message": "Semantic analysis completed successfully",
                "success": True,
                "ingredients": ingredients_data,
                "recipes": recipes_data,
                "warnings": analyzer.get_warnings()
            }
        else:
            errors = analyzer.get_errors()
            return {
                "message": "Semantic analysis failed",
                "success": False,
                "errors": errors
            }
            
    except SyntaxError as e:
        error_msg = str(e)
        # Try to extract line and col from error message
        import re
        match = re.search(r'line (\d+), col (\d+)', error_msg)
        if match:
            line = int(match.group(1))
            col = int(match.group(2))
            return {
                "message": error_msg,
                "success": False,
                "error": {
                    "line": line,
                    "col": col,
                    "message": error_msg
                }
            }
        return {"message": error_msg, "success": False}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Semantic analysis failed: {str(e)}")