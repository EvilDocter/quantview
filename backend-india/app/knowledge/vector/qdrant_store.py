"""
QuantView Financial Knowledge Platform — Qdrant Vector Store Manager

Manages local Qdrant collections, vector indexing, payload metadata storage,
and HNSW similarity search on your intranet server (10.250.101.68:6333).
"""

import uuid
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models

from app.knowledge.config import knowledge_settings
from app.knowledge.models import DocumentChunk, SearchHit, ChunkMetadata, SectionType

logger = logging.getLogger("knowledge_vector")


class QdrantVectorStore:
    """Manages Qdrant vector collections and similarity search."""

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        self.host = host or knowledge_settings.qdrant_host
        self.port = port or knowledge_settings.qdrant_port
        self.collection_name = knowledge_settings.qdrant_collection_annual_reports
        self.vector_dim = knowledge_settings.embedding_dimension
        self._client: Optional[QdrantClient] = None

    def _ensure_client(self):
        """Initialize Qdrant client with automatic server / local path fallback."""
        if self._client is not None:
            return

        try:
            logger.info(f"Connecting to Qdrant server at http://{self.host}:{self.port}...")
            client = QdrantClient(host=self.host, port=self.port, timeout=5.0)
            client.get_collections()
            self._client = client
            logger.info("Successfully connected to Qdrant server.")
        except Exception as e:
            logger.warning(f"Failed to connect to Qdrant server at {self.host}:{self.port} ({e}). Falling back to local embedded Qdrant database...")
            local_path = knowledge_settings.qdrant_local_path
            local_path.mkdir(parents=True, exist_ok=True)
            self._client = QdrantClient(path=str(local_path))
            logger.info(f"Initialized local embedded Qdrant DB at {local_path}")

        self._ensure_collection(self.collection_name)

    def _ensure_collection(self, collection_name: str):
        """Create vector collection if it doesn't already exist."""
        collections = self._client.get_collections().collections
        existing_names = [c.name for c in collections]

        if collection_name not in existing_names:
            logger.info(f"Creating Qdrant collection: '{collection_name}' (dim={self.vector_dim})...")
            self._client.create_collection(
                collection_name=collection_name,
                vectors_config=rest_models.VectorParams(
                    size=self.vector_dim,
                    distance=rest_models.Distance.COSINE,
                ),
            )
            logger.info(f"Collection '{collection_name}' created.")

    def upsert_chunks(self, chunks: List[DocumentChunk]):
        """Upsert document chunks into Qdrant vector database."""
        if not chunks:
            return

        self._ensure_client()
        points = []

        for chunk in chunks:
            if not chunk.embedding:
                continue

            # Convert string ID to UUID v5 deterministically
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id))
            payload = {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "text": chunk.text,
                "token_count": chunk.token_count,
                "company": chunk.metadata.company,
                "symbol": chunk.metadata.symbol,
                "exchange": chunk.metadata.exchange,
                "year": chunk.metadata.year,
                "document_type": chunk.metadata.document_type,
                "section": chunk.metadata.section.value if hasattr(chunk.metadata.section, "value") else str(chunk.metadata.section),
                "heading": chunk.metadata.heading,
                "page_number": chunk.metadata.page_number,
                "chunk_index": chunk.metadata.chunk_index,
                "sha256_hash": chunk.metadata.sha256_hash,
            }

            points.append(rest_models.PointStruct(
                id=point_id,
                vector=chunk.embedding,
                payload=payload,
            ))

        logger.info(f"Upserting {len(points)} vector points into Qdrant collection '{self.collection_name}'...")
        self._client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        logger.info(f"Upsert complete for {len(points)} points.")

    def search_similar_vectors(
        self,
        query_vector: List[float],
        symbol: Optional[str] = None,
        year: Optional[int] = None,
        section: Optional[SectionType] = None,
        top_k: int = 5,
    ) -> List[SearchHit]:
        """Perform HNSW cosine vector similarity search with metadata filters."""
        self._ensure_client()

        # Build Qdrant filter conditions
        must_filters = []
        if symbol:
            must_filters.append(rest_models.FieldCondition(
                key="symbol",
                match=rest_models.MatchValue(value=symbol.upper()),
            ))
        if year:
            must_filters.append(rest_models.FieldCondition(
                key="year",
                match=rest_models.MatchValue(value=year),
            ))
        if section:
            sec_val = section.value if hasattr(section, "value") else str(section)
            must_filters.append(rest_models.FieldCondition(
                key="section",
                match=rest_models.MatchValue(value=sec_val),
            ))

        query_filter = rest_models.Filter(must=must_filters) if must_filters else None

        search_results = self._client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k,
        )

        hits: List[SearchHit] = []
        for res in search_results:
            p = res.payload or {}
            meta = ChunkMetadata(
                company=p.get("company", ""),
                symbol=p.get("symbol", ""),
                exchange=p.get("exchange", "NSE"),
                year=p.get("year", 2025),
                document_type=p.get("document_type", "Annual Report"),
                section=SectionType(p.get("section", SectionType.GENERAL.value)),
                heading=p.get("heading"),
                page_number=p.get("page_number", 1),
                chunk_index=p.get("chunk_index", 0),
                sha256_hash=p.get("sha256_hash", ""),
            )

            hits.append(SearchHit(
                chunk_id=p.get("chunk_id", str(res.id)),
                text=p.get("text", ""),
                score=float(res.score),
                metadata=meta,
            ))

        return hits
