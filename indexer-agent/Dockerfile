# Dockerfile for Indexer Agent
# Runs as SSE server for microservices architecture

FROM python:3.11-slim

WORKDIR /app

# Install git for cloning repositories
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastmcp==2.12.0 \
    neo4j \
    gitpython \
    pydantic-settings \
    aiofiles

# Copy agent code
COPY . /app

# Default to HTTP transport for microservices
ENV MCP_TRANSPORT=http
ENV MCP_PORT=8003

EXPOSE 8003

# Run the MCP server
CMD ["python", "indexer_mcp.py"]
