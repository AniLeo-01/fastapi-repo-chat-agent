FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install fastmcp neo4j pydantic-settings

CMD ["python", "apps/graph-query-agent/graph_query_mcp.py"]
