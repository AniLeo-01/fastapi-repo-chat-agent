from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root is one level up from api-gateway
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# MCP agent paths (not configurable via env vars)
ORCHESTRATOR_MCP = str(PROJECT_ROOT / "orchestrator-agent" / "orchestrator_mcp.py")
INDEXER_MCP = str(PROJECT_ROOT / "indexer-agent" / "indexer_mcp.py")
GRAPH_QUERY_MCP = str(PROJECT_ROOT / "graph-query-agent" / "graph_query_mcp.py")
CODE_ANALYST_MCP = str(PROJECT_ROOT / "code-analyst-agent" / "code_analyst_mcp.py")

# Resolve .env path relative to this file's location
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
