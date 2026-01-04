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


class Settings(BaseSettings):
    OPENAI_API_KEY: str | None = None
    DEFAULT_TIMEOUT: int = 20
    LLM_MODEL_ID: str = "gpt-4o-mini"
    
    # Agent URLs (for microservices mode) or paths (for subprocess mode)
    # URLs take precedence if set
    CODE_AGENT_URL: str | None = None
    GRAPH_AGENT_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Determine agent connection strings
# Use URLs if provided (microservices), otherwise use file paths (subprocess)
def get_code_agent_path() -> str:
    if settings.CODE_AGENT_URL:
        return settings.CODE_AGENT_URL
    return str(AGENT_ROOT / "code-analyst-agent" / "code_analyst_mcp.py")

def get_graph_agent_path() -> str:
    if settings.GRAPH_AGENT_URL:
        return settings.GRAPH_AGENT_URL
    return str(AGENT_ROOT / "graph-query-agent" / "graph_query_mcp.py")

CODE_AGENT_PATH = get_code_agent_path()
GRAPH_AGENT_PATH = get_graph_agent_path()
