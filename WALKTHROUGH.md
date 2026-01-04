# FastAPI Repo Chat Agent - System Walkthrough

A multi-agent system that indexes, analyzes, and answers questions about the FastAPI codebase using a knowledge graph and LLM-powered reasoning.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Agent Design Decisions](#agent-design-decisions)
3. [Setup and Installation](#setup-and-installation)
4. [Indexing Process](#indexing-process)
5. [Example Queries](#example-queries)
6. [Agent Communication](#agent-communication)
7. [Monitoring and Observability](#monitoring-and-observability)

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Client (HTTP)                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API Gateway (FastAPI)                              │
│                              Port 8000                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ /api/chat   │  │ /api/index  │  │ /api/agents │  │ /api/graph  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                          (FastMCP Client - HTTP)
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent (Container)                           │
│                    FastMCP HTTP Server · Port 8004                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ Intent Classifier │  │ Entity Extractor │  │ Response Synth.  │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
                    │                                    │
        ┌───────────┴───────────┐            ┌──────────┴──────────┐
        │ HTTP (FastMCP)        │            │ HTTP (FastMCP)     │
        ▼                       ▼            ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Graph Query   │    │ Code Analyst  │    │   Indexer     │    │    Neo4j      │
│    Agent      │    │    Agent      │    │    Agent      │    │   Database    │
│  Port 8001    │    │  Port 8002    │    │  Port 8003    │    │  (Port 7687)  │
│ (FastMCP HTTP)│    │ (FastMCP HTTP)│    │ (FastMCP HTTP)│    │               │
└───────────────┘    └───────────────┘    └───────────────┘    └───────────────┘
        │                    │                    │                    │
        └────────────────────┴────────────────────┴────────────────────┘
                                      │
                              (Neo4j Bolt Protocol)
```

### Component Breakdown

| Component | Technology | Purpose |
|-----------|------------|---------|
| API Gateway | FastAPI + Uvicorn | HTTP entry point, request routing |
| Orchestrator Agent | FastMCP 2.12.0 (HTTP) | Query routing, agent coordination, response synthesis |
| Graph Query Agent | FastMCP 2.12.0 (HTTP) + Neo4j | Execute Cypher queries, find entities |
| Code Analyst Agent | FastMCP 2.12.0 (HTTP) + OpenAI | Explain code, analyze patterns |
| Indexer Agent | FastMCP 2.12.0 (HTTP) + GitPython | Clone repos, parse AST, populate graph |
| Knowledge Graph | Neo4j 5 | Store code entities and relationships |

### Data Flow

```
User Query → API Gateway → Orchestrator Agent (HTTP)
                              │
                              ├─→ Intent Classification (LLM)
                              │   └─→ Greeting? → Instant response (no agents)
                              ├─→ Entity Extraction (LLM)
                              │
                              ├─→ Graph Query Agent (HTTP, if needed)
                              │      └─→ Neo4j: Find entities/relationships
                              │
                              ├─→ Code Analyst Agent (HTTP, if needed)
                              │      └─→ LLM: Explain code patterns
                              │
                              └─→ Response Synthesis (LLM)
                                      │
                                      ▼
                              Final Response → User
                              (Clean format: {session_id, response})
```

---

## Agent Design Decisions

### Why Multi-Agent Architecture?

1. **Separation of Concerns**: Each agent has a single responsibility
   - Indexer: Repository management and AST parsing
   - Graph Query: Database operations and entity lookup
   - Code Analyst: LLM-based code understanding
   - Orchestrator: Coordination and synthesis

2. **Scalability**: Agents can be scaled independently
3. **Maintainability**: Changes to one agent don't affect others
4. **Testability**: Each agent can be tested in isolation

### Why FastMCP?

FastMCP (Model Context Protocol) was chosen for inter-agent communication because:

- **Microservices Architecture**: Each agent runs as a separate container with HTTP transport
- **Independent Scaling**: Scale agents horizontally (e.g., multiple graph-query instances)
- **Type-Safe Tools**: Pydantic-validated tool parameters
- **Async Support**: Native async/await for non-blocking I/O
- **Standard Protocol**: MCP is an emerging standard for AI tool use
- **Version**: We use `fastmcp==2.12.0` for stable HTTP transport support

### Why Neo4j?

- **Native Graph Model**: Code relationships are naturally graph-shaped
- **Cypher Query Language**: Expressive queries for traversing relationships
- **Performance**: Efficient for relationship-heavy queries
- **Visualization**: Built-in browser for exploring data

### Entity Extraction Strategy

The orchestrator uses a two-stage approach:

```python
# Stage 1: Intent Classification
# Determines which agents to involve
{
    "intent": "lookup",           # explain, compare, lookup, patterns, general
    "agents": ["graph_query"]     # Which agents to call
}

# Stage 2: Entity Extraction  
# Extracts specific entities and query type
{
    "entity_name": "FastAPI",
    "query_type": "find_entity",  # find_entity, get_dependencies, find_related, general_query
    "relationship": null          # INHERITS_FROM, CALLS, IMPORTS, etc.
}
```

### Fallback Behavior

When graph queries return no results, the system falls back to LLM knowledge:

```python
if not has_real_data:
    # Use LLM's training knowledge about FastAPI
    prompt = "The codebase search returned no results. Please answer based on your knowledge..."
```

---

## Setup and Installation

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- OpenAI API Key

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone <repo-url>
cd fastapi-repo-chat-agent

# 2. Create environment file
cp env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Create shared.env for Docker
cat > shared.env << EOF
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL_ID=gpt-4o-mini
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
EOF

# 4. Start all services (microservices architecture)
docker compose up -d

# This starts 6 containers:
# - neo4j (database)
# - graph-query-agent (port 8001)
# - code-analyst-agent (port 8002)
# - indexer-agent (port 8003)
# - orchestrator-agent (port 8004)
# - api-gateway (port 8000)

# 5. Check status
docker compose ps

# 6. View logs
docker compose logs -f api-gateway
```

### Option 2: Local Development

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start Neo4j (Docker)
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5-community

# 4. Create .env files in each agent directory
# orchestrator-agent/.env, indexer-agent/.env, etc.

# 5. Run the API Gateway
cd api-gateway
uvicorn app.main:app --reload --port 8000
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for LLM calls | Required |
| `LLM_MODEL_ID` | Model to use | `gpt-4o-mini` |
| `NEO4J_URI` | Neo4j connection string | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `password` |
| `FASTAPI_REPO_URL` | Repository to index | FastAPI GitHub URL |
| `REPO_DIR` | Local clone directory | `/tmp/fastapi-repo` |

---

## Indexing Process

### How Indexing Works

```
┌─────────────────────────────────────────────────────────────────┐
│                      Indexing Pipeline                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Clone/Pull Repository                                       │
│     └─→ git clone https://github.com/fastapi/fastapi.git       │
│                                                                 │
│  2. Discover Python Files                                       │
│     └─→ Find all *.py files recursively                        │
│                                                                 │
│  3. Parse AST (per file)                                        │
│     └─→ ast.parse() → Extract classes, functions, imports      │
│                                                                 │
│  4. Create Graph Nodes                                          │
│     └─→ MERGE (f:File {path: $path})                           │
│     └─→ MERGE (c:Class {name: $name, file: $path})             │
│     └─→ MERGE (fn:Function {name: $name, file: $path})         │
│                                                                 │
│  5. Create Relationships                                        │
│     └─→ (File)-[:CONTAINS]->(Class)                            │
│     └─→ (File)-[:CONTAINS]->(Function)                         │
│     └─→ (Class)-[:INHERITS_FROM]->(Class)                      │
│     └─→ (Function)-[:CALLS]->(Function)                        │
│     └─→ (File)-[:IMPORTS]->(File)                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Starting the Indexer

```bash
# Via API
curl -X POST http://localhost:8000/api/index/start

# Response
{"job_id": "a88f1e2f-a7bc-45f8-9a79-445c0acae726"}

# Check status
curl http://localhost:8000/api/index/status/a88f1e2f-a7bc-45f8-9a79-445c0acae726

# Response when complete
{
    "job_id": "a88f1e2f-a7bc-45f8-9a79-445c0acae726",
    "status": "completed",
    "error": null,
    "updated_at": "2026-01-03T00:11:51.201093"
}
```

### Knowledge Graph Schema

```cypher
// Node Types
(:File {path, name})
(:Class {name, file, start, end, docstring})
(:Function {name, file, start, end, docstring, is_async})
(:Import {module, alias})

// Relationship Types
(File)-[:CONTAINS]->(Class|Function)
(Class)-[:INHERITS_FROM]->(Class)
(Function)-[:CALLS]->(Function)
(File)-[:IMPORTS]->(File|Import)
(Class|Function)-[:DECORATED_BY]->(Decorator)
```

### Sample Cypher Queries

```cypher
-- Find a class by name
MATCH (c:Class {name: 'FastAPI'})
RETURN c.name, c.file, c.start, c.end

-- Find all classes that inherit from a base class
MATCH (child:Class)-[:INHERITS_FROM]->(parent:Class {name: 'BaseModel'})
RETURN child.name, child.file

-- Find what a function calls
MATCH (f:Function {name: 'create_app'})-[:CALLS]->(called:Function)
RETURN called.name

-- Find imports in a file
MATCH (f:File {name: 'routing.py'})-[:IMPORTS]->(i)
RETURN i.module
```

---

## Example Queries

### Simple Queries (Single Agent)

**Query**: "What is the FastAPI class?"

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the FastAPI class?"}'
```

**Agent Flow**:
```
Orchestrator
  ├─→ Intent: "lookup"
  ├─→ Entity: "FastAPI", Type: "find_entity"
  ├─→ Graph Query Agent
  │     └─→ MATCH (c:Class {name: 'FastAPI'}) RETURN c
  │     └─→ Result: {file: "fastapi/applications.py", lines: 48-4669}
  └─→ Synthesis: Combines graph result with LLM knowledge
```

**Response** (excerpt):
```json
{
    "session_id": "abc-123",
    "response": "The FastAPI class is the core application class defined in fastapi/applications.py. It builds on Starlette and provides: - Automatic request/response validation using Pydantic - Dependency injection system - OpenAPI schema generation - Interactive documentation (Swagger UI, ReDoc)"
}
```

---

### Medium Queries (2-3 Agents)

**Query**: "What classes inherit from APIRouter?"

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What classes inherit from APIRouter?"}'
```

**Agent Flow**:
```
Orchestrator
  ├─→ Intent: "lookup"
  ├─→ Entity: "APIRouter", Type: "find_related", Relationship: "INHERITS_FROM"
  ├─→ Graph Query Agent
  │     └─→ find_related("APIRouter", "INHERITS_FROM")
  └─→ Synthesis: Explains APIRouter and any subclasses found
```

---

**Query**: "Compare how Path and Query parameters are implemented"

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Compare how Path and Query parameters are implemented"}'
```

**Agent Flow**:
```
Orchestrator
  ├─→ Intent: "compare"
  ├─→ Entities: "Path" (primary), "Query" (secondary)
  ├─→ Graph Query Agent (2 calls)
  │     ├─→ find_entity("Path") → params.py, param_functions.py
  │     └─→ find_entity("Query") → params.py, param_functions.py
  ├─→ Code Analyst Agent
  │     └─→ explain_implementation("Path")
  └─→ Synthesis: Detailed comparison with file locations
```

---

### Complex Queries (Multiple Agents + Synthesis)

**Query**: "Explain the complete lifecycle of a FastAPI request"

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain the complete lifecycle of a FastAPI request"}'
```

**Agent Flow**:
```
Orchestrator
  ├─→ Intent: "explain"
  ├─→ Query Type: "general_query" (no specific entity)
  ├─→ Graph Query Agent: Skipped (general query)
  ├─→ Code Analyst Agent
  │     └─→ Attempts to find relevant code patterns
  └─→ Synthesis: Comprehensive explanation using LLM knowledge
```

**Response** (excerpt):
```
The FastAPI request lifecycle:

1. Server Startup / Lifespan
   - ASGI server starts and sends lifespan events
   - Startup handlers initialize resources (DB connections, caches)

2. Connection Accept
   - ASGI server accepts TCP connection
   - Creates scope dict with request metadata

3. Middleware Stack
   - Request flows through middleware (CORS, Auth, etc.)
   - Each middleware can modify request or short-circuit

4. Routing
   - Match path + method to endpoint
   - Extract path parameters

5. Dependency Injection
   - Resolve dependencies in topological order
   - Cache results for reuse within request

6. Validation
   - Parse and validate path, query, body parameters
   - Return 422 on validation errors

7. Endpoint Execution
   - Call the path operation function
   - Await async functions

8. Response Serialization
   - Convert return value to response
   - Apply response_model validation

9. Cleanup
   - Run yield dependency cleanup
   - Execute background tasks
```

---

**Query**: "What design patterns are used in FastAPI's core and why?"

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What design patterns are used in FastAPI core and why?"}'
```

**Response** (excerpt):
```
FastAPI uses several design patterns:

1. Dependency Injection / IoC
   - Where: fastapi/dependencies/*
   - Why: Testability, loose coupling, request-scoped lifecycle

2. Decorator Pattern
   - Where: @app.get(), @app.post() in routing.py
   - Why: Declarative route registration, introspection for docs

3. Adapter/Facade
   - Where: FastAPI wrapping Starlette
   - Why: Simpler API, adds validation layer

4. Chain of Responsibility
   - Where: Middleware stack
   - Why: Composable request processing

5. Factory/Strategy
   - Where: Response classes, security schemes
   - Why: Configurable behavior
```

---

## Agent Communication

### FastMCP Protocol

Agents communicate using the Model Context Protocol (MCP) over HTTP (FastMCP 2.12.0):

```python
# API Gateway connects to orchestrator via HTTP
async with Client("http://orchestrator-agent:8004/mcp") as client:
    result = await client.call_tool("synthesize_response", {
        "query": "What is FastAPI?",
        "session_id": "abc-123"
    })

# Orchestrator connects to graph query agent via HTTP
async with Client("http://graph-query-agent:8001/mcp") as client:
    result = await client.call_tool("find_entity", {
        "name": "FastAPI"
    })
```

**Note**: Each agent runs as a separate container with its own HTTP server, enabling:
- Independent scaling (e.g., `docker compose up -d --scale graph-query-agent=3`)
- Fault isolation
- Network-based deployment

### Tool Definitions

**Orchestrator Agent Tools**:
```python
@mcp.tool
async def synthesize_response(query: str, session_id: str = None) -> dict:
    """Main entry point - orchestrates other agents and synthesizes response."""

@mcp.tool
async def analyze_query(query: str) -> dict:
    """Classify intent and determine which agents to use."""

@mcp.tool
async def route_to_agents(query: str, session_id: str = None) -> dict:
    """Route query to appropriate agents based on intent."""
```

**Graph Query Agent Tools**:
```python
@mcp.tool
async def find_entity(name: str) -> dict:
    """Find a class, function, or file by name."""

@mcp.tool
async def get_dependencies(name: str) -> dict:
    """Find what an entity depends on."""

@mcp.tool
async def get_dependents(name: str) -> dict:
    """Find what depends on this entity."""

@mcp.tool
async def find_related(name: str, relationship: str) -> dict:
    """Find entities by relationship type."""

@mcp.tool
async def execute_query(query: str) -> dict:
    """Execute raw Cypher query."""
```

**Indexer Agent Tools**:
```python
@mcp.tool
async def index_repo() -> dict:
    """Index the full FastAPI repository."""

@mcp.tool
async def index_single_file(path: str) -> dict:
    """Index a specific Python file."""

@mcp.tool
async def index_status() -> dict:
    """Get indexer health status."""
```

### Response Synthesis Pipeline

```python
async def synthesize_response(query: str, session_id: str = None):
    # 1. Classify intent
    analysis = await route(query)  # Uses LLM (or quick check for greetings)
    
    # 2. Handle greetings instantly (no agent calls)
    if analysis.get("intent") == "greeting" or not analysis.get("agents"):
        return {
            "session_id": session_id,
            "response": get_greeting_response(query)
        }
    
    # 3. Extract entities
    extracted = await extract_entities(query)  # Uses LLM
    
    # 4. Call appropriate agents
    agent_outputs = {}
    
    if "graph_query" in analysis["agents"]:
        if extracted["query_type"] == "find_entity":
            agent_outputs["graph_query"] = await find_entity(extracted["entity_name"])
        elif extracted["query_type"] == "get_dependencies":
            agent_outputs["graph_query"] = await get_dependencies(extracted["entity_name"])
        # ... other query types
    
    if "code_analyst" in analysis["agents"]:
        agent_outputs["code_analyst"] = await explain(extracted["entity_name"] or query)
    
    # 5. Synthesize final response
    final_response = await synthesize(query, agent_outputs)  # Uses LLM
    
    # 6. Store in conversation memory
    memory.add_turn(session_id, query, final_response)
    
    # 7. Return clean response format
    return {"session_id": session_id, "response": final_response}
```

---

## Monitoring and Observability

### Health Checks

```bash
# Check all agents
curl http://localhost:8000/api/agents/health

# Response
{
    "orchestrator": true,
    "indexer": true,
    "graph": true,
    "code_analyst": true
}
```

### Docker Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api-gateway
docker compose logs -f orchestrator-agent

# Last N lines
docker compose logs --tail=100 api-gateway

# Scale agents for load balancing
docker compose up -d --scale graph-query-agent=3
```

### Neo4j Browser

Access the Neo4j browser at `http://localhost:7474` for:
- Query execution and visualization
- Database statistics
- Schema exploration

```cypher
-- Count all nodes
MATCH (n) RETURN labels(n), count(n)

-- Count all relationships
MATCH ()-[r]->() RETURN type(r), count(r)

-- View schema
CALL db.schema.visualization()
```

### API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send a query to the multi-agent system |
| `/api/index/start` | POST | Start indexing the repository |
| `/api/index/status/{job_id}` | GET | Check indexing job status |
| `/api/agents/health` | GET | Check health of all agents |
| `/api/graph/statistics` | GET | Get graph database statistics |

### Debugging Tips

1. **Check agent subprocess output**:
   ```bash
   docker logs fastapi-repo-api 2>&1 | grep -E "(ERROR|Exception|Traceback)"
   ```

2. **Test individual agents**:
   ```bash
   docker exec -it fastapi-repo-api python3 -c "
   import asyncio
   from fastmcp import Client
   
   async def test():
       async with Client('/app/indexer-agent/indexer_mcp.py') as client:
           tools = await client.list_tools()
           print([t.name for t in tools])
   
   asyncio.run(test())
   "
   ```

3. **Query Neo4j directly**:
   ```bash
   docker exec -it fastapi-repo-neo4j cypher-shell -u neo4j -p password \
     "MATCH (n) RETURN labels(n), count(n)"
   ```

4. **Check environment variables**:
   ```bash
   docker exec fastapi-repo-api env | grep -E "(NEO4J|OPENAI|LLM)"
   ```

---

## Future Enhancements

- [ ] Streaming responses for long answers
- [ ] Vector embeddings for semantic code search
- [ ] Support for multiple repositories
- [ ] Web UI for interactive exploration
- [ ] Caching layer for frequently asked questions
- [ ] More relationship types (type annotations, decorators)
- [ ] Code snippet extraction and highlighting

