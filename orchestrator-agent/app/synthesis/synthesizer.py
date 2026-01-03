from typing import Dict, Any
from app.llm import synthesize_response

async def synthesize(query: str, agent_outputs: Dict[str, Any]) -> Any:
    """Synthesize agent outputs into a final response."""
    return await synthesize_response(query, agent_outputs)
