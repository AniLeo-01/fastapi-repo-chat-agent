from neo4j import AsyncGraphDatabase
from app.config import settings

driver = AsyncGraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
)

async def run_query(cypher: str, params: dict = None):
    async with driver.session() as session:
        result = await session.run(cypher, params or {})
        records = await result.data()
        return records
