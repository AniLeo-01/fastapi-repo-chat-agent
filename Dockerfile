# Multi-stage build for FastAPI Repo Chat Agent
# This container includes the API Gateway and all MCP agents
# since agents are spawned as subprocesses via fastmcp.Client

FROM python:3.11-slim AS base

# Install git for cloning repositories during indexing
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn

# Copy all source code
COPY api-gateway/ ./api-gateway/
COPY orchestrator-agent/ ./orchestrator-agent/
COPY indexer-agent/ ./indexer-agent/
COPY graph-query-agent/ ./graph-query-agent/
COPY code-analyst-agent/ ./code-analyst-agent/

# Set PYTHONPATH to include all agent directories
ENV PYTHONPATH=/app

# Expose API Gateway port
EXPOSE 8000

# Run the API Gateway
WORKDIR /app/api-gateway
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

