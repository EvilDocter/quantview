"""
QuantView Financial Knowledge Platform — Structural Semantic Chunker

Splits document text by logical document hierarchy (CEO Letter, Risk Factors,
Balance Sheet, MD&A, Auditor Notes) rather than arbitrary token boundaries.
"""

import re
import hashlib
import logging
from typing import List
from app.knowledge.models import DocumentChunk, ChunkMetadata, SectionType
from app.knowledge.parser import ParsedDocument
from app.knowledge.config import knowledge_settings

logger = logging.getLogger("knowledge_chunker")


class StructuralChunker:
    """Chunks documents using document hierarchy and financial section headers."""

    SECTION_PATTERNS = [
        (r"(?:letter to shareholders|ceo message|chairman|executive summary)", SectionType.CEO_LETTER),
        (r"(?:business overview|management discussion|md\&a|segment performance)", SectionType.BUSINESS_OVERVIEW),
        (r"(?:risk factors|key risks|threats|uncertainties)", SectionType.RISK_FACTORS),
        (r"(?:balance sheet|statement of financial position)", SectionType.BALANCE_SHEET),
        (r"(?:statement of profit|profit and loss|income statement)", SectionType.PROFIT_AND_LOSS),
        (r"(?:cash flow statement|statement of cash flows)", SectionType.CASH_FLOW),
        (r"(?:independent auditor|auditor's report|key audit matters)", SectionType.AUDITOR_REPORT),
        (r"(?:corporate governance|board of directors)", SectionType.CORPORATE_GOVERNANCE),
        (r"(?:esg|sustainability|business responsibility|brsr)", SectionType.ESG),
        (r"(?:notes to accounts|notes forming part of financial)", SectionType.NOTES_TO_ACCOUNTS),
    ]

    @staticmethod
    def chunk_parsed_document(
        doc: ParsedDocument, company: str, symbol: str, year: int, sha256_hash: str, doc_type: str = "Annual Report"
    ) -> List[DocumentChunk]:
        """Chunk document structural pages into semantic section chunks."""
        chunks: List[DocumentChunk] = []
        doc_id = f"doc_{symbol}_{year}_{sha256_hash[:8]}"

        logger.info(f"Chunking document for {symbol} ({year}) with {len(doc.pages)} pages...")

        current_section = SectionType.GENERAL
        current_heading = "General Content"
        chunk_idx = 0

        for page in doc.pages:
            # Detect section transitions
            for heading in page.headings:
                matched_sec = StructuralChunker._detect_section(heading)
                if matched_sec:
                    current_section = matched_sec
                    current_heading = heading

            text_blocks = StructuralChunker._split_into_paragraphs(page.text, max_chars=1800)

            for block in text_blocks:
                if len(block.strip()) < 50:
                    continue

                chunk_idx += 1
                chunk_id = f"{doc_id}_chunk_{chunk_idx:04d}"

                metadata = ChunkMetadata(
                    company=company,
                    symbol=symbol,
                    exchange="NSE",
                    year=year,
                    document_type=doc_type,
                    section=current_section,
                    heading=current_heading,
                    page_number=page.page_num,
                    chunk_index=chunk_idx,
                    source_file="raw.pdf",
                    sha256_hash=sha256_hash,
                )

                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=doc_id,
                    text=block.strip(),
                    metadata=metadata,
                    token_count=len(block.split()),
                )
                chunks.append(chunk)

        logger.info(f"Generated {len(chunks)} structural chunks for {symbol} ({year}).")
        return chunks

    @staticmethod
    def _detect_section(heading_text: str) -> SectionType:
        """Match heading against financial section regex patterns."""
        heading_lower = heading_text.lower()
        for pattern, section_type in StructuralChunker.SECTION_PATTERNS:
            if re.search(pattern, heading_lower):
                return section_type
        return SectionType.GENERAL

    @staticmethod
    def _split_into_paragraphs(text: str, max_chars: int = 1800) -> List[str]:
        """Split page text into paragraphs of up to max_chars."""
        raw_paragraphs = text.split("\n\n")
        blocks = []
        current_block = []
        current_len = 0

        for p in raw_paragraphs:
            p_clean = p.strip()
            if not p_clean:
                continue

            if current_len + len(p_clean) > max_chars and current_block:
                blocks.append("\n\n".join(current_block))
                current_block = [p_clean]
                current_len = len(p_clean)
            else:
                current_block.append(p_clean)
                current_len += len(p_clean)

        if current_block:
            blocks.append("\n\n".join(current_block))

        return blocks
