"""
QuantView — Neo4j Knowledge Graph Populator

Saves entities and relationships extracted from corporate filings directly into Neo4j Aura.
"""

import logging
from app.db.neo4j import create_company_node, create_relationship

logger = logging.getLogger("graph_populator")

class GraphPopulator:
    """Orchestrates writing raw entities and relationships to Neo4j graph nodes."""

    @staticmethod
    async def populate_extracted_knowledge(
        company_symbol: str,
        company_name: str,
        relationships: list[dict]
    ):
        """Creates parent node and connects related entities."""
        try:
            # 1. Ensure primary Company Node exists
            await create_company_node(
                symbol=company_symbol,
                name=company_name,
                sector="Diversified" # Default sector, normalized dynamically
            )
            
            # 2. Add relationships
            for rel in relationships:
                related_entity = rel.get("entity")
                rel_type = rel.get("type")
                notes = rel.get("notes", "")

                if not related_entity or not rel_type:
                    continue

                # For simplicity, create target company node if not exists
                await create_company_node(
                    symbol=related_entity.upper().replace(" ", "_"),
                    name=related_entity,
                    sector="Unknown"
                )

                # Link them
                await create_relationship(
                    from_symbol=company_symbol,
                    to_symbol=related_entity.upper().replace(" ", "_"),
                    relationship_type=rel_type,
                    properties={"notes": notes}
                )
                
            logger.info(f"Populated {len(relationships)} graph relationships for {company_symbol}")
        except Exception as e:
            logger.error(f"Failed to populate graph for {company_symbol}: {e}")
