"""
QuantView — Knowledge Graph Agent

Traverses Neo4j graph nodes to discover competitor, customer, and supplier dependencies.
"""

from app.agents.state import AgentState
from app.db.neo4j import get_company_graph

class KGAgent:
    """Specialist node extracting corporate dependencies from Neo4j Aura."""

    @staticmethod
    async def execute(state: AgentState) -> dict:
        symbol = state["company_symbol"]
        evidence = []
        try:
            # Fetch connections from Neo4j
            graph_data = await get_company_graph(symbol)
            edges = graph_data.get("edges", [])
            for edge in edges:
                evidence.append({
                    "relationship": edge.get("type"),
                    "target": edge.get("target"),
                    "notes": edge.get("properties", {}).get("notes", "")
                })
        except Exception:
            pass

        return {
            "retrieved_evidence": [{
                "agent": "kg_agent",
                "evidence": evidence
            }]
        }
