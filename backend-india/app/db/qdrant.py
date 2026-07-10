"""
QuantView — Qdrant Vector Database Connection

Client for Qdrant Cloud free tier — handles collection creation,
vector upsert, and semantic search.
"""

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
)
from typing import Optional
from app.config import get_settings

settings = get_settings()

# ── Qdrant Client ────────────────────────────────────────────────
qdrant_client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key,
    timeout=30,
)


def init_qdrant_collection():
    """Create the document embeddings collection if it doesn't exist."""
    collections = qdrant_client.get_collections().collections
    collection_names = [c.name for c in collections]

    if settings.qdrant_collection not in collection_names:
        qdrant_client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(
                size=settings.qdrant_embedding_dim,
                distance=Distance.COSINE,
            ),
        )
        print(f"✅ Created Qdrant collection: {settings.qdrant_collection}")
    else:
        print(f"✅ Qdrant collection already exists: {settings.qdrant_collection}")


async def upsert_vectors(
    points: list[PointStruct],
    batch_size: int = 100,
):
    """Upsert vectors in batches to Qdrant."""
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        qdrant_client.upsert(
            collection_name=settings.qdrant_collection,
            points=batch,
        )


async def search_vectors(
    query_vector: list[float],
    limit: int = 10,
    company_id: Optional[int] = None,
    document_type: Optional[str] = None,
) -> list:
    """
    Semantic search over document embeddings.
    Optionally filter by company_id or document_type.
    """
    filters = []
    if company_id is not None:
        filters.append(
            FieldCondition(key="company_id", match=MatchValue(value=company_id))
        )
    if document_type is not None:
        filters.append(
            FieldCondition(key="document_type", match=MatchValue(value=document_type))
        )

    search_filter = Filter(must=filters) if filters else None

    results = qdrant_client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_vector,
        limit=limit,
        query_filter=search_filter,
        with_payload=True,
    )

    return results
