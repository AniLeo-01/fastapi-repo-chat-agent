import ast
import builtins
from app.graph.driver import run_query

PYTHON_BUILTINS = set(dir(builtins))


async def extract_entities(tree: ast.AST, file_path: str) -> dict:
    """
    Extract entities from a Python AST and populate Neo4j
    according to the required knowledge graph schema.
    """

    # ------------------------------------------------------
    # File node
    # ------------------------------------------------------
    await run_query(
        """
        MERGE (f:File {path:$file})
        RETURN f
        """,
        {"file": file_path},
    )

    current_class: str | None = None
    current_function: str | None = None

    for node in ast.walk(tree):

        # ==================================================
        # IMPORTS → Import, Module, IMPORTS, DEPENDS_ON
        # ==================================================
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                if module in PYTHON_BUILTINS:
                    continue

                await run_query(
                    """
                    MERGE (i:Import {name:$module})
                    MERGE (m:Module {name:$module})
                    WITH i, m
                    MATCH (f:File {path:$file})
                    MERGE (f)-[:IMPORTS]->(i)
                    MERGE (i)-[:DEPENDS_ON]->(m)
                    """,
                    {"file": file_path, "module": module},
                )

        if isinstance(node, ast.ImportFrom) and node.module:
            module = node.module
            if module not in PYTHON_BUILTINS:
                await run_query(
                    """
                    MERGE (i:Import {name:$module})
                    MERGE (m:Module {name:$module})
                    WITH i, m
                    MATCH (f:File {path:$file})
                    MERGE (f)-[:IMPORTS]->(i)
                    MERGE (i)-[:DEPENDS_ON]->(m)
                    """,
                    {"file": file_path, "module": module},
                )

        # ==================================================
        # CLASS → Class, CONTAINS, INHERITS_FROM, DOCSTRING
        # ==================================================
        if isinstance(node, ast.ClassDef):
            current_class = node.name
            current_function = None

            await run_query(
                """
                MERGE (c:Class {name:$name, file:$file})
                SET c.start = $start, c.end = $end
                WITH c
                MATCH (f:File {path:$file})
                MERGE (f)-[:CONTAINS]->(c)
                """,
                {
                    "name": node.name,
                    "file": file_path,
                    "start": node.lineno,
                    "end": node.end_lineno,
                },
            )

            # Inheritance
            for base in node.bases:
                if isinstance(base, ast.Name):
                    await run_query(
                        """
                        MATCH (child:Class {name:$child})
                        MERGE (parent:Class {name:$parent})
                        MERGE (child)-[:INHERITS_FROM]->(parent)
                        """,
                        {"child": node.name, "parent": base.id},
                    )

            # Docstring
            doc = ast.get_docstring(node)
            if doc:
                await run_query(
                    """
                    CREATE (d:Docstring {text:$doc})
                    WITH d
                    MATCH (c:Class {name:$cls})
                    MERGE (c)-[:DOCUMENTED_BY]->(d)
                    """,
                    {"cls": node.name, "doc": doc},
                )

        # ==================================================
        # FUNCTION / METHOD
        # ==================================================
        if isinstance(node, ast.FunctionDef):
            current_function = node.name
            label = "Method" if current_class else "Function"

            await run_query(
                f"""
                MERGE (fn:{label} {{name:$name, file:$file}})
                SET fn.start = $start, fn.end = $end
                WITH fn
                MATCH (f:File {{path:$file}})
                MERGE (f)-[:CONTAINS]->(fn)
                """,
                {
                    "name": node.name,
                    "file": file_path,
                    "start": node.lineno,
                    "end": node.end_lineno,
                },
            )

            # Parameters
            for arg in node.args.args:
                await run_query(
                    """
                    MERGE (p:Parameter {name:$param})
                    WITH p
                    MATCH (fn {name:$fn})
                    MERGE (fn)-[:HAS_PARAMETER]->(p)
                    """,
                    {"fn": node.name, "param": arg.arg},
                )

            # Decorators
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    dec_name = dec.id
                elif isinstance(dec, ast.Attribute):
                    dec_name = dec.attr
                else:
                    continue

                await run_query(
                    """
                    MERGE (d:Decorator {name:$dec})
                    WITH d
                    MATCH (fn {name:$fn})
                    MERGE (fn)-[:DECORATED_BY]->(d)
                    """,
                    {"fn": node.name, "dec": dec_name},
                )

            # Docstring
            doc = ast.get_docstring(node)
            if doc:
                await run_query(
                    """
                    CREATE (d:Docstring {text:$doc})
                    WITH d
                    MATCH (fn {name:$fn})
                    MERGE (fn)-[:DOCUMENTED_BY]->(d)
                    """,
                    {"fn": node.name, "doc": doc},
                )

        # ==================================================
        # CALL GRAPH → CALLS + DEPENDS_ON
        # ==================================================
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            callee = node.func.id

            if callee in PYTHON_BUILTINS:
                continue
            if not current_function:
                continue

            await run_query(
                """
                MATCH (caller {name:$caller})
                MERGE (callee:Function {name:$callee})
                MERGE (caller)-[:CALLS]->(callee)
                MERGE (caller)-[:DEPENDS_ON]->(callee)
                """,
                {"caller": current_function, "callee": callee},
            )

    return {"status": "indexed", "file": file_path}
