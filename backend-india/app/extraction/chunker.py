"""
QuantView — Document Chunking Service

Segments large financial documents into semantically coherent blocks
ready for vector embeddings and Qdrant ingestion.
"""

import logging

logger = logging.getLogger("chunker")

class DocumentChunker:
    """Splits raw text strings into overlapping chunks based on character/token count."""

    @staticmethod
    def split_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
        """
        Splits text using a sliding window.
        Assumes tokenized strings approximate length using whitespace splitting.
        """
        if not text:
            return []

        words = text.split()
        chunks = []
        
        i = 0
        while i < len(words):
            chunk_words = words[i : i + chunk_size]
            chunk_text = " ".join(chunk_words)
            chunks.append(chunk_text)
            i += (chunk_size - overlap)
            
        return chunks
