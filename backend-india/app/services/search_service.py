"""
QuantView — Hybrid Search Fusion Service

Combines Qdrant vector semantic results with OpenSearch keyword results
using Reciprocal Rank Fusion (RRF) to serve highly accurate context to research agents.
"""

import logging
from collections import defaultdict
from typing import Optional

from app.db.qdrant import search_vectors
from app.db.opensearch import search_documents
from app.extraction.embedding_generator import EmbeddingGenerator

logger = logging.getLogger("search_service")

class SearchService:
    """Executes multi-database search queries and fuses results using RRF ranking."""

    @staticmethod
    def reciprocal_rank_fusion(
        vector_results: list[dict],
        keyword_results: list[dict],
        k: int = 60
    ) -> list[dict]:
        """
        Calculates fusion scoring: score = sum( 1 / (k + rank) )
        Normalizes outputs to a unified search ranking.
        """
        scores = defaultdict(float)
        docs = {}

        # Process Vector Results
        for rank, item in enumerate(vector_results):
            doc_id = item.get("id")
            scores[doc_id] += 1.0 / (k + rank + 1)
            docs[doc_id] = item

        # Process Keyword Results
        for rank, item in enumerate(keyword_results):
            doc_id = item.get("_id")
            scores[doc_id] += 1.0 / (k + rank + 1)
            # Retain detail payload if not already added
            if doc_id not in docs:
                docs[doc_id] = {
                    "id": doc_id,
                    "payload": item
                }

        # Sort based on combined score
        sorted_keys = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        return [docs[key] for key in sorted_keys]

    @classmethod
    async def hybrid_search(
        cls,
        query: str,
        company_id: Optional[int] = None,
        company_symbol: Optional[str] = None,
        limit: int = 10
    ) -> list[dict]:
        """Runs vector and keyword queries concurrently and merges them."""
        # 1. Generate Embeddings
        query_vectors = await EmbeddingGenerator.generate_embeddings([query])
        query_vector = query_vectors[0] if query_vectors else [0.0] * 1024

        # 2. Query Qdrant Vector DB
        try:
            vector_res = await search_vectors(
                query_vector=query_vector,
                limit=limit,
                company_id=company_id
            )
            # Map Qdrant models to simple dict representation
            vector_items = [
                {"id": hit.id, "payload": hit.payload, "score": hit.score}
                for hit in vector_res
            ]
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            vector_items = []

        # 3. Query OpenSearch Index
        try:
            keyword_items = search_documents(
                query=query,
                company_symbol=company_symbol,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            keyword_items = []

        # 4. Perform Fusion
        return cls.reciprocal_rank_fusion(vector_items, keyword_items)
