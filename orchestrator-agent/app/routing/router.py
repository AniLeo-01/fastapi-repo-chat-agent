from app.routing.intent import analyze_intent

async def route(query: str) -> dict:
    result = await analyze_intent(query)
    return {
        "query": query,
        "intent": result["intent"],
        "agents": result["agents"],
    }
