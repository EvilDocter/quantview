"""
QuantView — Filing Analysis Agent (Knowledge Platform RAG Bridge)

Queries QuantView Financial Knowledge Platform (Qdrant Vector DB + Hybrid Search)
to retrieve exact annual report chunks, financial statements, and page citations.
"""

from app.agents.state import AgentState
import logging
import asyncio
from typing import List, Dict, Any

from app.knowledge.retrieval import HybridSearchEngine
from app.knowledge.models import SearchQuery
from ddgs import DDGS
import trafilatura

logger = logging.getLogger("filing_agent")
search_engine = HybridSearchEngine()


class FilingAgent:
    """Specialist node resolving corporate filing data via Knowledge Platform RAG & local Qdrant."""

    @staticmethod
    async def execute(state: AgentState) -> dict:
        symbol = state["company_symbol"]
        query = state["query"]
        evidence: List[Dict[str, Any]] = []

        # 1. Query QuantView Financial Knowledge Platform (Qdrant Vector DB + BM25)
        try:
            logger.info(f"Querying Knowledge Platform RAG for {symbol}...")
            search_req = SearchQuery(query=f"{symbol} {query}", symbol=symbol, top_k=5, min_score=0.25)
            search_resp = await asyncio.to_thread(search_engine.search, search_req)

            if search_resp.hits:
                logger.info(f"Retrieved {len(search_resp.hits)} RAG chunks for {symbol}")
                for hit in search_resp.hits:
                    sec_val = hit.metadata.section.value if hasattr(hit.metadata.section, "value") else str(hit.metadata.section)
                    evidence.append({
                        "source": f"QuantView Knowledge RAG (NSE {symbol} {hit.metadata.year} Annual Report)",
                        "title": f"Section: {sec_val} | Page {hit.metadata.page_number}",
                        "url": hit.metadata.source_file,
                        "content": hit.text,
                        "page": hit.metadata.page_number,
                        "section": sec_val,
                        "year": hit.metadata.year,
                        "score": hit.score,
                    })
        except Exception as e:
            logger.warning(f"Knowledge Platform RAG lookup error for {symbol}: {e}")

        # 2. Web search fallback if no local RAG chunks found
        if not evidence:
            try:
                logger.info(f"No RAG chunks found. Live DDGS fallback for {symbol}")
                ddgs = DDGS()
                results = list(ddgs.text(keywords=f"{symbol} annual report filing results", max_results=3))

                for item in results:
                    url = item.get("href", "")
                    title = item.get("title", "")
                    content = item.get("body", "")

                    evidence.append({
                        "source": "duckduckgo_filing_scraper",
                        "title": title,
                        "url": url,
                        "content": content,
                    })
            except Exception as e:
                logger.error(f"Live filing scraping failed for {symbol}: {e}")

        return {
            "retrieved_evidence": [{
                "agent": "filing_agent",
                "evidence": evidence,
            }]
        }
