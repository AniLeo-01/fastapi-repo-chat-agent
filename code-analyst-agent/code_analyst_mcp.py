# apps/code-analyst-agent/code_analyst_mcp.py
import os

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
    # Search across all node types (Class, Function, Method, etc.) that have the required properties
    result = await run_query("""
        MATCH (n {name:$name})
        WHERE n.file IS NOT NULL AND n.start IS NOT NULL AND n.end IS NOT NULL
        RETURN n.file AS file, n.start AS start, n.end AS end
        LIMIT 1
    """, {"name": name})
    
    if not result:
        return None
    
    file = result[0].get("file")
    start = result[0].get("start")
    end = result[0].get("end")
    
    # Validate that we have all required fields (should be guaranteed by WHERE clause, but double-check)
    if file is None or start is None or end is None:
        return None
    
    return file, start, end

# -----------------------------------------------------------
# 1) Analyze Function
# -----------------------------------------------------------
@mcp.tool
async def analyze_function(name: str) -> dict:
    resolved = await resolve_entity(name)
    if not resolved:
        return {"error": f"Entity '{name}' not found in graph database. The entity may not be indexed yet."}
    file, start, end = resolved
    try:
        code = await get_code_snippet(file, start, end)
    except (ValueError, FileNotFoundError) as e:
        return {"error": f"Could not retrieve code for entity '{name}': {str(e)}"}
    structure = analyze_function_logic(code)
    return FunctionAnalysis(file_path=file, code=code, structure=structure).dict()

# -----------------------------------------------------------
# 2) Analyze Class
# -----------------------------------------------------------
@mcp.tool
async def analyze_class(name: str) -> dict:
    resolved = await resolve_entity(name)
    if not resolved:
        return {"error": f"Entity '{name}' not found in graph database. The entity may not be indexed yet."}
    file, start, end = resolved
    try:
        code = await get_code_snippet(file, start, end)
    except (ValueError, FileNotFoundError) as e:
        return {"error": f"Could not retrieve code for entity '{name}': {str(e)}"}
    patterns = detect_patterns(code)
    return ClassPatternAnalysis(file_path=file, code=code, patterns_detected=patterns).dict()

# -----------------------------------------------------------
# 3) Detect Patterns
# -----------------------------------------------------------
@mcp.tool
async def find_patterns(name: str) -> dict:
    resolved = await resolve_entity(name)
    if not resolved:
        return {"error": f"Entity '{name}' not found in graph database. The entity may not be indexed yet."}
    file, start, end = resolved
    try:
        code = await get_code_snippet(file, start, end)
    except (ValueError, FileNotFoundError) as e:
        return {"error": f"Could not retrieve code for entity '{name}': {str(e)}"}
    return {"patterns": detect_patterns(code)}

# -----------------------------------------------------------
# 4) Get Snippet
# -----------------------------------------------------------
@mcp.tool
async def get_code_snippet_tool(name: str, context: int = 3) -> dict:
    resolved = await resolve_entity(name)
    if not resolved:
        return {"error": f"Entity '{name}' not found in graph database. The entity may not be indexed yet."}
    file, start, end = resolved
    try:
        snippet = await get_code_snippet(file, start, end, context)
    except (ValueError, FileNotFoundError) as e:
        return {"error": f"Could not retrieve code for entity '{name}': {str(e)}"}
    return CodeSnippetResponse(file_path=file, snippet=snippet, start=start, end=end, context=context).dict()

# -----------------------------------------------------------
# 5) Explain Code (LLM)
# -----------------------------------------------------------
@mcp.tool
async def explain_implementation(name: str) -> dict:
    resolved = await resolve_entity(name)
    if not resolved:
        return {"error": f"Entity '{name}' not found in graph database. The entity may not be indexed yet."}
    file, start, end = resolved
    
    try:
        code = await get_code_snippet(file, start, end)
    except (ValueError, FileNotFoundError) as e:
        return {"error": f"Could not retrieve code for entity '{name}': {str(e)}"}
    
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
        return {"error": f"Entity '{name_a}' not found in graph database. The entity may not be indexed yet."}
    if not resolved_b:
        return {"error": f"Entity '{name_b}' not found in graph database. The entity may not be indexed yet."}

    a_file, a_start, a_end = resolved_a
    b_file, b_start, b_end = resolved_b

    try:
        code_a = await get_code_snippet(a_file, a_start, a_end)
    except (ValueError, FileNotFoundError) as e:
        return {"error": f"Could not retrieve code for entity '{name_a}': {str(e)}"}
    
    try:
        code_b = await get_code_snippet(b_file, b_start, b_end)
    except (ValueError, FileNotFoundError) as e:
        return {"error": f"Could not retrieve code for entity '{name_b}': {str(e)}"}

    try:
        comparison = await compare_code(code_a, code_b)
        return ImplementationComparison(implementation_a=code_a, implementation_b=code_b, comparison=comparison).dict()

    except Exception as e:
        return ImplementationComparison(implementation_a=code_a, implementation_b=code_b, error=str(e)).dict()

# -----------------------------------------------------------
# Start Server
# -----------------------------------------------------------
if __name__ == "__main__":
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "http":
        port = int(os.environ.get("MCP_PORT", "8002"))
        mcp.run(transport="http", host="0.0.0.0", port=port)
    else:
        mcp.run()  # Default stdio for subprocess mode
