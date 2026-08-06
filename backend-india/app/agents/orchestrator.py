"""
QuantView — LangGraph Orchestration Workspace

Builds and compiles the multi-agent execution state chart using LangGraph.
Only includes agents that have live data sources (no empty-DB agents).
"""

import logging
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.planner import PlannerAgent
from app.agents.financial_agent import FinancialAgent
from app.agents.filing_agent import FilingAgent
from app.agents.news_agent import NewsAgent
from app.agents.valuation_agent import ValuationAgent
from app.agents.synthesis_agent import SynthesisAgent

logger = logging.getLogger("agent_orchestrator")


def build_workflow() -> StateGraph:
    """Compiles the routing graph: planner → specialists → synthesis → END."""
    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("planner", PlannerAgent.route_query)

    async def wrap_agent(agent_cls, state: AgentState):
        res = await agent_cls.execute(state)
        res["current_step"] = state.get("current_step", 0) + 1
        return res

    async def run_financial(state: AgentState):
        return await wrap_agent(FinancialAgent, state)

    async def run_filing(state: AgentState):
        return await wrap_agent(FilingAgent, state)

    async def run_news(state: AgentState):
        return await wrap_agent(NewsAgent, state)

    async def run_valuation(state: AgentState):
        return await wrap_agent(ValuationAgent, state)

    workflow.add_node("financial_agent", run_financial)
    workflow.add_node("filing_agent", run_filing)
    workflow.add_node("news_agent", run_news)
    workflow.add_node("valuation_agent", run_valuation)
    workflow.add_node("synthesis_agent", SynthesisAgent.execute)

    # Entry point
    workflow.set_entry_point("planner")

    # Dynamic router: walk through the plan list, then go to synthesis
    def router_transition(state: AgentState):
        plan = state.get("plan", [])
        current_step = state.get("current_step", 0)
        if current_step < len(plan):
            return plan[current_step]
        return "synthesis_agent"

    # All possible targets from the router
    all_nodes = [
        "financial_agent", "filing_agent", "news_agent",
        "valuation_agent", "synthesis_agent",
    ]

    workflow.add_conditional_edges(
        "planner", router_transition, {n: n for n in all_nodes}
    )

    for specialist in all_nodes[:-1]:  # everything except synthesis
        workflow.add_conditional_edges(
            specialist, router_transition, {n: n for n in all_nodes}
        )

    workflow.add_edge("synthesis_agent", END)

    return workflow.compile()
