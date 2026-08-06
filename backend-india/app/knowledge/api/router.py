"""
QuantView Financial Knowledge Platform — REST API Endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional

from app.knowledge.models import SearchQuery, SearchResponse
from app.knowledge.retrieval import HybridSearchEngine
from app.knowledge.pipeline import IngestionPipeline
from app.knowledge.config import knowledge_settings

router = APIRouter(prefix="/knowledge", tags=["Financial Knowledge Platform"])
search_engine = HybridSearchEngine()


@router.post("/search", response_model=SearchResponse)
async def hybrid_search(query: SearchQuery):
    """
    Perform hybrid vector + keyword search against QuantView Knowledge Base.
    Returns structured chunks with section, page number, and source citations.
    """
    try:
        return search_engine.search(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hybrid Search failed: {e}")


@router.post("/context")
async def get_agent_context(symbol: str, query: str, top_k: int = 5):
    """
    Agent Consumption Endpoint: Supplies RAG context to Planner, Financial, Risk, and Synthesis Agents.
    """
    try:
        search_req = SearchQuery(query=query, symbol=symbol, top_k=top_k)
        resp = search_engine.search(search_req)
        
        # Build context string
        context_blocks = []
        for hit in resp.hits:
            sec_name = hit.metadata.section.value if hasattr(hit.metadata.section, "value") else str(hit.metadata.section)
            context_blocks.append(
                f"[Source: {hit.metadata.company} ({hit.metadata.year}) | Section: {sec_name} | Page: {hit.metadata.page_number}]\n"
                f"{hit.text}"
            )
            
        full_context = "\n\n---\n\n".join(context_blocks)
        return {
            "symbol": symbol,
            "query": query,
            "retrieved_chunks_count": len(resp.hits),
            "context": full_context,
            "hits": resp.hits,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context retrieval failed: {e}")


@router.post("/company")
async def ingest_company(symbol: str, background_tasks: BackgroundTasks):
    """Trigger document discovery, download, parsing, chunking, and embedding for a company symbol."""
    pipeline = IngestionPipeline()
    background_tasks.add_task(pipeline.ingest_company, symbol)
    return {"status": "accepted", "symbol": symbol, "message": f"Ingestion job started for {symbol}"}


@router.get("/status")
async def platform_status():
    """Expose system statistics, vector database status, and configuration info."""
    return {
        "status": "operational",
        "embedding_model": knowledge_settings.embedding_model_name,
        "embedding_dimension": knowledge_settings.embedding_dimension,
        "qdrant_host": knowledge_settings.qdrant_host,
        "qdrant_port": knowledge_settings.qdrant_port,
        "qdrant_collection": knowledge_settings.qdrant_collection_annual_reports,
        "storage_root": str(knowledge_settings.storage_root),
    }
