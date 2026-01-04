import logging
import sys
from fastmcp import Client
from app.clients.errors import AgentCallError

logger = logging.getLogger(__name__)
# Ensure logger outputs to stdout
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


async def call_mcp_tool(agent_path: str, tool: str, payload: dict, timeout: int = 20) -> dict:
    """
    Call an MCP tool using the FastMCP Client.
    
    This is the recommended approach per FastMCP docs:
    https://gofastmcp.com/clients/client.md
    """
    call_msg = f"[MCP_CALL] Calling {agent_path} -> {tool} with payload: {payload}"
    logger.info(call_msg)
    print(call_msg, flush=True)
    try:
        async with Client(agent_path) as client:
            result = await client.call_tool(tool, payload)
            # Extract the data from the result
            success_msg = f"[MCP_CALL] {agent_path} -> {tool} completed successfully"
            if hasattr(result, 'data'):
                logger.info(success_msg)
                print(success_msg, flush=True)
                return result.data
            logger.info(success_msg)
            print(success_msg, flush=True)
            return result
    except Exception as e:
        error_msg = f"[MCP_CALL] Error calling {agent_path} -> {tool}: {str(e)}"
        logger.error(error_msg)
        print(error_msg, flush=True)
        raise AgentCallError(agent_path, str(e))
