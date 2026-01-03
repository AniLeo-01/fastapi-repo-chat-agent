# apps/indexer-agent/app/indexing/repository_manager.py
import asyncio
import shutil
from functools import partial
from git import Repo, InvalidGitRepositoryError
from pathlib import Path
from ..config import settings
from ..indexing.file_indexer import index_file

def _update_repo_sync():
    """Synchronous git operations (run in executor)."""
    repo_dir = Path(settings.REPO_DIR)
    git_dir = repo_dir / ".git"
    
    if git_dir.exists():
        # Valid git repo exists, pull latest
        try:
            Repo(settings.REPO_DIR).remotes.origin.pull()
        except Exception:
            # If pull fails, re-clone
            shutil.rmtree(repo_dir, ignore_errors=True)
            Repo.clone_from(settings.FASTAPI_REPO_URL, settings.REPO_DIR)
    else:
        # No git repo, remove any existing files and clone fresh
        if repo_dir.exists():
            shutil.rmtree(repo_dir, ignore_errors=True)
        Repo.clone_from(settings.FASTAPI_REPO_URL, settings.REPO_DIR)

async def update_repo():
    """Run git operations in thread pool to avoid blocking."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _update_repo_sync)

async def index_repository():
    await update_repo()
    py_files = list(Path(settings.REPO_DIR).rglob("*.py"))
    
    # Index files sequentially to avoid Neo4j deadlocks
    # Batch processing with limited concurrency
    indexed = 0
    batch_size = 3  # Small batches to avoid deadlocks
    
    for i in range(0, len(py_files), batch_size):
        batch = py_files[i:i + batch_size]
        try:
            await asyncio.gather(*[index_file(str(f)) for f in batch])
            indexed += len(batch)
        except Exception as e:
            # Log but continue with next batch
            print(f"Batch indexing error: {e}")
            # Try indexing files one by one in failed batch
            for f in batch:
                try:
                    await index_file(str(f))
                    indexed += 1
                except Exception:
                    pass  # Skip failed files
    
    return {"indexed_files": indexed}
