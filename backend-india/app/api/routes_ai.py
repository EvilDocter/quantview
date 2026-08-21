"""
QuantView — AI Research API Routes

Endpoints for AI-powered research, analysis, comparison,
screening, daily intelligence, and self-growing pipeline debugging using Qwen model engine.
"""

import time
import logging
import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.core.schemas import ResearchRequest, ResearchResponse
from app.agents.orchestrator import build_workflow
from app.services.symbol_resolver import SymbolResolverService
from app.agents.verification_engine import VerificationEngine
from app.services.dynamic_indexer import DynamicIndexerPipeline
from app.services.company_registry import CompanyRegistryService
from app.agents.evidence_packet import EvidencePacketBuilder
from app.agents.synthesis_agent import clear_report_cache

router = APIRouter()
logger = logging.getLogger("routes_ai")


def detect_symbol(query: str) -> str:
    """Extract the company symbol dynamically from user query string."""
    res = SymbolResolverService.resolve_symbol(query)
    return res.get("symbol", "RELIANCE")


@router.get("/debug/evidence/{symbol}")
async def debug_evidence_pipeline(symbol: str):
    """
    Debug Endpoint: Returns full self-growing pipeline visibility for any symbol:
    resolved_ticker, canonical_registry, cache_status, evidence_packet, generated_report, verification_table, latency_breakdown.
    """
    start_time = time.time()
    clear_report_cache()  # Force fresh evidence evaluation for debug calls

    resolved = SymbolResolverService.resolve_symbol(symbol)
    resolved_symbol = resolved["symbol"]
    yf_symbol = resolved["yf_symbol"]

    # 1. Ensure company is indexed dynamically
    indexing_res = await DynamicIndexerPipeline.ensure_indexed(resolved_symbol)
    registry_record = CompanyRegistryService.get_company_record(resolved_symbol)

    # 2. Execute research workflow
    initial_state = {
        "query": f"Analyze {resolved_symbol}",
        "company_symbol": resolved_symbol,
        "plan": ["financial_agent", "news_agent", "filing_agent", "valuation_agent"],
        "current_step": 0,
        "retrieved_evidence": [],
        "final_report": "",
        "confidence_score": 0.0,
        "citations": [],
    }

    workflow = build_workflow()
    result = await workflow.ainvoke(initial_state)
    total_latency = round(time.time() - start_time, 3)

    evidence_packet = result.get("evidence_packet")
    citations = result.get("citations", [])

    # If packet missing or empty, build dynamically
    if not evidence_packet or not evidence_packet.get("financial_summary"):
        clear_report_cache()
        evidence_packet = EvidencePacketBuilder.build_packet(
            symbol=resolved_symbol,
            yf_symbol=yf_symbol,
            query=f"Analyze {resolved_symbol}",
            rag_chunks=citations,
            news_items=[],
        )

    final_report = result.get("final_report", "")

    # 3. Run audit against populated evidence packet
    audit_res = VerificationEngine.audit_report(final_report, evidence_packet)

    return {
        "symbol_query": symbol,
        "resolved_symbol": resolved_symbol,
        "yf_symbol": yf_symbol,
        "company_name": resolved.get("company_name"),
        "canonical_registry": registry_record,
        "indexing_status": indexing_res,
        "evidence_packet": evidence_packet,
        "retrieved_chunks_count": max(len(citations), len(evidence_packet.get("relevant_filing_sections", []))),
        "generated_report": final_report,
        "fact_verification": {
            "total_claims": audit_res["total_claims"],
            "grounded_claims": audit_res["grounded_claims"],
            "hallucination_rate_pct": audit_res["hallucination_rate_pct"],
            "verification_table": audit_res["verification_table"],
        },
        "latency_breakdown": {
            "total_latency_sec": total_latency,
            "is_cached": result.get("is_cached", False),
        }
    }


@router.post("/research", response_model=ResearchResponse)
async def submit_research_query(
    request: ResearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a research query to the AI agent system.
    Dynamically indexes company on first sight and triggers background peer prefetching.
    """
    start_time = time.time()
    query = request.query
    detected_symbol = detect_symbol(query)

    # Ensure company is dynamically indexed on first query
    await DynamicIndexerPipeline.ensure_indexed(detected_symbol)

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

        confidence = float(result.get("confidence_score", 0.85))
        final_answer = str(result.get("final_report", ""))
        evidence_packet = result.get("evidence_packet", {})

        # If packet missing or empty, build dynamically
        if not evidence_packet or not evidence_packet.get("financial_summary"):
            resolved = SymbolResolverService.resolve_symbol(detected_symbol)
            evidence_packet = EvidencePacketBuilder.build_packet(
                symbol=detected_symbol,
                yf_symbol=resolved["yf_symbol"],
                query=query,
                rag_chunks=result.get("citations", []),
                news_items=[],
            )

        # Run Verification Engine audit
        audit_res = VerificationEngine.audit_report(final_answer, evidence_packet)

        # Append Verification Table to report answer
        if audit_res.get("verification_table"):
            table_md = "\n\n### Numerical Fact-Verification Audit (Phase 8 Mandate)\n"
            table_md += f"* **Total Claims Audited**: {audit_res['total_claims']} | **Grounded Claims**: {audit_res['grounded_claims']} | **Hallucination Rate**: {audit_res['hallucination_rate_pct']}%\n\n"
            table_md += "| Claim Extracted | Ground Truth Source | Status | Confidence |\n|---|---|---|---|\n"
            for row in audit_res["verification_table"][:10]:
                table_md += f"| `{row['claim']}` | {row['source']} | **{row['match']}** | {row['confidence']} |\n"
            final_answer += table_md

        agents_used = [str(a) for a in result.get("plan", [])]

        return ResearchResponse(
            query=query,
            answer=final_answer,
            confidence=confidence,
            citations=[],
            agents_used=agents_used,
            processing_time_ms=processing_time,
        )

    except Exception as e:
        logger.error(f"AI pipeline failed for query '{query}': {e}")
        logger.error(traceback.format_exc())
        processing_time = int((time.time() - start_time) * 1000)
        return ResearchResponse(
            query=query,
            answer=f"**Error:** The AI research pipeline encountered an error: `{str(e)}`.",
            confidence=0.0,
            citations=[],
            agents_used=[],
            processing_time_ms=processing_time,
        )


@router.post("/compare")
async def compare_companies(symbols: list[str], db: AsyncSession = Depends(get_db)):
    if not symbols or len(symbols) < 2:
        return {"symbols": symbols, "comparison": "Please provide at least 2 stock symbols to compare."}
    sym1 = detect_symbol(symbols[0])
    sym2 = detect_symbol(symbols[1])

    # Dynamic indexing for both comparison candidates
    await DynamicIndexerPipeline.ensure_indexed(sym1)
    await DynamicIndexerPipeline.ensure_indexed(sym2)

    try:
        from app.services.llm_service import LLMService
        from datetime import datetime
        current_date = datetime.now().strftime("%B %d, %Y")
        prompt = f"""Compare Indian equities {sym1} vs {sym2} on {current_date}. Provide Executive Summary, Valuation Comparison, Financial Comparison, and Recommendation."""
        comparison_text = await LLMService.generate(prompt=prompt, temperature=0.2, max_tokens=1200)
        return {"symbols": [sym1, sym2], "comparison": comparison_text}
    except Exception as e:
        return {"symbols": symbols, "comparison": f"Error comparing companies: {str(e)}"}


@router.post("/copilot")
async def copilot_research_workspace(payload: dict):
    """
    Phase IX AI Research Copilot Endpoint:
    Provides evidence-grounded analyst reasoning, interactive chart configuration,
    Annual Report OCR citations, and suggested follow-up questions.
    """
    symbol = payload.get("symbol", "RELIANCE")
    query = payload.get("query", "Analyze this company")
    chat_history = payload.get("chat_history", [])

    from app.agents.copilot_agent import AICopilotAgent
    res = await AICopilotAgent.process_query(symbol=symbol, query=query, chat_history=chat_history)
    return res

