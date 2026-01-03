import uuid
import asyncio
from fastmcp import Client
from app.state import state, IndexJobStatus, IndexJob
from app.config import INDEXER_MCP


async def start_indexing(path: str = None, incremental: bool = False):
    """Start an indexing job in the background."""
    job_id = str(uuid.uuid4())
    job = IndexJob(job_id, path or "default", incremental)
    state.index_jobs[job_id] = job
    job.update(IndexJobStatus.RUNNING)

    # Start indexing in background (non-blocking)
    asyncio.create_task(_run_indexer(job_id))

    return job_id


async def _run_indexer(job_id: str):
    """
    Run the indexer MCP agent using the FastMCP Client.
    
    The index_repo tool uses the configured FASTAPI_REPO_URL from settings,
    so no parameters are needed.
    """
    job = state.index_jobs.get(job_id)
    if not job:
        return

    try:
        async with Client(INDEXER_MCP) as client:
            # index_repo takes no parameters - uses configured repo URL
            result = await client.call_tool("index_repo", {})
            job.update(IndexJobStatus.COMPLETED)
    except Exception as e:
        job.update(IndexJobStatus.FAILED, error=str(e))


async def get_job_status(job_id: str):
    """Get the status of an indexing job."""
    job = state.index_jobs.get(job_id)
    if not job:
        return {"status": "unknown"}

    return {
        "job_id": job.job_id,
        "status": job.status,
        "error": job.error,
        "updated_at": job.updated_at,
    }
