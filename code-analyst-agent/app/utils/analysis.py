# apps/code-analyst-agent/app/utils/analysis.py
import ast

def analyze_function_logic(code: str):
    """
    Inspect AST to extract structural insights:
    - branches / loops / returns / complexity hints
    """
    tree = ast.parse(code)
    
    info = {
        "has_loops": any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(tree)),
        "has_conditionals": any(isinstance(n, ast.If) for n in ast.walk(tree)),
        "returns_count": sum(isinstance(n, ast.Return) for n in ast.walk(tree)),
        "calls": list({n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)})
    }

    return info
