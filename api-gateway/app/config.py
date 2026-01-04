import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root is one level up from api-gateway
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Resolve .env path relative to this file's location
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

# In Docker, use shared.env if available
DOCKER_ENV_FILE = Path("/app/shared.env")
if DOCKER_ENV_FILE.exists():
    ENV_FILE = DOCKER_ENV_FILE


class Settings(BaseSettings):
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Agent URLs (for microservices mode) or None (for subprocess mode)
    ORCHESTRATOR_URL: str | None = None
    INDEXER_URL: str | None = None
    GRAPH_QUERY_URL: str | None = None
    CODE_ANALYST_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


# Determine agent connection strings
# Use URLs if provided (microservices), otherwise use file paths (subprocess)
def get_orchestrator_path() -> str:
    if settings.ORCHESTRATOR_URL:
        return settings.ORCHESTRATOR_URL
    return str(PROJECT_ROOT / "orchestrator-agent" / "orchestrator_mcp.py")

def get_indexer_path() -> str:
    if settings.INDEXER_URL:
        return settings.INDEXER_URL
    return str(PROJECT_ROOT / "indexer-agent" / "indexer_mcp.py")

def get_graph_query_path() -> str:
    if settings.GRAPH_QUERY_URL:
        return settings.GRAPH_QUERY_URL
    return str(PROJECT_ROOT / "graph-query-agent" / "graph_query_mcp.py")

def get_code_analyst_path() -> str:
    if settings.CODE_ANALYST_URL:
        return settings.CODE_ANALYST_URL
    return str(PROJECT_ROOT / "code-analyst-agent" / "code_analyst_mcp.py")

ORCHESTRATOR_MCP = get_orchestrator_path()
INDEXER_MCP = get_indexer_path()
GRAPH_QUERY_MCP = get_graph_query_path()
CODE_ANALYST_MCP = get_code_analyst_path()
