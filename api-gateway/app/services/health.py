from fastmcp import Client


async def check_agent(path: str) -> bool:
    """
    Check if an MCP agent is healthy by attempting to connect.
    
    Uses FastMCP Client for proper connection testing:
    https://gofastmcp.com/clients/client.md
    """
    try:
        async with Client(path) as client:
            # List tools to verify the server is responding
            await client.list_tools()
        return True
    except Exception:
        return False
