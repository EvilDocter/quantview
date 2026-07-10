"""
QuantView — Neo4j Graph Database Connection

Client for Neo4j Aura free tier — handles graph queries,
node/relationship CRUD, and knowledge graph traversals.
"""

from neo4j import AsyncGraphDatabase, AsyncDriver
from typing import Optional
from app.config import get_settings

settings = get_settings()

# ── Neo4j Driver ─────────────────────────────────────────────────
_driver: Optional[AsyncDriver] = None


async def get_neo4j_driver() -> AsyncDriver:
    """Get or create the Neo4j async driver."""
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _driver


async def close_neo4j():
    """Close the Neo4j driver."""
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None


async def init_neo4j_schema():
    """Create indexes and constraints for the knowledge graph."""
    driver = await get_neo4j_driver()
    async with driver.session() as session:
        # Unique constraints
        await session.run(
            "CREATE CONSTRAINT company_symbol IF NOT EXISTS "
            "FOR (c:Company) REQUIRE c.symbol IS UNIQUE"
        )
        await session.run(
            "CREATE CONSTRAINT person_id IF NOT EXISTS "
            "FOR (p:Person) REQUIRE p.id IS UNIQUE"
        )
        await session.run(
            "CREATE CONSTRAINT product_id IF NOT EXISTS "
            "FOR (p:Product) REQUIRE p.id IS UNIQUE"
        )
        await session.run(
            "CREATE CONSTRAINT sector_name IF NOT EXISTS "
            "FOR (s:Sector) REQUIRE s.name IS UNIQUE"
        )

        # Indexes for faster lookups
        await session.run(
            "CREATE INDEX company_name_idx IF NOT EXISTS "
            "FOR (c:Company) ON (c.name)"
        )
        await session.run(
            "CREATE INDEX person_name_idx IF NOT EXISTS "
            "FOR (p:Person) ON (p.name)"
        )

    print("✅ Neo4j schema initialized")


async def run_cypher(query: str, params: dict = None) -> list:
    """Execute a Cypher query and return results as a list of dicts."""
    driver = await get_neo4j_driver()
    async with driver.session() as session:
        result = await session.run(query, params or {})
        records = [record.data() async for record in result]
        return records


async def create_company_node(
    symbol: str, name: str, sector: str, market_cap: int = 0
):
    """Create or update a Company node in the knowledge graph."""
    query = """
    MERGE (c:Company {symbol: $symbol})
    SET c.name = $name,
        c.sector = $sector,
        c.market_cap = $market_cap,
        c.updated_at = datetime()
    RETURN c
    """
    return await run_cypher(
        query,
        {"symbol": symbol, "name": name, "sector": sector, "market_cap": market_cap},
    )


async def create_relationship(
    from_symbol: str,
    to_symbol: str,
    relationship_type: str,
    properties: dict = None,
):
    """Create a relationship between two Company nodes."""
    props_clause = ""
    params = {"from_symbol": from_symbol, "to_symbol": to_symbol}

    if properties:
        prop_parts = []
        for key, value in properties.items():
            params[f"prop_{key}"] = value
            prop_parts.append(f"{key}: $prop_{key}")
        props_clause = " {" + ", ".join(prop_parts) + "}"

    query = f"""
    MATCH (a:Company {{symbol: $from_symbol}})
    MATCH (b:Company {{symbol: $to_symbol}})
    MERGE (a)-[r:{relationship_type}{props_clause}]->(b)
    SET r.updated_at = datetime()
    RETURN a, r, b
    """
    return await run_cypher(query, params)


async def get_company_graph(symbol: str, depth: int = 1) -> dict:
    """
    Get the full relationship graph for a company.
    Returns nodes and edges for D3.js visualization.
    """
    query = """
    MATCH (c:Company {symbol: $symbol})-[r]-(related)
    RETURN c, type(r) as rel_type, properties(r) as rel_props,
           labels(related) as related_labels, properties(related) as related_props
    """
    records = await run_cypher(query, {"symbol": symbol})

    nodes = [{"id": symbol, "label": symbol, "type": "Company", "primary": True}]
    edges = []
    seen_nodes = {symbol}

    for record in records:
        related_id = (
            record["related_props"].get("symbol")
            or record["related_props"].get("name")
            or record["related_props"].get("id", "unknown")
        )
        if related_id not in seen_nodes:
            nodes.append(
                {
                    "id": related_id,
                    "label": record["related_props"].get("name", related_id),
                    "type": record["related_labels"][0] if record["related_labels"] else "Unknown",
                }
            )
            seen_nodes.add(related_id)

        edges.append(
            {
                "source": symbol,
                "target": related_id,
                "type": record["rel_type"],
                "properties": record.get("rel_props", {}),
            }
        )

    return {"nodes": nodes, "edges": edges}


async def keep_alive():
    """Ping Neo4j to prevent Aura Free auto-pause (3-day inactivity)."""
    driver = await get_neo4j_driver()
    async with driver.session() as session:
        result = await session.run("RETURN 1 AS ping")
        record = await result.single()
        return record["ping"] == 1
