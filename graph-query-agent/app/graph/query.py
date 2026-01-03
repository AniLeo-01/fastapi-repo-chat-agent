from .driver import run_query

# ---------------------------------------------------------
# 1) Find Entity
# ---------------------------------------------------------
async def find_entity_node(name: str):
    return await run_query("""
        MATCH (n {name:$name})
        RETURN n
    """, {"name": name})


# ---------------------------------------------------------
# 2) Dependencies (CALLS)
# ---------------------------------------------------------
async def get_dependencies_for(name: str):
    return await run_query("""
        MATCH (caller:Function {name:$name})-[:CALLS]->(dep)
        RETURN dep
    """, {"name": name})


# ---------------------------------------------------------
# 3) Dependents (reverse CALLS)
# ---------------------------------------------------------
async def get_dependents_for(name: str):
    return await run_query("""
        MATCH (dep)<-[:CALLS]-(caller:Function {name:$name})
        RETURN caller
    """, {"name": name})


# ---------------------------------------------------------
# 4) Trace Import Chains
# ---------------------------------------------------------
async def trace_import_chain(path: str):
    return await run_query("""
        MATCH p = (f:File {path:$path})-[:IMPORTS*1..5]->(m)
        RETURN p
    """, {"path": path})


# ---------------------------------------------------------
# 5) Find Related by Relationship Type
# ---------------------------------------------------------
async def find_related_entities(name: str, rel: str):
    allowed = ["CONTAINS","IMPORTS","CALLS","INHERITS_FROM","DECORATED_BY"]
    if rel not in allowed:
        return {"error": f"Invalid relationship type. Allowed: {allowed}"}

    return await run_query(
        f"""
        MATCH (a {{name:$name}})-[r:{rel}]->(b)
        RETURN a,r,b
        """,
        {"name": name}
    )


# ---------------------------------------------------------
# 6) Safe Cypher Executor
# ---------------------------------------------------------
async def execute_safe_cypher(query: str):
    blocked = ["DELETE", "DETACH", "REMOVE", "DROP", "MERGE", "SET"]
    if any(cmd in query.upper() for cmd in blocked):
        return {"error": "Query blocked for safety. Read-only queries only."}

    return await run_query(query)
