# FastAPI Repo Chat Agent

A multi-agent system that indexes, analyzes, and answers questions about the FastAPI codebase using a knowledge graph and LLM-powered reasoning.

## Features

- 🤖 **Microservices Architecture**: Each agent runs as a separate container for independent scaling
- 🔍 **Knowledge Graph**: Neo4j-powered code entity and relationship storage
- 💬 **Natural Language Queries**: Ask questions about FastAPI in plain English
- 🧠 **LLM-Powered Synthesis**: Intelligent response generation using GPT models
- ⚡ **Smart Greeting Detection**: Instant responses for simple greetings without agent calls
- 🐳 **Docker Ready**: One-command deployment with `docker compose up`

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Setup and Installation](#setup-and-installation)
- [Agent Documentation](#agent-documentation)
- [API Documentation](#api-documentation)
- [Design Decisions](#design-decisions)
- [Known Limitations & Future Improvements](#known-limitations--future-improvements)

---

## Architecture Overview

### System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENT                                        │
│                            (HTTP Requests)                                      │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY                                        │
│                    FastAPI Container · Port 8000                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  /api/chat   │  │ /api/index/* │  │/api/agents/* │  │ /api/graph/* │         │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                           FastMCP Client (HTTP)
                                       │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR AGENT (Container)                            │
│                    FastMCP HTTP Server · Port 8004                             │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐         │
│  │  Intent Classifier │  │  Entity Extractor  │  │ Response Synthesizer│        │
│  │       (LLM)        │  │       (LLM)        │  │       (LLM)         │        │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘         │
│  ┌─────────────────────────────────────────────────────────────────────┐       │
│  │  Greeting Detection (Fast Path - No Agent Calls)                   │       │
│  └─────────────────────────────────────────────────────────────────────┘       │
│                                                                                 │
│  Tools: analyze_query, route_to_agents, synthesize_response                     │
└─────────────────────────────────────────────────────────────────────────────────┘
                    │                                           │
        ┌───────────┴─────────────┐                 ┌──────────┴──────────┐
        │ HTTP (FastMCP 2.12.0)  │                 │ HTTP (FastMCP)     │
        ▼                         ▼                 ▼                     ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐   ┌─────────────┐
│  GRAPH QUERY      │   │  CODE ANALYST     │   │    INDEXER        │   │   NEO4J     │
│     AGENT         │   │     AGENT         │   │     AGENT         │   │  DATABASE   │
│  Container        │   │  Container        │   │  Container        │   │  Container  │
│  Port 8001        │   │  Port 8002        │   │  Port 8003        │   │ Port 7687   │
│  (FastMCP HTTP)   │   │  (FastMCP HTTP)   │   │  (FastMCP HTTP)   │   │             │
├───────────────────┤   ├───────────────────┤   ├───────────────────┤   ├─────────────┤
│ • find_entity     │   │ • analyze_function│   │ • index_repo      │   │ • Classes   │
│ • get_dependencies│   │ • explain_impl    │   │ • index_file      │   │ • Functions │
│ • get_dependents  │   │ • find_patterns   │   │ • parse_ast       │   │ • Files     │
│ • find_related    │   │                   │   │ • extract_entities│   │ • Relations │
│ • execute_query   │   │                   │   │                   │   │             │
└───────────────────┘   └───────────────────┘   └───────────────────┘   └─────────────┘
        │                         │                       │                     │
        │                         │                       │                     │
        └─────────────────────────┴───────────────────────┴─────────────────────┘
                                           │
                                   Neo4j Bolt Protocol
                                           │
                                   (All agents connect)
```

**Architecture Notes:**
- **Microservices**: Each agent runs in a separate Docker container
- **HTTP Transport**: Agents communicate via FastMCP HTTP (version 2.12.0)
- **Independent Scaling**: Each agent can be scaled independently
- **Fast Path**: Greetings bypass agent calls for instant responses

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              QUERY PROCESSING FLOW                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Example 1: Simple Greeting                                                     │
│  ──────────────────────────────────────────────────────────────────────────────│
│  User Query: "Hello"                                                            │
│       │                                                                         │
│       ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐            │
│  │ 1. GREETING DETECTION (LLM)                                     │            │
│  │    Input:  "Hello"                                               │            │
│  │    Output: { is_greeting: true }                                 │            │
│  └─────────────────────────────────────────────────────────────────┘            │
│       │                                                                         │
│       ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐            │
│  │ 2. INSTANT RESPONSE (No Agent Calls)                            │            │
│  │    Output: "Hi there! I can help you understand..."             │            │
│  └─────────────────────────────────────────────────────────────────┘            │
│                                                                                 │
│  Example 2: Complex Query                                                        │
│  ──────────────────────────────────────────────────────────────────────────────│
│  User Query: "What is the FastAPI class?"                                       │
│       │                                                                         │
│       ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐            │
│  │ 1. GREETING DETECTION (LLM)                                     │            │
│  │    Input:  "What is the FastAPI class?"                         │            │
│  │    Output: { is_greeting: false }                               │            │
│  └─────────────────────────────────────────────────────────────────┘            │
│       │                                                                         │
│       ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐            │
│  │ 2. INTENT CLASSIFICATION (LLM)                                  │            │
│  │    Input:  "What is the FastAPI class?"                         │            │
│  │    Output: { intent: "lookup", agents: ["graph_query"] }        │            │
│  └─────────────────────────────────────────────────────────────────┘            │
│       │                                                                         │
│       ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐            │
│  │ 3. ENTITY EXTRACTION (LLM)                                      │            │
│  │    Input:  "What is the FastAPI class?"                         │            │
│  │    Output: { entity_name: "FastAPI", query_type: "find_entity" }│            │
│  └─────────────────────────────────────────────────────────────────┘            │
│       │                                                                         │
│       ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐            │
│  │ 4. AGENT DISPATCH (HTTP)                                         │            │
│  │    Route to: Graph Query Agent (http://graph-query-agent:8001) │            │
│  │    Tool:     find_entity("FastAPI")                             │            │
│  └─────────────────────────────────────────────────────────────────┘            │
│       │                                                                         │
│       ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐            │
│  │ 5. GRAPH QUERY (Neo4j)                                          │            │
│  │    Cypher: MATCH (c:Class {name: 'FastAPI'}) RETURN c           │            │
│  │    Result: { file: "fastapi/applications.py", lines: 48-4669 }  │            │
│  └─────────────────────────────────────────────────────────────────┘            │
│       │                                                                         │
│       ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐            │
│  │ 6. RESPONSE SYNTHESIS (LLM)                                    │            │
│  │    Combines: Graph results + LLM knowledge                      │            │
│  │    Output:   Comprehensive explanation of FastAPI class         │            │
│  └─────────────────────────────────────────────────────────────────┘            │
│       │                                                                         │
│       ▼                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐            │
│  │ 7. RESPONSE FORMAT                                              │            │
│  │    { session_id: "uuid", response: "..." }                      │            │
│  └─────────────────────────────────────────────────────────────────┘            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Knowledge Graph Schema

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              GRAPH SCHEMA                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  NODE TYPES:                                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    File     │  │    Class    │  │  Function   │  │   Import    │             │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤  ├─────────────┤             │
│  │ path        │  │ name        │  │ name        │  │ module      │             │
│  │ name        │  │ file        │  │ file        │  │ alias       │             │
│  │             │  │ start       │  │ start       │  │             │             │
│  │             │  │ end         │  │ end         │  │             │             │
│  │             │  │ docstring   │  │ is_async    │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                                 │
│  RELATIONSHIPS:                                                                 │
│                                                                                 │
│  (File)──[:CONTAINS]──▶(Class)                                                  │
│  (File)──[:CONTAINS]──▶(Function)                                               │
│  (Class)──[:INHERITS_FROM]──▶(Class)                                            │
│  (Function)──[:CALLS]──▶(Function)                                              │
│  (File)──[:IMPORTS]──▶(File|Import)                                             │
│  (Class|Function)──[:DECORATED_BY]──▶(Decorator)                                │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Setup and Installation

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11+ | Runtime environment |
| Docker | Latest | Container runtime |
| Docker Compose | v2+ | Service orchestration |
| OpenAI API Key | - | LLM access |

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone <repo-url>
cd fastapi-repo-chat-agent

# 2. Create shared.env for Docker
cat > shared.env << EOF
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL_ID=gpt-4o-mini
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
EOF

# 3. Start all services (microservices architecture)
docker compose up -d

# Services will start:
# - neo4j (port 7687, 7474)
# - graph-query-agent (port 8001)
# - code-analyst-agent (port 8002)
# - indexer-agent (port 8003)
# - orchestrator-agent (port 8004)
# - api-gateway (port 8000)

# 4. Verify services are running
docker compose ps

# Expected output:
# NAME                                    STATUS              PORTS
# fastapi-repo-api                        Up                  0.0.0.0:8000->8000/tcp
# fastapi-repo-neo4j                      Up (healthy)        0.0.0.0:7474->7474/tcp, 0.0.0.0:7687->7687/tcp
# fastapi-repo-chat-agent-orchestrator... Up                  8004/tcp
# fastapi-repo-chat-agent-graph-query...  Up                  8001/tcp
# fastapi-repo-chat-agent-code-analyst... Up                  8002/tcp
# fastapi-repo-chat-agent-indexer-agent   Up                  8003/tcp

# 4b. Scale agents independently (optional)
docker compose up -d --scale graph-query-agent=3

# 5. Check agent health
curl http://localhost:8000/api/agents/health

# 6. Start indexing
curl -X POST http://localhost:8000/api/index/start

# 7. Monitor indexing (replace JOB_ID)
curl http://localhost:8000/api/index/status/{JOB_ID}
```

### Option 2: Local Development

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start Neo4j with Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5-community

# 4. Create .env files for each agent
# orchestrator-agent/.env
cat > orchestrator-agent/.env << EOF
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL_ID=gpt-5-mini
EOF

# indexer-agent/.env, graph-query-agent/.env, code-analyst-agent/.env
# (similar content, add NEO4J_URI=bolt://localhost:7687)

# 5. Start the API Gateway
cd api-gateway
uvicorn app.main:app --reload --port 8000
```

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | - | OpenAI API key for LLM calls |
| `LLM_MODEL_ID` | No | `gpt-4o-mini` | Model for intent/synthesis |
| `NEO4J_URI` | No | `bolt://localhost:7687` | Neo4j connection string |
| `NEO4J_USER` | No | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | No | `password` | Neo4j password |
| `FASTAPI_REPO_URL` | No | FastAPI GitHub | Repository to index |
| `REPO_DIR` | No | `/tmp/fastapi-repo` | Local clone directory |

---

## Agent Documentation

### Orchestrator Agent

**Purpose**: Central coordinator that routes queries, manages agent calls, and synthesizes responses.

**Location**: `orchestrator-agent/`

**Tools**:

| Tool | Parameters | Description |
|------|------------|-------------|
| `analyze_query` | `query: str` | Classify intent and determine candidate agents |
| `route_to_agents` | `query: str, session_id: str` | Route query and persist routing decision |
| `synthesize_response` | `query: str, session_id: str, user_context: dict` | Full orchestration pipeline |
| `get_conversation_context` | `session_id: str` | Retrieve conversation history |

**Key Components**:

```
orchestrator-agent/
├── orchestrator_mcp.py      # MCP server entry point
└── app/
    ├── config.py            # Settings (OpenAI key, agent paths)
    ├── llm.py               # LLM calls (intent, extraction, synthesis)
    ├── routing/
    │   ├── intent.py        # Intent classification logic
    │   └── router.py        # Agent routing decisions
    ├── synthesis/
    │   └── synthesizer.py   # Response combination
    ├── memory/
    │   ├── models.py        # Data models (turns, routing decisions)
    │   └── store.py         # Conversation memory store
    └── clients/
        ├── base.py          # Base MCP client wrapper
        ├── graph_agent.py   # Graph Query Agent client
        └── code_agent.py    # Code Analyst Agent client
```

---

### Graph Query Agent

**Purpose**: Execute queries against the Neo4j knowledge graph to find code entities and relationships.

**Location**: `graph-query-agent/`

**Tools**:

| Tool | Parameters | Description |
|------|------------|-------------|
| `find_entity` | `name: str` | Locate a class, function, module, or file by name |
| `get_dependencies` | `name: str` | Find what an entity depends on (CALLS graph) |
| `get_dependents` | `name: str` | Find who depends on this entity |
| `find_related` | `name: str, relationship: str` | Search by relationship type |
| `trace_imports` | `path: str` | Follow IMPORTS chain for a module |
| `execute_query` | `query: str` | Run read-only Cypher queries |

**Supported Relationships**:
- `CONTAINS` - File contains class/function
- `IMPORTS` - File imports another file/module
- `CALLS` - Function calls another function
- `INHERITS_FROM` - Class inherits from another class
- `DECORATED_BY` - Entity decorated by decorator

**Example Usage**:

```python
# Find a class
await client.call_tool("find_entity", {"name": "FastAPI"})

# Find subclasses
await client.call_tool("find_related", {
    "name": "BaseModel", 
    "relationship": "INHERITS_FROM"
})

# Raw Cypher
await client.call_tool("execute_query", {
    "query": "MATCH (f:Function) WHERE f.is_async = true RETURN f.name LIMIT 10"
})
```

---

### Code Analyst Agent

**Purpose**: Analyze code patterns and provide explanations using LLM.

**Location**: `code-analyst-agent/`

**Tools**:

| Tool | Parameters | Description |
|------|------------|-------------|
| `analyze_function` | `name: str` | Analyze a function's implementation |
| `explain_implementation` | `name: str` | Explain how code works |

**Key Components**:

```
code-analyst-agent/
├── code_analyst_mcp.py     # MCP server entry point
└── app/
    ├── config.py           # Settings
    ├── graph/
    │   └── driver.py       # Neo4j connection
    └── utils/
        ├── analysis.py     # Code analysis utilities
        ├── llm.py          # LLM-based explanations
        ├── patterns.py     # Pattern detection
        └── snippet.py      # Code snippet extraction
```

---

### Indexer Agent

**Purpose**: Clone repositories, parse Python AST, and populate the knowledge graph.

**Location**: `indexer-agent/`

**Tools**:

| Tool | Parameters | Description |
|------|------------|-------------|
| `index_repo` | - | Index the full FastAPI repository |
| `index_single_file` | `path: str` | Index a specific Python file |
| `parse_ast` | `path: str` | Return AST node count for a file |
| `extract_code_entities` | `path: str` | Extract entities and push to Neo4j |
| `index_status` | - | Get indexer health status |

**Indexing Pipeline**:

```
1. Clone/Pull Repository (GitPython)
       │
       ▼
2. Discover *.py files (pathlib.rglob)
       │
       ▼
3. For each file (batched, 3 concurrent):
   ├── Parse AST (ast.parse)
   ├── Extract classes, functions, imports
   └── Create Neo4j nodes & relationships
       │
       ▼
4. Return { indexed_files: N }
```

---

## API Documentation

### POST /api/chat

Send a natural language query to the multi-agent system.

**Request**:
```json
{
    "message": "What is the FastAPI class?",
    "session_id": "optional-session-id"
}
```

**Response**:
```json
{
    "session_id": "uuid",
    "response": "The FastAPI class is..."
}
```

**Note**: Simple greetings like "hi", "hello", "thanks" are detected and return instant responses without calling agents.

**Example**:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the FastAPI class?"}'
```

---

### POST /api/index/start

Start indexing the configured repository.

**Request**: No body required

**Response**:
```json
{
    "job_id": "a88f1e2f-a7bc-45f8-9a79-445c0acae726"
}
```

---

### GET /api/index/status/{job_id}

Check the status of an indexing job.

**Response**:
```json
{
    "job_id": "a88f1e2f-a7bc-45f8-9a79-445c0acae726",
    "status": "completed",  // "running", "failed", "completed"
    "error": null,
    "updated_at": "2026-01-03T00:11:51.201093"
}
```

---

### GET /api/agents/health

Check health status of all agents.

**Response**:
```json
{
    "orchestrator": true,
    "indexer": true,
    "graph": true,
    "code_analyst": true
}
```

---

### GET /api/graph/statistics

Get knowledge graph statistics.

**Response**:
```json
{
    "total_nodes": 15234,
    "total_relationships": 48291
}
```

---

## Design Decisions

### Why Multi-Agent Architecture?

| Decision | Rationale |
|----------|-----------|
| **Separation of Concerns** | Each agent has a single responsibility, making the system easier to understand, test, and maintain |
| **Independent Scaling** | Agents can be scaled based on load (e.g., multiple indexers) |
| **Fault Isolation** | Failure in one agent doesn't crash the entire system |
| **Technology Flexibility** | Each agent can use different tools/libraries as needed |

### Why FastMCP for Agent Communication?

| Decision | Rationale |
|----------|-----------|
| **Microservices Architecture** | Each agent runs as a separate container, enabling independent scaling and fault isolation |
| **HTTP Transport** | Agents communicate via HTTP (FastMCP 2.12.0), allowing network-based deployment |
| **Type-Safe Tools** | Pydantic validation ensures correct parameter types |
| **Standard Protocol** | MCP is an emerging standard for AI tool use |
| **Async Native** | Non-blocking I/O for better throughput |

**Note**: We use `fastmcp==2.12.0` as it has stable HTTP transport support. Newer versions may have issues with tool execution over HTTP.

**Trade-off**: HTTP communication adds network latency (~10-50ms per call), but enables true microservices with horizontal scaling.

### Why Neo4j for Knowledge Storage?

| Decision | Rationale |
|----------|-----------|
| **Native Graph Model** | Code relationships (imports, calls, inheritance) are naturally graph-shaped |
| **Cypher Query Language** | Expressive pattern matching for complex relationship queries |
| **Visualization** | Built-in browser for exploring and debugging data |
| **ACID Transactions** | Data consistency during indexing |

**Trade-off**: Neo4j requires separate infrastructure. For simpler use cases, SQLite with recursive CTEs could work.

### Why LLM-Based Intent Classification?

| Decision | Rationale |
|----------|-----------|
| **Flexibility** | Handles varied natural language without rigid patterns |
| **Extensibility** | Easy to add new intents by updating prompts |
| **Context Awareness** | Can understand nuanced queries |

**Trade-off**: LLM calls add latency (~500ms-2s). For latency-critical apps, consider hybrid approach with rule-based fast path.

### Entity Extraction Strategy

Two-stage approach chosen for accuracy:

1. **Intent Classification**: Determines *which agents* to call
2. **Entity Extraction**: Extracts *specific parameters* for those agents

**Trade-off**: Two LLM calls instead of one, but significantly better accuracy for complex queries.

### Greeting Detection for Performance

Simple greetings are detected early to avoid unnecessary agent calls:

```python
# Fast path for greetings
if await is_greeting(query):
    return {"session_id": session_id, "response": "Hi there! I can help..."}
```

**Rationale**: Instant responses for common greetings improve user experience and reduce LLM costs.

### Docker Environment Detection

Agents detect Docker environment to use correct Neo4j hostname:

```python
def _get_neo4j_default():
    if os.path.exists("/.dockerenv"):
        return "bolt://neo4j:7687"  # Docker service name
    return "bolt://localhost:7687"  # Local development
```

**Rationale**: In microservices architecture, each container needs to know the correct service names for inter-container communication.

---

## Known Limitations & Future Improvements

### Current Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| **No streaming responses** | Long answers appear all at once | Wait for complete response |
| **Single repository support** | Can only index one repo at a time | Re-index to switch repos |
| **Limited relationship extraction** | Not all code relationships captured | Use raw Cypher for complex queries |
| **No semantic code search** | Relies on exact entity names | Use broader search terms |
| **HTTP network latency** | Agent calls add ~10-50ms overhead | Acceptable trade-off for microservices benefits |
| **Neo4j deadlocks with high concurrency** | Indexing may fail | Reduced to 3 concurrent file indexes |

### Planned Improvements

| Feature | Priority | Description |
|---------|----------|-------------|
| **Streaming Responses** | High | Server-sent events for progressive output |
| **Vector Embeddings** | High | Semantic search using code embeddings |
| **Multi-Repo Support** | Medium | Index and query multiple repositories |
| **Web UI** | Medium | Interactive chat interface and graph explorer |
| **Caching Layer** | Medium | Redis cache for frequent queries |
| **More Relationships** | Low | Type annotations, decorators, exceptions |
| **Code Snippet Highlighting** | Low | Syntax-highlighted code in responses |
| **Authentication** | Low | API key/OAuth for production use |

### Contributing

Contributions welcome! Areas that need help:

1. **Better AST parsing** - Extract more relationship types
2. **Performance optimization** - Reduce LLM call latency
3. **Test coverage** - Unit and integration tests
4. **Documentation** - More examples and tutorials

---

## Quick Reference

### Common Commands

```bash
# Start all services (microservices)
docker compose up -d

# Scale specific agents
docker compose up -d --scale graph-query-agent=3

# Stop services
docker compose down

# View logs
docker compose logs -f api-gateway
docker compose logs -f orchestrator-agent

# Rebuild after code changes
docker compose up -d --build api-gateway orchestrator-agent

# Access Neo4j browser
open http://localhost:7474

# Run Cypher query
docker exec -it fastapi-repo-neo4j cypher-shell -u neo4j -p password \
  "MATCH (n) RETURN labels(n), count(n)"
```

### Example Queries

```bash
# Simple
"What is the FastAPI class?"
"Find the Depends function"

# Medium
"What classes inherit from APIRouter?"
"What does the Router class depend on?"

# Complex
"Explain the complete lifecycle of a FastAPI request"
"What design patterns are used in FastAPI core?"
"Compare how Path and Query parameters are implemented"
```

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The framework being analyzed
- [FastMCP](https://gofastmcp.com/) - Agent communication protocol
- [Neo4j](https://neo4j.com/) - Graph database
- [OpenAI](https://openai.com/) - LLM provider
