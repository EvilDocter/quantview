"""
QuantView — Synthesis Agent

Aggregates all retrieved evidence nodes and invokes Qwen 2.5 7B reasoning server
to produce the final investment research report with citations.
"""

import httpx
import logging
import json
from app.config import get_settings
from app.agents.state import AgentState

logger = logging.getLogger("synthesis_agent")
settings = get_settings()

class SynthesisAgent:
    """Consolidates evidence arrays to generate final cited reports."""

    @staticmethod
    async def execute(state: AgentState) -> dict:
        query = state["query"]
        symbol = state["company_symbol"]
        evidence = state["retrieved_evidence"]
        
        prompt = f"""
You are the Lead Financial Analyst at QuantView.
Create a comprehensive, professional investment research report on {symbol} to answer the user query.

User Query: "{query}"

Retrieved Evidence Context:
{json.dumps(evidence, indent=2)}

Guidelines:
1. Synthesize P&L details, news sentiment, risk parameters, and graph connections.
2. Cite sources inline: [Source: financial_agent] or [Source: filing_agent].
3. Maintain objective analysis.

Write the final cited report in Markdown format:
"""
        final_report = "System synthesis failed. Please try again."
        confidence_score = 0.5
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.ai_server_url}/completion",
                    json={
                        "prompt": prompt,
                        "model": settings.llm_reasoning_model,
                        "temperature": 0.2,
                        "max_tokens": 1500
                    }
                )
                if response.status_code == 200:
                    final_report = response.json().get("text", "")
                    confidence_score = 0.85
        except Exception as e:
            logger.error(f"Synthesis agent call failed: {e}")

        return {
            "final_report": final_report,
            "confidence_score": confidence_score,
            "citations": evidence
        }
