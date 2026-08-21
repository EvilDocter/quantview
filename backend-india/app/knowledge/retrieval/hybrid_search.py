"""
QuantView Financial Knowledge Platform — Hybrid Search Engine

Combines Qdrant HNSW vector search with BM25 keyword matching and metadata filters.
"""

import time
import logging
import re
import math
from typing import List, Optional, Dict, Any

from app.knowledge.embeddings import EmbeddingService
from app.knowledge.vector import QdrantVectorStore
from app.knowledge.models import SearchQuery, SearchResponse, SearchHit, SectionType

logger = logging.getLogger("knowledge_retrieval")

# Financial terminology expansion dictionary for Indian equities
FINANCIAL_SYNONYMS: Dict[str, str] = {
    "nim": "net interest margin interest income yield",
    "casa": "current account savings account low cost deposit",
    "credit cost": "provisioning impairment bad debts credit loss",
    "npa": "non performing assets gross npa net npa asset quality",
    "npas": "non performing assets gross npa net npa asset quality",
    "slippage": "fresh asset quality degradation new npa addition",
    "slippages": "fresh asset quality degradation new npa addition",
    "roe": "return on equity profitability shareholder return",
    "ebitda": "operating profit ebitda margin operating earnings",
    "fcf": "free cash flow operating cash flow capex",
    "capex": "capital expenditure property plant equipment expansion",
    "gnpa": "gross non performing assets asset quality",
    "nnpa": "net non performing assets provisions",
    "pru": "provision coverage ratio pcr",
    "pcr": "provision coverage ratio npa coverage",
}


def expand_query(query: str) -> str:
    """Expand query with domain-specific financial synonyms."""
    words = re.findall(r"\w+", query.lower())
    expanded = list(words)
    for word in words:
        if word in FINANCIAL_SYNONYMS:
            expanded.append(FINANCIAL_SYNONYMS[word])
    return " ".join(expanded)


class HybridSearchEngine:
    """Performs hybrid vector + BM25 keyword search against Qdrant and knowledge artifacts."""

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[QdrantVectorStore] = None,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ):
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or QdrantVectorStore()
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight

    def _bm25_score(self, query: str, text: str) -> float:
        """Compute term frequency overlap score for keyword matching."""
        if not text or not query:
            return 0.0
        q_terms = set(re.findall(r"\w+", query.lower()))
        t_terms = re.findall(r"\w+", text.lower())
        if not t_terms or not q_terms:
            return 0.0

        matches = sum(1 for term in t_terms if term in q_terms)
        score = matches / (len(t_terms) ** 0.5 + 1.0)
        return min(1.0, score)

    def search(self, request: SearchQuery) -> SearchResponse:
        """
        Perform hybrid search with fallback ladder:
        1. Primary: Vector + BM25 with strict filters and min_score
        2. Fallback 1: Lower min_score
        3. Fallback 2: Drop section filter
        4. Fallback 3: Drop year filter
        5. Fallback 4: Load local disk chunks.json if vector store yields no hits
        """
        start_time = time.time()
        expanded_q = expand_query(request.query)
        logger.info(
            f"Executing Hybrid Search for '{request.query}' (expanded: '{expanded_q}') "
            f"[symbol={request.symbol}, year={request.year}, section={request.section}]"
        )

        hits = self._execute_search_ladder(request, expanded_q)

        elapsed_ms = (time.time() - start_time) * 1000.0
        logger.info(f"Hybrid Search completed: {len(hits)} hits returned in {elapsed_ms:.1f} ms.")

        return SearchResponse(
            query=request.query,
            total_hits=len(hits),
            hits=hits,
            execution_time_ms=elapsed_ms,
        )

    def _execute_search_ladder(self, request: SearchQuery, expanded_query: str) -> List[SearchHit]:
        """Try search tiers iteratively until hits are found."""

        # Attempt 1: Strict search
        hits = self._single_search(request, expanded_query, request.min_score, request.section, request.year)
        if hits:
            return hits

        # Attempt 2: Lower min_score (0.15)
        logger.info("Search ladder Tier 2: Lowering min_score threshold to 0.15...")
        hits = self._single_search(request, expanded_query, 0.15, request.section, request.year)
        if hits:
            return hits

        # Attempt 3: Remove section filter
        if request.section:
            logger.info("Search ladder Tier 3: Removing section filter...")
            hits = self._single_search(request, expanded_query, 0.15, None, request.year)
            if hits:
                return hits

        # Attempt 4: Remove year filter
        if request.year:
            logger.info("Search ladder Tier 4: Removing year filter...")
            hits = self._single_search(request, expanded_query, 0.10, None, None)
            if hits:
                return hits

        # Attempt 5: Disk chunks fallback if vector store yields 0
        if request.symbol:
            logger.info(f"Search ladder Tier 5: Disk fallback for {request.symbol}...")
            return self._disk_chunks_fallback(request.symbol, request.query, request.top_k)

        return []

    def _single_search(
        self,
        request: SearchQuery,
        expanded_query: str,
        min_score: float,
        section: Optional[SectionType],
        year: Optional[int],
    ) -> List[SearchHit]:
        """Perform single vector query and blend with BM25 keyword score."""
        query_vec = self.embedding_service.generate_single_embedding(expanded_query)

        vector_hits = self.vector_store.search_similar_vectors(
            query_vector=query_vec,
            symbol=request.symbol,
            year=year,
            section=section,
            top_k=request.top_k * 2,  # Over-fetch for hybrid re-ranking
        )

        res_hits = []
        for v_hit in vector_hits:
            bm25 = self._bm25_score(expanded_query, v_hit.text)
            hybrid_score = (self.vector_weight * v_hit.score) + (self.keyword_weight * bm25)

            if hybrid_score >= min_score:
                v_hit.score = round(hybrid_score, 4)
                res_hits.append(v_hit)

        # Sort by hybrid score descending
        res_hits.sort(key=lambda h: h.score, reverse=True)
        return res_hits[: request.top_k]

    def _disk_chunks_fallback(self, symbol: str, query: str, top_k: int) -> List[SearchHit]:
        """Load disk-cached chunks if Qdrant has not yet indexed this symbol."""
        from app.knowledge.crawler.dynamic_scraper import BASE_DIR
        import json
        from app.knowledge.models import ChunkMetadata, SectionType

        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "")
        company_dir = BASE_DIR / "documents" / "NSE" / clean_sym

        if not company_dir.exists():
            return []

        all_chunks = []
        for year_dir in sorted(company_dir.iterdir(), reverse=True):
            if year_dir.is_dir():
                for sub in ["annual_report", "AnnualReport"]:
                    chunks_file = year_dir / sub / "chunks.json"
                    if chunks_file.exists():
                        try:
                            with open(chunks_file, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                for c in data:
                                    c["_year"] = int(year_dir.name) if year_dir.name.isdigit() else 2024
                                    all_chunks.append(c)
                        except Exception:
                            pass

        if not all_chunks:
            return []

        # Rank disk chunks by BM25 keyword score
        q_lower = query.lower()
        q_words = set(re.findall(r"\w+", q_lower))

        scored = []
        for idx, c in enumerate(all_chunks):
            text = c.get("text", "")
            page_num = c.get("page_number", c.get("page", 1))
            sec_str = c.get("section", "BUSINESS_OVERVIEW")
            year = c.get("_year", 2024)

            score = self._bm25_score(query, text)
            text_lower = text.lower()
            match_count = sum(text_lower.count(w) for w in q_words if len(w) > 2)
            if match_count > 0:
                score += 0.2 + (0.05 * min(10, match_count))

            meta = ChunkMetadata(
                company=f"{clean_sym} Limited",
                symbol=clean_sym,
                exchange="NSE",
                year=year,
                document_type="Annual Report",
                section=SectionType.GENERAL,
                heading=f"Page {page_num}",
                page_number=page_num,
                chunk_index=idx + 1,
                sha256_hash="disk_fallback",
            )

            scored.append(
                SearchHit(
                    chunk_id=c.get("chunk_id", f"{clean_sym}_disk_{idx}"),
                    text=text,
                    score=round(score, 4),
                    metadata=meta,
                )
            )

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]

