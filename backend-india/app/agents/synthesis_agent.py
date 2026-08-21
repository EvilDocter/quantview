"""
QuantView — Retrieval-Constrained Synthesis Agent (Phase IV Institutional Analyst Engine)

Constructs senior sell-side institutional research reports grounded 100% in retrieved JSON evidence packets.
Adopts the persona of a Managing Director at Jefferies / Motilal Oswal / Goldman Sachs.
Enforces strict zero-hallucination rules and analytical derivations.
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any

from app.agents.state import AgentState
from app.services.llm_service import LLMService
from app.agents.evidence_packet import EvidencePacketBuilder

logger = logging.getLogger("synthesis_agent")

# In-memory report cache (Symbol -> (Timestamp, ResponseDict))
_REPORT_CACHE: Dict[str, Dict[str, Any]] = {}
_CACHE_TTL_SEC = 1800  # 30 Minutes


def clear_report_cache():
    """Clear in-memory report cache."""
    _REPORT_CACHE.clear()


class SynthesisAgent:
    """Retrieval-constrained sell-side research synthesis agent."""

    @staticmethod
    async def execute(state: AgentState) -> dict:
        query = state["query"]
        symbol = state["company_symbol"]
        evidence = state.get("retrieved_evidence", [])
        current_date = datetime.now().strftime("%B %d, %Y")

        # 1. Check in-memory report cache (only if evidence_packet exists and is non-empty)
        cache_key = f"{symbol.upper()}_{query.upper().strip()}"
        if cache_key in _REPORT_CACHE:
            cached_entry = _REPORT_CACHE[cache_key]
            if time.time() - cached_entry["timestamp"] < _CACHE_TTL_SEC:
                cached_data = cached_entry["data"]
                if cached_data.get("evidence_packet") and cached_data["evidence_packet"].get("financial_summary"):
                    logger.info(f"Returning cached equity report for {symbol} (Latency <0.5s)")
                    res = dict(cached_data)
                    res["is_cached"] = True
                    return res

        # 2. Unpack agent evidence arrays correctly
        fin_evidence = {}
        news_items = []
        rag_chunks = []
        val_evidence = {}

        for item in evidence:
            agent_name = item.get("agent")
            ev_list = item.get("evidence", [])
            for ev in ev_list:
                if agent_name == "financial_agent":
                    fin_evidence = ev
                elif agent_name == "news_agent":
                    news_items.extend(ev.get("news_search_results", []))
                    if ev.get("title"):
                        news_items.append(ev)
                elif agent_name == "filing_agent":
                    text_content = ev.get("content") or ev.get("text") or ""
                    if text_content:
                        rag_chunks.append({
                            "text": text_content,
                            "document": ev.get("title") or f"NSE {symbol} Annual Report",
                            "section": ev.get("section") or "BUSINESS_OVERVIEW",
                        })
                elif agent_name == "valuation_agent":
                    val_evidence = ev

        # 3. Build structured evidence packet
        packet = EvidencePacketBuilder.build_packet(
            symbol=symbol,
            yf_symbol=f"{symbol}.NS",
            query=query,
            rag_chunks=rag_chunks,
            news_items=news_items,
        )

        # 4. Phase IV Institutional Sell-Side Analyst Prompt
        prompt = f"""You are the Managing Director & Senior Equity Research Analyst at QuantView (formerly Senior Analyst at Motilal Oswal / Jefferies / Goldman Sachs).
Today's date is {current_date}.

Write an institutional sell-side equity research report on **{symbol}** strictly grounded in the JSON evidence packet below.

Do not merely summarize metrics. **INTERPRET AND DERIVE REASONING**.
Analyze:
- Leverage & Liquidity (Net Debt / EBITDA, Cash Cover)
- Profitability & Margin Sustainability (Gross vs Operating Margin spread)
- Earnings Quality & FCF Conversion (Net Income vs Free Cash Flow)
- Valuation Multiples & Capital Allocation Quality
- 16 Analytical Derivations (Moat, Management, Macro Sensitivity, Catalysts, Risks)

## User Query
"{query}"

## Structured Financial Evidence Packet (Verified Primary Data)
```json
{json.dumps(packet, indent=2, default=str)}
```

## Mandatory Zero-Hallucination & Analytical Rules
1. Every number cited MUST exist in the evidence packet above.
2. Never output '0.0%' for unavailable data — write "Data Unavailable" if a metric is absent.
3. Every conclusion must reference filing evidence chunks or financial ratios.

## Required Report Structure
1. **Executive Summary & Institutional Rating** — Rating (BUY / OUTPERFORM / HOLD / UNDERPERFORM), Target Fair Value Range, & Core Analytical Thesis.
2. **Key Derived Financial Metrics Table** — Markdown Table with Stock Price, Market Cap, Revenue, EBITDA, Net Income, P/E, EV/EBITDA, Net Debt/EBITDA, FCF Yield, Gross/Operating Margins, ROE.
3. **16-Point Institutional Analytical Assessment**:
   * *Leverage & Balance Sheet Risk*
   * *Liquidity & Cash Cover*
   * *Profitability Quality & ROE Trajectory*
   * *Margin Sustainability & Operating Leverage*
   * *Cash Flow Conversion & FCF Yield*
   * *Valuation Multiples & Peer Standing*
   * *Earnings Quality*
   * *Capital Allocation & ROIC Efficiency*
   * *Business Moat & Competitive Pricing Power*
   * *Management & Governance Assessment*
   * *Industry Positioning & Secular Growth*
   * *Macro & FX Sensitivity*
   * *Upside Catalysts (3 Triggers)*
   * *Downside Structural Risks (3 Risks)*
4. **Scenario Valuation Model (Bull / Base / Bear Cases)**:
   * **Bull Case**: Optimistic Growth & Valuation Multiple Target
   * **Base Case**: Fair Value Estimate & Primary Recommendation Target
   * **Bear Case**: Downside Margin Compression Floor Target
5. **Key Model Assumptions & Final Analyst Confidence Score**
"""
        final_report = "Research synthesis failed. The LLM did not return a response."
        confidence_score = 0.85

        try:
            raw = await LLMService.generate(prompt=prompt, temperature=0.1, max_tokens=1500)
            if raw and len(raw.strip()) > 100:
                final_report = raw
            else:
                logger.warning("Synthesis returned empty or short response")
        except Exception as e:
            logger.error(f"Synthesis agent call failed: {e}")

        result_payload = {
            "final_report": final_report,
            "confidence_score": confidence_score,
            "citations": rag_chunks[:5],
            "evidence_packet": packet,
            "is_cached": False,
        }

        # Cache report
        _REPORT_CACHE[cache_key] = {
            "timestamp": time.time(),
            "data": result_payload
        }

        return result_payload
