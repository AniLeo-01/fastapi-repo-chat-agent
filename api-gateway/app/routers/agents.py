import asyncio
from fastapi import APIRouter
from app.services.health import check_agent
from app.config import ORCHESTRATOR_MCP, INDEXER_MCP, GRAPH_QUERY_MCP, CODE_ANALYST_MCP

router = APIRouter()


@router.get("/api/agents/health")
async def agents_health():
    orchestrator, indexer, graph, code_analyst = await asyncio.gather(
        check_agent(ORCHESTRATOR_MCP),
        check_agent(INDEXER_MCP),
        check_agent(GRAPH_QUERY_MCP),
        check_agent(CODE_ANALYST_MCP),
    )
    return {
        "orchestrator": orchestrator,
        "indexer": indexer,
        "graph": graph,
        "code_analyst": code_analyst,
    }
