"""
QuantView — Structured Evidence Packet Builder (Phase 5 Mandate)

Assembles standardized institutional evidence JSON before LLM inference.
Combines dynamic financial profile, high-signal RAG filing sections, news, and peer context.
"""

import json
import logging
from typing import Dict, Any, List
from app.services.financial_extractor import FinancialExtractorService
from app.agents.reranker import ChunkReranker

logger = logging.getLogger("evidence_packet")


class EvidencePacketBuilder:
    """Assembles structured financial evidence JSON for any Indian company."""

    @staticmethod
    def build_packet(
        symbol: str,
        yf_symbol: str,
        query: str,
        rag_chunks: List[Dict[str, Any]],
        news_items: List[Dict[str, Any]],
        peer_symbols: List[str] = None
    ) -> Dict[str, Any]:
        """
        Build standardized evidence packet payload.
        """
        # 1. Extract dynamic financial profile
        profile = FinancialExtractorService.extract_full_financial_profile(symbol, yf_symbol)

        # 2. Rerank and filter RAG chunks
        reranked_chunks = ChunkReranker.rerank_chunks(rag_chunks, query, top_k=5)

        # 3. Process news
        formatted_news = []
        for n in news_items[:5]:
            formatted_news.append({
                "title": n.get("title", ""),
                "publisher": n.get("publisher") or n.get("source", "Market News"),
                "snippet": n.get("content") or n.get("snippet", ""),
                "url": n.get("url", ""),
            })

        # 4. Process peer comparisons if provided
        peer_profiles = []
        if peer_symbols:
            for psym in peer_symbols[:3]:
                if psym != symbol:
                    try:
                        p_profile = FinancialExtractorService.extract_full_financial_profile(psym)
                        peer_profiles.append({
                            "symbol": p_profile["company_identity"]["symbol"],
                            "company_name": p_profile["company_identity"]["company_name"],
                            "market_cap": p_profile["valuation_metrics"]["market_cap"],
                            "revenue": p_profile["income_statement"]["revenue"],
                            "pe_ratio": p_profile["valuation_metrics"]["pe_ratio"],
                            "roe_pct": p_profile["valuation_metrics"]["roe_pct"],
                        })
                    except Exception as e:
                        logger.warning(f"Failed extracting peer profile for {psym}: {e}")

        # 5. Assemble packet
        packet = {
            "company_identity": profile["company_identity"],
            "market_data": profile["market_data"],
            "financial_summary": {
                "currency": profile["company_identity"]["currency"],
                "market_cap_inr": profile["valuation_metrics"]["market_cap"],
                "revenue_inr": profile["income_statement"]["revenue"],
                "net_income_inr": profile["income_statement"]["net_income"],
                "pe_ratio": profile["valuation_metrics"]["pe_ratio"],
                "roe_pct": profile["valuation_metrics"]["roe_pct"],
            },
            "income_statement": profile["income_statement"],
            "balance_sheet": profile["balance_sheet"],
            "cash_flow": profile["cash_flow"],
            "valuation_metrics": profile["valuation_metrics"],
            "growth_metrics": profile["growth_metrics"],
            "ownership_data": {
                "promoter_holding_pct": "N/A",
                "fii_holding_pct": "N/A",
                "dii_holding_pct": "N/A",
            },
            "recent_news": formatted_news,
            "relevant_filing_sections": reranked_chunks,
            "macro_context": {
                "country": "India",
                "exchange": "NSE / BSE",
                "benchmark_index": "NIFTY 50",
            },
            "peer_comparison": peer_profiles,
        }

        return packet
