from fastapi import APIRouter
from app.services.graph import get_graph_statistics

router = APIRouter()

@router.get("/api/graph/statistics")
async def graph_stats():
    return await get_graph_statistics()
