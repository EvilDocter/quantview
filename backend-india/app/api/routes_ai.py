"""
QuantView — AI Research API Routes

Endpoints for AI-powered research, analysis, comparison,
screening, daily intelligence, and research history.
"""

import time
import logging
import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.core.schemas import ResearchRequest, ResearchResponse
from app.agents.orchestrator import build_workflow

router = APIRouter()
logger = logging.getLogger("routes_ai")

# Symbol detection map
SYMBOL_MAP = {
    "RELIANCE": "RELIANCE",
    "INFOSYS": "INFY",
    "INFY": "INFY",
    "TCS": "TCS",
    "HDFC": "HDFCBANK",
    "HDFCBANK": "HDFCBANK",
    "TATA MOTORS": "TATAMOTORS",
    "TATAMOTORS": "TATAMOTORS",
    "TATA": "TATAMOTORS",
    "BHARTI": "BHARTIARTL",
    "AIRTEL": "BHARTIARTL",
    "ICICI": "ICICIBANK",
    "ICICIBANK": "ICICIBANK",
    "WIPRO": "WIPRO",
    "SBI": "SBIN",
    "SBIN": "SBIN",
    "BAJAJ": "BAJFINANCE",
    "MARUTI": "MARUTI",
    "ITC": "ITC",
    "LT": "LT",
    "LARSEN": "LT",
    "KOTAK": "KOTAKBANK",
    "AXIS": "AXISBANK",
    "AXISBANK": "AXISBANK",
    "SUNPHARMA": "SUNPHARMA",
    "TITAN": "TITAN",
    "ASIAN PAINTS": "ASIANPAINT",
    "ULTRATECH": "ULTRACEMCO",
    "NESTLE": "NESTLEIND",
    "ADANI": "ADANIENT",
}


def detect_symbol(query: str) -> str:
    """Extract the most likely company symbol from a natural-language query."""
    query_upper = query.upper()
    for keyword, ticker in SYMBOL_MAP.items():
        if keyword in query_upper:
            return ticker
    return "NIFTY50"


@router.post("/research", response_model=ResearchResponse)
async def submit_research_query(
    request: ResearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a research query to the AI agent system.
    The planner routes to specialist agents, which scrape live data,
    then the synthesis agent produces a cited report via Gemini.
    """
    start_time = time.time()
    query = request.query
    detected_symbol = detect_symbol(query)

    initial_state = {
        "query": query,
        "company_symbol": detected_symbol,
        "plan": [],
        "current_step": 0,
        "retrieved_evidence": [],
        "final_report": "",
        "confidence_score": 0.0,
        "citations": [],
    }

    try:
        workflow = build_workflow()
        result = await workflow.ainvoke(initial_state)
        processing_time = int((time.time() - start_time) * 1000)

        # Extract fields safely
        confidence = 0.85
        try:
            confidence = float(result.get("confidence_score", 0.85))
        except (ValueError, TypeError):
            pass

        final_answer = str(result.get("final_report", ""))
        if not final_answer or len(final_answer.strip()) < 50:
            final_answer = "The AI pipeline completed but did not generate a meaningful report. Please try again."

        agents_used = result.get("plan", [])
        if not isinstance(agents_used, list):
            agents_used = []
        agents_used = [str(a) for a in agents_used]

        return ResearchResponse(
            query=query,
            answer=final_answer,
            confidence=confidence,
            citations=[],
            agents_used=agents_used,
            processing_time_ms=processing_time,
        )

    except Exception as e:
        logger.error(f"AI pipeline failed: {e}")
        logger.error(traceback.format_exc())
        processing_time = int((time.time() - start_time) * 1000)
        return ResearchResponse(
            query=query,
            answer=f"**Error:** The AI research pipeline encountered an error: `{str(e)}`. Please try again.",
            confidence=0.0,
            citations=[],
            agents_used=[],
            processing_time_ms=processing_time,
        )


@router.post("/compare")
async def compare_companies(
    symbols: list[str],
    db: AsyncSession = Depends(get_db),
):
    """Compare two or more companies using AI analysis and live financial data."""
    if not symbols or len(symbols) < 2:
        return {"symbols": symbols, "comparison": "Please provide at least 2 stock symbols to compare."}
    
    sym1 = detect_symbol(symbols[0])
    sym2 = detect_symbol(symbols[1])
    
    try:
        from app.services.llm_service import LLMService
        from datetime import datetime
        current_date = datetime.now().strftime("%B %d, %Y")
        
        prompt = f"""You are the Lead Financial Analyst at QuantView.
Today's date is {current_date}.

Compare the following two Indian equities for an investor:
1. **{sym1}**
2. **{sym2}**

Write a detailed, structured comparison report in Markdown:
1. **Executive Summary & Verdict** — Which stock is a better buy right now and why?
2. **Business Model & Market Position** — Compare key revenue drivers.
3. **Valuation & Financial Comparison** — Compare typical PE ratios, growth, and margins.
4. **Risk Profile** — Key risks for each company.
5. **Final Recommendation** — Clear preference based on investor risk profile (Growth vs Value vs Income).
"""
        comparison_text = await LLMService.generate(prompt=prompt, temperature=0.3, max_tokens=3000)
        return {
            "symbols": [sym1, sym2],
            "comparison": comparison_text or f"Failed to generate comparison for {sym1} vs {sym2}."
        }
    except Exception as e:
        logger.error(f"Compare failed: {e}")
        return {"symbols": symbols, "comparison": f"Error comparing companies: {str(e)}"}


@router.post("/screen")
async def ai_screen(query: str, db: AsyncSession = Depends(get_db)):
    """Natural language stock screening."""
    return {"query": query, "results": []}


@router.get("/daily-intelligence")
async def get_daily_intelligence():
    """Get today's AI-generated market intelligence report."""
    return {"intelligence": "Daily intelligence report coming soon"}


@router.get("/trending")
async def get_trending_research():
    """Get trending research topics and queries."""
    return {"trending": []}


@router.get("/history")
async def get_research_history(
    user_id: str = "anonymous",
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Get user's research query history."""
    return {"history": []}
