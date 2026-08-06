"""
QuantView — Synthesis Agent

Aggregates all retrieved evidence and broker portfolio context to produce
a structured, cited investment research or portfolio intelligence report.
"""

import logging
import json
from datetime import datetime
from app.agents.state import AgentState
from app.services.llm_service import LLMService
from app.broker_gateway.drivers.factory import BrokerFactory
from app.broker_gateway.schemas.normalized import BrokerCode
from app.broker_gateway.core.intelligence import PortfolioIntelligenceEngine

logger = logging.getLogger("synthesis_agent")


class SynthesisAgent:
    """Consolidates evidence arrays and broker portfolio context to generate final reports."""

    @staticmethod
    async def execute(state: AgentState) -> dict:
        query = state["query"]
        symbol = state["company_symbol"]
        evidence = state["retrieved_evidence"]
        current_date = datetime.now().strftime("%B %d, %Y")

        # Check if query is asking for portfolio analysis
        query_lower = query.lower()
        portfolio_context = None

        if any(k in query_lower for k in ["portfolio", "my holding", "my stock", "my zerodha", "my angel", "health score", "beta"]):
            try:
                driver = BrokerFactory.get_driver(
                    broker_code=BrokerCode.ZERODHA,
                    connection_id="conn_zerodha_01",
                    account_id="CLIENT_UCC",
                    access_token="MOCK_ACCESS_TOKEN",
                    api_key="MOCK_API_KEY"
                )
                p = await driver.get_full_portfolio()
                intel = PortfolioIntelligenceEngine.analyze_portfolio(p)
                portfolio_context = {
                    "account": p.account_id,
                    "total_investment": float(p.total_investment),
                    "current_value": float(p.total_current_value),
                    "total_pnl": float(p.total_pnl),
                    "pnl_pct": float(p.total_pnl_percentage),
                    "intelligence": intel,
                    "holdings": [
                        {
                            "symbol": h.trading_symbol,
                            "qty": h.quantity,
                            "avg_price": float(h.average_price),
                            "current_price": float(h.current_price),
                            "pnl": float(h.pnl)
                        } for h in p.holdings
                    ]
                }
            except Exception as e:
                logger.warning(f"Failed to load broker portfolio context for query: {e}")

        portfolio_prompt_block = ""
        if portfolio_context:
            portfolio_prompt_block = f"""
## User Connected Broker Portfolio (Live Normalized Context)
{json.dumps(portfolio_context, indent=2)}
"""

        prompt = f"""You are the Lead Financial Analyst at QuantView, an AI-powered equity research platform.
Today's date is {current_date}.

Write a comprehensive investment research report on **{symbol}** based on the user's query, the real-time evidence data, and the user's connected broker portfolio (if relevant).

## User Query
"{query}"
{portfolio_prompt_block}
## Retrieved Evidence (from live web scraping and financial APIs)
{json.dumps(evidence, indent=2, default=str)}

## Report Structure (follow this exactly)
1. **Executive Summary** — 2-3 sentence verdict with a clear recommendation (Buy / Hold / Sell / Avoid) and a confidence level. Include portfolio impact if user's portfolio context is provided.
2. **Key Financial Metrics** — Present the actual numbers from the evidence in a markdown table (Revenue, Net Profit, EBITDA, PE Ratio, EPS, Current Price, Debt-to-Equity). If a metric is 0 or missing, say "Data unavailable" instead of showing 0.
3. **Recent News & Sentiment** — Summarize the scraped news articles. Cite the article titles and publishers.
4. **Corporate Profile & Filings** — Summarize any filing or annual report data from the evidence.
5. **Valuation Assessment** — Analyze the PE ratio, EPS, and price-to-book from the evidence. Compare to typical sector averages.
6. **Risk Factors** — List 3-5 specific risks based on the evidence and your knowledge.
7. **Investment Recommendation** — Final verdict with reasoning.

## Rules
- Use ONLY the data provided in the evidence and portfolio context above. Do NOT invent numbers.
- If evidence is missing or empty for a section, state "Insufficient data retrieved" honestly.
- Cite sources inline with page numbers: [Source: QuantView Knowledge RAG (NSE INFY 2026 Annual Report, Page 48)], [Source: financial_agent], [Source: broker_gateway], etc.
- Use markdown formatting with headers, bold, and tables.
- Be specific and quantitative wherever possible.
"""
        final_report = "Research synthesis failed. The LLM did not return a response."
        confidence_score = 0.5

        try:
            raw = await LLMService.generate(
                prompt=prompt, temperature=0.3, max_tokens=4000
            )
            if raw and len(raw.strip()) > 50:
                final_report = raw
                confidence_score = 0.85
            else:
                logger.warning("Synthesis returned empty or trivial response")
        except Exception as e:
            logger.error(f"Synthesis agent call failed: {e}")

        return {
            "final_report": final_report,
            "confidence_score": confidence_score,
            "citations": evidence,
        }
