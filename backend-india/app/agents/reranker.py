"""
QuantView — Hybrid RAG Reranker & Section Classifier (Phase 3 & Phase 4 Mandate)

Classifies RAG chunks by financial section and reranks them based on query relevance.
Filters out non-material administrative boilerplate (AGM notices, proxy forms, e-voting instructions).
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger("reranker")

# Section keywords & priority weights
SECTION_PATTERNS = {
    "FINANCIAL_HIGHLIGHTS": (re.compile(r'financial highlights|revenue|net profit|ebitda|margin|balance sheet|cash flow', re.I), 1.0),
    "SEGMENT_PERFORMANCE": (re.compile(r'segment|business segment|oil & gas|retail|jio|defense|aerospace|automobile|pharma', re.I), 0.95),
    "BUSINESS_OVERVIEW": (re.compile(r'business overview|company profile|operations|products|services|market share', re.I), 0.9),
    "RISK_FACTORS": (re.compile(r'risk factors|risks|uncertainties|regulatory risk|competition|foreign exchange risk', re.I), 0.85),
    "CAPITAL_ALLOCATION": (re.compile(r'capital allocation|capex|debt reduction|dividend|share buyback|borrowings', re.I), 0.85),
    "OUTLOOK_STRATEGY": (re.compile(r'outlook|future strategy|growth drivers|expansion|pipeline|guidance', re.I), 0.9),
    "GOVERNANCE": (re.compile(r'board of directors|audit committee|corporate governance|auditor report', re.I), 0.5),
    "ADMINISTRATIVE": (re.compile(r'notice of annual general meeting|agm notice|proxy form|e-voting|cin:|telefax|maker chambers|videoconferencing', re.I), 0.05),
}


class ChunkReranker:
    """Hybrid search and section-aware reranker for RAG chunks."""

    @staticmethod
    def classify_section(text: str) -> tuple:
        """Classify chunk section and return (section_name, weight)."""
        best_section = "GENERAL"
        best_weight = 0.7

        for sec_name, (pattern, weight) in SECTION_PATTERNS.items():
            if pattern.search(text):
                if weight < best_weight if sec_name == "ADMINISTRATIVE" else weight > best_weight:
                    best_section = sec_name
                    best_weight = weight
                    if sec_name == "ADMINISTRATIVE":
                        break

        return best_section, best_weight

    @staticmethod
    def rerank_chunks(chunks: List[Dict[str, Any]], query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Rerank RAG chunks using section priority, keyword matching, and administrative filtering.
        """
        query_terms = set(re.findall(r'\w+', query.lower()))
        scored_chunks = []

        for chunk in chunks:
            text = chunk.get("text", "")
            if not text or len(text.strip()) < 30:
                continue

            section_name, section_weight = ChunkReranker.classify_section(text)
            
            # Penalize administrative chunks heavily
            if section_name == "ADMINISTRATIVE":
                continue

            # Term overlap score
            text_terms = set(re.findall(r'\w+', text.lower()))
            overlap = len(query_terms.intersection(text_terms))
            overlap_score = overlap / (len(query_terms) + 1e-5)

            # Total score
            final_score = (overlap_score * 0.4) + (section_weight * 0.6)

            scored_chunk = dict(chunk)
            scored_chunk["section"] = section_name
            scored_chunk["relevance_score"] = round(final_score, 4)
            scored_chunks.append(scored_chunk)

        # Sort by relevance_score descending
        scored_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_chunks[:top_k]
