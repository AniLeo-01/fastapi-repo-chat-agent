from pathlib import Path
from .ast_parser import parse_python_ast
from .entity_extractor import extract_entities
from ..graph.driver import run_query

async def index_file(path: str):
    """
    Index a single Python file:
    - Create/merge File node in Neo4j
    - Parse Python AST
    - Extract classes & functions → push to graph
    """
    path = str(Path(path).resolve())

    # Create the file node in graph
    await run_query("""
        MERGE (f:File {path: $path})
        RETURN f
    """, {"path": path})

    # Parse + extract
    tree = await parse_python_ast(path)
    await extract_entities(tree, path)

    return {
        "status": "indexed",
        "file": path
    }
