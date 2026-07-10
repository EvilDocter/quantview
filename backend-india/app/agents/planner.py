"""
QuantView — Planner Agent

Invokes Qwen 2.5 7B to classify queries and decompose research objectives
into tasks for specialized agents.
"""

import httpx
import logging
from app.config import get_settings
from app.agents.state import AgentState

logger = logging.getLogger("planner_agent")
settings = get_settings()

class PlannerAgent:
    """Orchestrates agent routing and sub-task scheduling."""

    @staticmethod
    async def route_query(state: AgentState) -> dict:
        """Determines which agent nodes are required to fulfill the user's research request."""
        query = state["query"]
        prompt = f"""
You are the Lead Coordinator for the QuantView AI Financial Research OS.
Analyze this user query and decide which agents need to execute.

Available specialist agents:
1. financial_agent (P&L, Balance Sheet, Ratios, comparisons)
2. filing_agent (Annual reports, quarterly disclosures, transcripts)
3. news_agent (Recent news, market sentiment)
4. valuation_agent (DCF valuation, multiples)

Return a JSON list representing the execution sequence.
Example: ["financial_agent", "filing_agent"]

Query: "{query}"
"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.ai_server_url}/completion",
                    json={
                        "prompt": prompt,
                        "model": settings.llm_reasoning_model,
                        "temperature": 0.0
                    }
                )
                if response.status_code == 200:
                    raw = response.json().get("text", "")
                    # Extract list block
                    if "[" in raw:
                        import json
                        start = raw.find("[")
                        end = raw.rfind("]") + 1
                        plan = json.loads(raw[start:end])
                        return {"plan": plan, "current_step": 0}
        except Exception as e:
            logger.error(f"Planner routing failed: {e}")

        # Default fallback plan if coordinator is unreachable
        return {"plan": ["financial_agent", "filing_agent"], "current_step": 0}
