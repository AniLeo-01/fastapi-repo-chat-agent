from app.clients.base import call_mcp_tool
from app.config import CODE_AGENT_PATH


async def analyze_function(name: str) -> dict:
    """Analyze a function's structure and logic."""
    return await call_mcp_tool(
        agent_path=CODE_AGENT_PATH,
        tool="analyze_function",
        payload={"name": name},
    )


async def explain(name: str) -> dict:
    """Get an LLM explanation of a code entity."""
    return await call_mcp_tool(
        agent_path=CODE_AGENT_PATH,
        tool="explain_implementation",
        payload={"name": name},
    )
