from app.llm import classify_intent

async def analyze_intent(query: str) -> dict:
    """Classify query intent and determine candidate agents."""
    return await classify_intent(query)
