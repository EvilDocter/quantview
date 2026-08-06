"""
QuantView — Planner Agent

Deterministic planner that always routes to all data-gathering agents.
No LLM call needed — this saves an API call and removes a failure point.
"""

import logging
from app.agents.state import AgentState

logger = logging.getLogger("planner_agent")


class PlannerAgent:
    """Deterministic routing — always invokes all live-data agents."""

    @staticmethod
    async def route_query(state: AgentState) -> dict:
        plan = ["financial_agent", "news_agent", "filing_agent", "valuation_agent"]
        logger.info(f"Planner: routing query '{state['query']}' → {plan}")
        return {"plan": plan, "current_step": 0}
