import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve paths relative to this file's location
AGENT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

# In Docker, use shared.env mounted at /app/shared.env
DOCKER_ENV_FILE = Path("/app/shared.env")
if DOCKER_ENV_FILE.exists():
    ENV_FILE = DOCKER_ENV_FILE

# MCP agent paths (absolute paths for subprocess spawning)
CODE_AGENT_PATH = str(AGENT_ROOT / "code-analyst-agent" / "code_analyst_mcp.py")
GRAPH_AGENT_PATH = str(AGENT_ROOT / "graph-query-agent" / "graph_query_mcp.py")


class Settings(BaseSettings):
    OPENAI_API_KEY: str | None = None
    DEFAULT_TIMEOUT: int = 20
    LLM_MODEL_ID: str = "gpt-5-mini"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
