from neo4j import AsyncGraphDatabase
from app.config import settings

async def get_graph_statistics():
    driver = AsyncGraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
    )

    async with driver.session() as session:
        nodes_result = await session.run(
            "MATCH (n) RETURN count(n) AS c"
        )
        nodes_record = await nodes_result.single()
        nodes = nodes_record["c"]

        rels_result = await session.run(
            "MATCH ()-[r]->() RETURN count(r) AS c"
        )
        rels_record = await rels_result.single()
        relationships = rels_record["c"]

    await driver.close()

    return {
        "total_nodes": nodes,
        "total_relationships": relationships,
    }
