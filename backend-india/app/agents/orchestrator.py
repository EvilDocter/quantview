"""
QuantView — LangGraph Orchestration Workspace

Builds and compiles the multi-agent execution state chart using LangGraph.
"""

import logging
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.planner import PlannerAgent
from app.agents.financial_agent import FinancialAgent
from app.agents.filing_agent import FilingAgent
from app.agents.news_agent import NewsAgent
from app.agents.valuation_agent import ValuationAgent
from app.agents.risk_agent import RiskAgent
from app.agents.kg_agent import KGAgent
from app.agents.synthesis_agent import SynthesisAgent

logger = logging.getLogger("agent_orchestrator")

def build_workflow() -> StateGraph:
    """Compiles the routing graph defining transitions between planner and specialists."""
    workflow = StateGraph(AgentState)

    # 1. Register Nodes
    workflow.add_node("planner", PlannerAgent.route_query)
    workflow.add_node("financial_agent", FinancialAgent.execute)
    workflow.add_node("filing_agent", FilingAgent.execute)
    workflow.add_node("news_agent", NewsAgent.execute)
    workflow.add_node("valuation_agent", ValuationAgent.execute)
    workflow.add_node("risk_agent", RiskAgent.execute)
    workflow.add_node("kg_agent", KGAgent.execute)
    workflow.add_node("synthesis_agent", SynthesisAgent.execute)

    # 2. Define Entry Point
    workflow.set_entry_point("planner")

    # 3. Dynamic Router Logic
    def router_transition(state: AgentState):
        plan = state["plan"]
        current_step = state["current_step"]
        
        if current_step < len(plan):
            next_agent = plan[current_step]
            # Increment step context
            state["current_step"] += 1
            return next_agent
        
        return "synthesis_agent"

    # 4. Map Conditional Edges
    workflow.add_conditional_edges(
        "planner",
        router_transition,
        {
            "financial_agent": "financial_agent",
            "filing_agent": "filing_agent",
            "news_agent": "news_agent",
            "valuation_agent": "valuation_agent",
            "risk_agent": "risk_agent",
            "kg_agent": "kg_agent",
            "synthesis_agent": "synthesis_agent"
        }
    )

    # Specialists feed back into routing context to process remaining items in planner schedule
    specialists = ["financial_agent", "filing_agent", "news_agent", "valuation_agent", "risk_agent", "kg_agent"]
    for specialist in specialists:
        workflow.add_conditional_edges(
            specialist,
            router_transition,
            {
                "financial_agent": "financial_agent",
                "filing_agent": "filing_agent",
                "news_agent": "news_agent",
                "valuation_agent": "valuation_agent",
                "risk_agent": "risk_agent",
                "kg_agent": "kg_agent",
                "synthesis_agent": "synthesis_agent"
            }
        )

    # Synthesis is the terminal node
    workflow.add_edge("synthesis_agent", END)

    return workflow.compile()
