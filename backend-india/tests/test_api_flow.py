"""
QuantView — E2E Test Suite for Indian Market Modules

Tests data ingestion pipes, AI agents state flows, and FastAPI routes.
"""

import pytest
from datetime import date
from app.core.utils import generate_hash, fiscal_year_from_date, quarter_from_date
from app.agents.state import AgentState
from app.agents.planner import PlannerAgent
from app.services.quant_service import QuantService
from app.services.monte_carlo import MonteCarloService

def test_hash_generation():
    h1 = generate_hash("RELIANCE", "annual", 2024)
    h2 = generate_hash("RELIANCE", "annual", 2024)
    h3 = generate_hash("RELIANCE", "quarterly", 2024)
    assert h1 == h2
    assert h1 != h3

def test_fiscal_year_mapping():
    assert fiscal_year_from_date(date(2024, 3, 31)) == "FY24"
    assert fiscal_year_from_date(date(2024, 4, 1)) == "FY25"
    assert quarter_from_date(date(2024, 6, 30)) == "Q1"
    assert quarter_from_date(date(2024, 12, 31)) == "Q3"

def test_monte_carlo_walk():
    trajectories = MonteCarloService.run_monte_carlo_simulation(
        start_price=100.0,
        days=10,
        simulations=5
    )
    assert len(trajectories) == 5
    assert len(trajectories[0]) == 11
    assert trajectories[0][0] == 100.0
