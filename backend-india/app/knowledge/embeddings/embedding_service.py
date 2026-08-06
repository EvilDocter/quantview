"""
QuantView Financial Knowledge Platform — Local Embedding Generator

Generates 1024-dimensional dense vector embeddings for financial text chunks
using BAAI/bge-large-en-v1.5 with batch acceleration support.
"""

import logging
from typing import List
from app.knowledge.config import knowledge_settings
from app.knowledge.models import DocumentChunk

logger = logging.getLogger("knowledge_embeddings")


class EmbeddingService:
    """Generates 1024-dimensional embeddings using local BAAI/bge-large-en-v1.5 model."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or knowledge_settings.embedding_model_name
        self.dimension = knowledge_settings.embedding_dimension
        self._model = None

    def _ensure_model(self):
        """Lazy load fastembed or sentence-transformers model."""
        if self._model is not None:
            return

        try:
            from fastembed import TextEmbedding
            logger.info(f"Loading FastEmbed model: {self.model_name}...")
            self._model = TextEmbedding(model_name=self.model_name)
            logger.info("FastEmbed model loaded successfully.")
        except Exception as e:
            logger.warning(f"FastEmbed load failed ({e}). Falling back to SentenceTransformers...")
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                logger.info("SentenceTransformers model loaded successfully.")
            except Exception as e2:
                logger.error(f"Failed to load embedding model: {e2}")
                raise RuntimeError(f"Embedding model failure: {e2}")

    def generate_chunk_embeddings(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Generate and attach 1024-dimensional vector embeddings to each DocumentChunk."""
        if not chunks:
            return chunks

        self._ensure_model()
        texts = [c.text for c in chunks]
        logger.info(f"Generating embeddings for {len(chunks)} chunks using {self.model_name}...")

        try:
            if hasattr(self._model, "embed"):
                # FastEmbed generator interface
                embeddings_gen = list(self._model.embed(texts))
                for chunk, emb in zip(chunks, embeddings_gen):
                    chunk.embedding = list(emb)
            else:
                # SentenceTransformers interface
                embeddings_arr = self._model.encode(texts, batch_size=32, show_progress_bar=False)
                for chunk, emb in zip(chunks, embeddings_arr):
                    chunk.embedding = emb.tolist()

            logger.info(f"Successfully generated embeddings for {len(chunks)} chunks.")
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

        return chunks

    def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for a single query string."""
        from app.knowledge.models import ChunkMetadata, SectionType
        dummy_meta = ChunkMetadata(
            company="Query",
            symbol="QUERY",
            exchange="NSE",
            year=2025,
            document_type="Query",
            section=SectionType.GENERAL,
            sha256_hash="queryhash",
        )
        dummy_chunk = DocumentChunk(
            chunk_id="query",
            document_id="query",
            text=text,
            metadata=dummy_meta,
        )
        res = self.generate_chunk_embeddings([dummy_chunk])
        return res[0].embedding or [0.0] * self.dimension
