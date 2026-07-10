"""
QuantView — Vector Embedding Generator Service

Proxies embedding requests to the AI Model Server to convert document chunks
into high-dimensional vectors (BGE-large-en-v1.5) for Qdrant ingestion.
"""

import httpx
import logging
from app.config import get_settings

logger = logging.getLogger("embedding_generator")
settings = get_settings()

class EmbeddingGenerator:
    """Sends list of texts to the AI Model Server to generate vector embeddings."""

    @staticmethod
    async def generate_embeddings(texts: list[str]) -> list[list[float]]:
        """Invokes AI server `/embeddings` endpoint to fetch vector weights."""
        if not texts:
            return []

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.ai_server_url}/embeddings",
                    json={"texts": texts}
                )
                if response.status_code == 200:
                    return response.json().get("embeddings", [])
        except Exception as e:
            logger.error(f"Embedding request failed: {e}")
            
        # Fallback empty vectors stub if server is offline
        # Size matches BGE-large (1024 dims)
        return [[0.0] * settings.qdrant_embedding_dim for _ in texts]
