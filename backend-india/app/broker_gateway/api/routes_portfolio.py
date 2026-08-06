"""
QuantView Broker Gateway — Normalized Portfolio Routes

Provides normalized portfolio, holdings, positions, funds, and intelligence metrics
for any connected Indian broker.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from decimal import Decimal

from app.broker_gateway.schemas.normalized import (
    NormalizedPortfolio, NormalizedHolding, NormalizedPosition,
    NormalizedFunds, BrokerCode
)
from app.broker_gateway.drivers.factory import BrokerFactory
from app.broker_gateway.drivers import * # Register all drivers
from app.broker_gateway.core.intelligence import PortfolioIntelligenceEngine

router = APIRouter(prefix="/broker-gateway", tags=["Broker Gateway"])

# In-memory store for connected sessions during development
MOCK_SESSIONS: Dict[str, Dict[str, Any]] = {
    "conn_zerodha_01": {
        "broker": BrokerCode.ZERODHA,
        "account_id": "AB1234",
        "access_token": "MOCK_ZERODHA_TOKEN",
        "api_key": "MOCK_KEY"
    },
    "conn_angel_01": {
        "broker": BrokerCode.ANGEL,
        "account_id": "A56789",
        "access_token": "MOCK_ANGEL_TOKEN",
        "api_key": "MOCK_KEY"
    },
    "conn_fyers_01": {
        "broker": BrokerCode.FYERS,
        "account_id": "FY1234",
        "access_token": "MOCK_FYERS_TOKEN",
        "api_key": "MOCK_KEY"
    },
    "conn_upstox_01": {
        "broker": BrokerCode.UPSTOX,
        "account_id": "UP9999",
        "access_token": "MOCK_UPSTOX_TOKEN",
        "api_key": "MOCK_KEY"
    },
    "conn_dhan_01": {
        "broker": BrokerCode.DHAN,
        "account_id": "DH8888",
        "access_token": "MOCK_DHAN_TOKEN",
        "api_key": "MOCK_KEY"
    }
}


@router.get("/portfolio", response_model=NormalizedPortfolio)
async def get_normalized_portfolio(
    broker: BrokerCode = Query(..., description="Broker code e.g. zerodha, angel, fyers, upstox, dhan"),
    connection_id: str = Query("conn_zerodha_01", description="Unique connection ID")
):
    """
    Returns normalized portfolio across ANY connected Indian broker.
    The response structure is 100% identical regardless of the underlying broker.
    """
    try:
        session = MOCK_SESSIONS.get(connection_id)
        token = session["access_token"] if session else "MOCK_ACCESS_TOKEN"
        account_id = session["account_id"] if session else "DEMO_ACCOUNT"
        api_key = session["api_key"] if session else "MOCK_API_KEY"

        driver = BrokerFactory.get_driver(
            broker_code=broker,
            connection_id=connection_id,
            account_id=account_id,
            access_token=token,
            api_key=api_key
        )
        return await driver.get_full_portfolio()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch portfolio from {broker}: {str(e)}")


@router.get("/portfolio/intelligence")
async def get_portfolio_intelligence(
    broker: BrokerCode = Query(BrokerCode.ZERODHA),
    connection_id: str = Query("conn_zerodha_01")
):
    """
    Returns portfolio analytics (Health Score, Portfolio Beta, Sector Distribution, Concentration Risk).
    """
    try:
        session = MOCK_SESSIONS.get(connection_id)
        token = session["access_token"] if session else "MOCK_ACCESS_TOKEN"
        account_id = session["account_id"] if session else "DEMO_ACCOUNT"
        api_key = session["api_key"] if session else "MOCK_API_KEY"

        driver = BrokerFactory.get_driver(
            broker_code=broker,
            connection_id=connection_id,
            account_id=account_id,
            access_token=token,
            api_key=api_key
        )
        portfolio = await driver.get_full_portfolio()
        intelligence = PortfolioIntelligenceEngine.analyze_portfolio(portfolio)
        return {
            "portfolio_summary": {
                "account_id": portfolio.account_id,
                "broker": portfolio.broker_code,
                "total_current_value": float(portfolio.total_current_value),
                "total_pnl": float(portfolio.total_pnl),
                "pnl_percentage": float(portfolio.total_pnl_percentage)
            },
            "intelligence": intelligence
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze portfolio: {str(e)}")
