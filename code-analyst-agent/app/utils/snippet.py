# apps/code-analyst-agent/app/utils/snippet.py
import aiofiles
from app.config import settings

async def get_code_snippet(file_path: str, start: int, end: int, context: int = 3):
    """
    Extract code lines with context around the target block.
    """
    full_path = file_path if file_path.startswith("/") else f"{settings.REPO_ROOT}/{file_path}"

    async with aiofiles.open(full_path, "r") as f:
        lines = await f.readlines()

    start_idx = max(0, start - context)
    end_idx = min(len(lines), end + context)

    return "".join(lines[start_idx:end_idx])
