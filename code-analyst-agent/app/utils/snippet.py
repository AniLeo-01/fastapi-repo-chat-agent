# apps/code-analyst-agent/app/utils/snippet.py
import aiofiles
import os
from pathlib import Path
from app.config import settings

async def get_code_snippet(file_path: str, start: int, end: int, context: int = 3):
    """
    Extract code lines with context around the target block.
    """
    if file_path is None:
        raise ValueError("file_path cannot be None")
    full_path = file_path if file_path.startswith("/") else f"{settings.REPO_ROOT}/{file_path}"

    # Check if file exists before trying to open
    if not os.path.exists(full_path):
        # Provide helpful error message
        repo_root_exists = os.path.exists(settings.REPO_ROOT)
        raise FileNotFoundError(
            f"File not found: {full_path}\n"
            f"REPO_ROOT: {settings.REPO_ROOT} (exists: {repo_root_exists})\n"
            f"Original path: {file_path}"
        )

    async with aiofiles.open(full_path, "r") as f:
        lines = await f.readlines()

    start_idx = max(0, start - context)
    end_idx = min(len(lines), end + context)

    return "".join(lines[start_idx:end_idx])
