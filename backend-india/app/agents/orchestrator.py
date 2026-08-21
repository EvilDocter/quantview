"""
QuantView — High-Performance Parallel Orchestrator

Executes all specialist evidence gathering agents concurrently via asyncio.gather()
for sub-3 second evidence retrieval latency, followed by synthesis.
"""

import asyncio
import logging
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.financial_agent import FinancialAgent
from app.agents.filing_agent import FilingAgent
from app.agents.news_agent import NewsAgent
from app.agents.valuation_agent import ValuationAgent
from app.agents.synthesis_agent import SynthesisAgent

logger = logging.getLogger("agent_orchestrator")


async def run_parallel_evidence_gatherer(state: AgentState) -> dict:
    """Run all 4 specialist evidence agents concurrently in parallel."""
    query = state["query"]
    symbol = state["company_symbol"]
    logger.info(f"Triggering parallel evidence gathering for '{symbol}'...")

    # Execute all specialist agents in parallel
    results = await asyncio.gather(
        FinancialAgent.execute(state),
        NewsAgent.execute(state),
        FilingAgent.execute(state),
        ValuationAgent.execute(state),
        return_exceptions=True
    )

    combined_evidence = []
    for res in results:
        if isinstance(res, dict) and "retrieved_evidence" in res:
            combined_evidence.extend(res["retrieved_evidence"])
        elif isinstance(res, Exception):
            logger.warning(f"Specialist agent threw exception during parallel gather: {res}")

    return {
        "retrieved_evidence": combined_evidence,
        "plan": ["financial_agent", "news_agent", "filing_agent", "valuation_agent"],
        "current_step": 4,
    }


def build_workflow() -> StateGraph:
    """Compiles high-speed workflow: parallel_gatherer → synthesis → END."""
    workflow = StateGraph(AgentState)

    workflow.add_node("parallel_gatherer", run_parallel_evidence_gatherer)
    workflow.add_node("synthesis_agent", SynthesisAgent.execute)

    workflow.set_entry_point("parallel_gatherer")
    workflow.add_edge("parallel_gatherer", "synthesis_agent")
    workflow.add_edge("synthesis_agent", END)

    return workflow.compile()
