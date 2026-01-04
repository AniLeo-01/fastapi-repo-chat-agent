# Dockerfile for Graph Query Agent
# Runs as SSE server for microservices architecture

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastmcp==2.12.0 \
    neo4j \
    pydantic-settings

# Copy agent code
COPY . /app

# Default to HTTP transport for microservices
ENV MCP_TRANSPORT=http
ENV MCP_PORT=8001

EXPOSE 8001

# Run the MCP server
CMD ["python", "graph_query_mcp.py"]
