from fastmcp import Client
from app.config import ORCHESTRATOR_MCP


async def call_orchestrator(message: str, session_id: str | None):
    """
    Call the orchestrator MCP agent using the FastMCP Client.
    
    This is the recommended approach per FastMCP docs:
    https://gofastmcp.com/clients/client.md
    """
    async with Client(ORCHESTRATOR_MCP) as client:
        result = await client.call_tool(
            "synthesize_response",
            {"query": message, "session_id": session_id},
        )
        return result
