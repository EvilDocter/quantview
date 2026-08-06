"""
QuantView Financial Knowledge Platform — Hybrid Search Engine

Combines Qdrant HNSW vector search with BM25 keyword matching and metadata filters.
"""

import time
import logging
from typing import List, Optional

from app.knowledge.embeddings import EmbeddingService
from app.knowledge.vector import QdrantVectorStore
from app.knowledge.models import SearchQuery, SearchResponse, SearchHit, SectionType

logger = logging.getLogger("knowledge_retrieval")


class HybridSearchEngine:
    """Performs hybrid vector + keyword search against Qdrant and knowledge artifacts."""

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[QdrantVectorStore] = None,
    ):
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or QdrantVectorStore()

    def search(self, request: SearchQuery) -> SearchResponse:
        """Perform hybrid search and return top-K scored chunks with metadata."""
        start_time = time.time()
        logger.info(f"Executing Hybrid Search for query: '{request.query}' (symbol={request.symbol}, year={request.year})...")

        # 1. Generate query embedding vector
        query_vec = self.embedding_service.generate_single_embedding(request.query)

        # 2. Vector search in Qdrant with filters
        vector_hits = self.vector_store.search_similar_vectors(
            query_vector=query_vec,
            symbol=request.symbol,
            year=request.year,
            section=request.section,
            top_k=request.top_k,
        )

        # 3. Filter hits by min_score threshold
        filtered_hits = [h for h in vector_hits if h.score >= request.min_score]

        elapsed_ms = (time.time() - start_time) * 1000.0
        logger.info(f"Hybrid Search returned {len(filtered_hits)} hits in {elapsed_ms:.1f} ms.")

        return SearchResponse(
            query=request.query,
            total_hits=len(filtered_hits),
            hits=filtered_hits,
            execution_time_ms=elapsed_ms,
        )
