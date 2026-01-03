# apps/indexer-agent/app/indexing/ast_parser.py
import ast
import aiofiles

async def parse_python_ast(path: str) -> ast.AST:
    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        content = await f.read()
        return ast.parse(content)
