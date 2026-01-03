from fastapi import APIRouter
from typing import Optional
from app.schemas import IndexRequest
from app.services.indexer import start_indexing, get_job_status

router = APIRouter()

@router.post("/api/index/start")
async def start_index():
    """Start indexing using the default configured repository."""
    job_id = await start_indexing()
    return {"job_id": job_id}

@router.post("/api/index")
async def index_repo(req: Optional[IndexRequest] = None):
    """Start indexing with optional custom path."""
    path = req.path if req else None
    incremental = req.incremental if req else False
    job_id = await start_indexing(path, incremental)
    return {"job_id": job_id}

@router.get("/api/index/status/{job_id}")
async def index_status(job_id: str):
    return await get_job_status(job_id)
