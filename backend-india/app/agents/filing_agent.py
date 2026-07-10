"""
QuantView — Filing Analysis Agent

Queries Qdrant vector database to extract paragraph contexts from corporate annual reports.
"""

from app.agents.state import AgentState
from app.services.search_service import SearchService

class FilingAgent:
    """Specialist node resolving unstructured details in corporate filings."""

    @staticmethod
    async def execute(state: AgentState) -> dict:
        query = state["query"]
        symbol = state["company_symbol"]
        
        evidence = []
        try:
            # Search Qdrant vector db
            results = await SearchService.hybrid_search(
                query=query,
                company_symbol=symbol,
                limit=3
            )
            for item in results:
                payload = item.get("payload", {})
                evidence.append({
                    "source": payload.get("document_type", "annual_report"),
                    "text": payload.get("text", ""),
                    "page": payload.get("page_number", 1)
                })
        except Exception as e:
            pass

        return {
            "retrieved_evidence": [{
                "agent": "filing_agent",
                "evidence": evidence
            }]
        }
