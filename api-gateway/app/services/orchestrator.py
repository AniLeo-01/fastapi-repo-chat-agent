import asyncio
import json
from fastmcp import Client
from app.config import ORCHESTRATOR_MCP


def extract_response(result) -> dict:
    """Extract clean response from MCP tool result."""
    # Handle different result structures
    if hasattr(result, 'data') and result.data:
        data = result.data
    elif hasattr(result, 'structured_content') and result.structured_content:
        data = result.structured_content
    elif isinstance(result, dict):
        data = result.get('data') or result.get('structured_content') or result
    else:
        data = result
    
    # If data is a dict with session_id and response, return it clean
    if isinstance(data, dict) and 'response' in data:
        return {
            "session_id": data.get('session_id'),
            "response": data.get('response')
        }
    
    # Fallback
    return {"session_id": None, "response": str(data)}


async def call_orchestrator(message: str, session_id: str | None):
    """
    Call the orchestrator MCP agent using the FastMCP Client.
    
    This is the recommended approach per FastMCP docs:
    https://gofastmcp.com/clients/client.md
    """
    try:
        async with Client(ORCHESTRATOR_MCP) as client:
            # Add timeout to prevent hanging
            result = await asyncio.wait_for(
                client.call_tool(
                    "synthesize_response",
                    {"query": message, "session_id": session_id},
                ),
                timeout=120.0  # 2 minute timeout
            )
            return extract_response(result)
    except asyncio.TimeoutError:
        return {"error": "Request timed out after 120 seconds", "session_id": session_id}
    except Exception as e:
        return {"error": str(e), "session_id": session_id}
