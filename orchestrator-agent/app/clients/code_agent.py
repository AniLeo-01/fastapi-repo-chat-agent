import logging
import sys
from app.clients.base import call_mcp_tool
from app.config import CODE_AGENT_PATH

logger = logging.getLogger(__name__)
# Ensure logger outputs to stdout
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


async def analyze_function(name: str) -> dict:
    """Analyze a function's structure and logic."""
    logger.info(f"[CODE_AGENT] Calling analyze_function for: '{name}'")
    result = await call_mcp_tool(
        agent_path=CODE_AGENT_PATH,
        tool="analyze_function",
        payload={"name": name},
    )
    logger.info(f"[CODE_AGENT] analyze_function completed for: '{name}'")
    return result


async def explain(name: str) -> dict:
    """Get an LLM explanation of a code entity."""
    call_msg = f"[CODE_AGENT] Calling explain_implementation for: '{name}'"
    logger.info(call_msg)
    print(call_msg, flush=True)
    result = await call_mcp_tool(
        agent_path=CODE_AGENT_PATH,
        tool="explain_implementation",
        payload={"name": name},
    )
    complete_msg = f"[CODE_AGENT] explain_implementation completed for: '{name}'"
    logger.info(complete_msg)
    print(complete_msg, flush=True)
    return result
