from typing import Any


from fastmcp import FastMCP
from app.graph.query import (
    find_entity_node,
    get_dependencies_for,
    get_dependents_for,
    trace_import_chain,
    find_related_entities,
    execute_safe_cypher,
)

mcp = FastMCP[Any](name="Graph Query Agent")

@mcp.tool
async def find_entity(name: str) -> dict:
    """Locate a class, function, module, or file by name."""
    return {"results": await find_entity_node(name)}

@mcp.tool
async def get_dependencies(name: str) -> dict:
    """Find what an entity depends on (CALL graph)."""
    return {"results": await get_dependencies_for(name)}

@mcp.tool
async def get_dependents(name: str) -> dict:
    """Find who depends on this entity."""
    return {"results": await get_dependents_for(name)}

@mcp.tool
async def trace_imports(path: str) -> dict:
    """Follow IMPORTS chain for a module/file."""
    return {"results": await trace_import_chain(path)}

@mcp.tool
async def find_related(name: str, relationship: str) -> dict:
    """Search by relationship: CONTAINS, IMPORTS, CALLS, INHERITS_FROM, DECORATED_BY."""
    return {"results": await find_related_entities(name, relationship)}

@mcp.tool
async def execute_query(query: str) -> dict:
    """Run read-only Cypher queries."""
    return {"results": await execute_safe_cypher(query)}

if __name__ == "__main__":
    mcp.run()
