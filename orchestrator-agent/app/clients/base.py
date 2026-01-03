from fastmcp import Client
from app.clients.errors import AgentCallError


async def call_mcp_tool(agent_path: str, tool: str, payload: dict, timeout: int = 20) -> dict:
    """
    Call an MCP tool using the FastMCP Client.
    
    This is the recommended approach per FastMCP docs:
    https://gofastmcp.com/clients/client.md
    """
    try:
        async with Client(agent_path) as client:
            result = await client.call_tool(tool, payload)
            # Extract the data from the result
            if hasattr(result, 'data'):
                return result.data
            return result
    except Exception as e:
        raise AgentCallError(agent_path, str(e))
