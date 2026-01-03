# apps/code-analyst-agent/code_analyst_mcp.py

from fastmcp import FastMCP
from app.utils.snippet import get_code_snippet
from app.utils.analysis import analyze_function_logic
from app.utils.patterns import detect_patterns
from app.utils.llm import explain_code, compare_code
from app.models import (
    FunctionAnalysis,
    ClassPatternAnalysis,
    CodeSnippetResponse,
    ImplementationExplanation,
    ImplementationComparison,
)
from app.graph.driver import run_query

mcp = FastMCP(name="Code Analyst Agent")

async def resolve_entity(name: str):
    result = await run_query("""
        MATCH (n {name:$name})
        RETURN n.file AS file, n.start AS start, n.end AS end
    """, {"name": name})
    
    if not result:
        return None
    return result[0]["file"], result[0]["start"], result[0]["end"]

# -----------------------------------------------------------
# 1) Analyze Function
# -----------------------------------------------------------
@mcp.tool
async def analyze_function(name: str) -> dict:
    resolved = await resolve_entity(name)
    if not resolved:
        return {"error": f"Entity '{name}' not found"}
    file, start, end = resolved
    code = await get_code_snippet(file, start, end)
    structure = analyze_function_logic(code)
    return FunctionAnalysis(file_path=file, code=code, structure=structure).dict()

# -----------------------------------------------------------
# 2) Analyze Class
# -----------------------------------------------------------
@mcp.tool
async def analyze_class(name: str) -> dict:
    resolved = await resolve_entity(name)
    if not resolved:
        return {"error": f"Entity '{name}' not found"}
    file, start, end = resolved
    code = await get_code_snippet(file, start, end)
    patterns = detect_patterns(code)
    return ClassPatternAnalysis(file_path=file, code=code, patterns_detected=patterns).dict()

# -----------------------------------------------------------
# 3) Detect Patterns
# -----------------------------------------------------------
@mcp.tool
async def find_patterns(name: str) -> dict:
    resolved = await resolve_entity(name)
    if not resolved:
        return {"error": f"Entity '{name}' not found"}
    file, start, end = resolved
    code = await get_code_snippet(file, start, end)
    return {"patterns": detect_patterns(code)}

# -----------------------------------------------------------
# 4) Get Snippet
# -----------------------------------------------------------
@mcp.tool
async def get_code_snippet_tool(name: str, context: int = 3) -> dict:
    resolved = await resolve_entity(name)
    if not resolved:
        return {"error": f"Entity '{name}' not found"}
    file, start, end = resolved
    snippet = await get_code_snippet(file, start, end, context)
    return CodeSnippetResponse(file_path=file, snippet=snippet, start=start, end=end, context=context).dict()

# -----------------------------------------------------------
# 5) Explain Code (LLM)
# -----------------------------------------------------------
@mcp.tool
async def explain_implementation(name: str) -> dict:
    resolved = await resolve_entity(name)
    if not resolved:
        return {"error": f"Entity '{name}' not found"}
    file, start, end = resolved
    code = await get_code_snippet(file, start, end)
    
    try:
        explanation = await explain_code(code)
        return ImplementationExplanation(file_path=file, explanation=explanation, code=code).dict()
    except Exception as e:
        return ImplementationExplanation(file_path=file, code=code, error=str(e)).dict()

# -----------------------------------------------------------
# 6) Compare Implementations
# -----------------------------------------------------------
@mcp.tool
async def compare_implementations(name_a: str, name_b: str) -> dict:
    resolved_a = await resolve_entity(name_a)
    resolved_b = await resolve_entity(name_b)
    
    if not resolved_a:
        return {"error": f"Entity '{name_a}' not found"}
    if not resolved_b:
        return {"error": f"Entity '{name_b}' not found"}

    a_file, a_start, a_end = resolved_a
    b_file, b_start, b_end = resolved_b

    code_a = await get_code_snippet(a_file, a_start, a_end)
    code_b = await get_code_snippet(b_file, b_start, b_end)

    try:
        comparison = await compare_code(code_a, code_b)
        return ImplementationComparison(implementation_a=code_a, implementation_b=code_b, comparison=comparison).dict()

    except Exception as e:
        return ImplementationComparison(implementation_a=code_a, implementation_b=code_b, error=str(e)).dict()

# -----------------------------------------------------------
# Start Server
# -----------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
