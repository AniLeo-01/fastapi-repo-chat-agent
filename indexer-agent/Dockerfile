FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install fastmcp neo4j gitpython pydantic-settings

CMD ["python", "apps/indexer-agent/indexer_mcp.py"]
