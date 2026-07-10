"""
QuantView — LangGraph Agent State definitions

Establishes the state objects passed between specialized agents during research compilation.
"""

from typing import TypedDict, Annotated, List, Dict, Any
import operator

class AgentState(TypedDict):
    """LangGraph execution context representation."""
    query: str
    company_symbol: str
    plan: List[str]
    current_step: int
    retrieved_evidence: Annotated[List[Dict[str, Any]], operator.add]
    final_report: str
    confidence_score: float
    citations: List[Dict[str, Any]]
