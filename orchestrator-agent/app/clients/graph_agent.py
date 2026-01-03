from app.clients.base import call_mcp_tool
from app.config import GRAPH_AGENT_PATH


async def query_graph(query: str) -> dict:
    """Run a Cypher query against the graph database."""
    return await call_mcp_tool(
        agent_path=GRAPH_AGENT_PATH,
        tool="execute_query",
        payload={"query": query},
    )


async def find_entity(name: str) -> dict:
    """Find an entity (class, function, module) by name."""
    return await call_mcp_tool(
        agent_path=GRAPH_AGENT_PATH,
        tool="find_entity",
        payload={"name": name},
    )


async def get_dependencies(name: str) -> dict:
    """Find what an entity depends on (CALL graph)."""
    return await call_mcp_tool(
        agent_path=GRAPH_AGENT_PATH,
        tool="get_dependencies",
        payload={"name": name},
    )


async def get_dependents(name: str) -> dict:
    """Find who depends on this entity."""
    return await call_mcp_tool(
        agent_path=GRAPH_AGENT_PATH,
        tool="get_dependents",
        payload={"name": name},
    )


async def trace_imports(path: str) -> dict:
    """Follow IMPORTS chain for a module/file."""
    return await call_mcp_tool(
        agent_path=GRAPH_AGENT_PATH,
        tool="trace_imports",
        payload={"path": path},
    )


async def find_related(name: str, relationship: str) -> dict:
    """Search by relationship: CONTAINS, IMPORTS, CALLS, INHERITS_FROM, DECORATED_BY."""
    return await call_mcp_tool(
        agent_path=GRAPH_AGENT_PATH,
        tool="find_related",
        payload={"name": name, "relationship": relationship},
    )
