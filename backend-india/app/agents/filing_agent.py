"""
QuantView — Filing Analysis Agent (Knowledge Platform RAG Bridge + Real-Time Auto-Ingestion)

Queries QuantView Financial Knowledge Platform (Qdrant Vector DB + Hybrid Search).
If a company's reports are not yet ingested, automatically triggers real-time
NSE document discovery, PDF download, extraction, chunking, and Qdrant indexing on-the-fly!
"""

from app.agents.state import AgentState
import logging
import asyncio
from typing import List, Dict, Any

from app.knowledge.retrieval import HybridSearchEngine
from app.knowledge.pipeline import KnowledgeIngestionPipeline
from app.knowledge.models import SearchQuery
from ddgs import DDGS

logger = logging.getLogger("filing_agent")
search_engine = HybridSearchEngine()
pipeline = KnowledgeIngestionPipeline()


class FilingAgent:
    """Specialist node resolving corporate filing data via Knowledge Platform RAG & real-time auto-ingestion."""

    @staticmethod
    async def execute(state: AgentState) -> dict:
        symbol = state["company_symbol"]
        query = state["query"]
        evidence: List[Dict[str, Any]] = []

        if not symbol or symbol == "NIFTY50":
            symbol = "INFY"  # Default fallback benchmark

        # 1. Query QuantView Financial Knowledge Platform (Qdrant Vector DB + BM25)
        try:
            logger.info(f"Querying Knowledge Platform RAG for {symbol}...")
            search_req = SearchQuery(query=f"{symbol} {query}", symbol=symbol, top_k=5, min_score=0.20)
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

        # 2. Real-Time Auto-Ingestion: If no local RAG chunks found, download & index filings on-the-fly!
        if not evidence:
            try:
                logger.info(f"No RAG chunks in Qdrant for '{symbol}'. Triggering Real-Time Auto-Ingestion on-the-fly...")
                ingest_res = await pipeline.ingest_company(symbol)
                logger.info(f"Auto-ingestion completed for {symbol}: {ingest_res}")

                # Re-query Knowledge Platform post-ingestion
                search_req = SearchQuery(query=f"{symbol} {query}", symbol=symbol, top_k=5, min_score=0.15)
                search_resp = await asyncio.to_thread(search_engine.search, search_req)

                if search_resp.hits:
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
                logger.warning(f"Real-time auto-ingestion for {symbol} encountered error: {e}")

        # 3. Live DDGS Search Fallback if still empty
        if not evidence:
            try:
                logger.info(f"Live DDGS fallback for {symbol}")
                ddgs = DDGS()
                results = list(ddgs.text(keywords=f"{symbol} annual report filing results risk factors", max_results=3))
                for item in results:
                    evidence.append({
                        "source": f"Live Web Search ({symbol} Filings)",
                        "title": item.get("title", ""),
                        "url": item.get("href", ""),
                        "content": item.get("body", ""),
                    })
            except Exception as e:
                logger.warning(f"DDGS web search fallback failed for {symbol}: {e}")

        return {
            "retrieved_evidence": [{
                "agent": "filing_agent",
                "evidence": evidence,
            }]
        }
