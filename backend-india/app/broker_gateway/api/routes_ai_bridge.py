"""
QuantView Broker Gateway — AI Context Bridge

Provides secure, normalized portfolio context to QuantView AI Agents
without ever exposing raw credentials or access tokens to LLMs.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any

from app.broker_gateway.schemas.normalized import BrokerCode
from app.broker_gateway.drivers.factory import BrokerFactory
from app.broker_gateway.core.intelligence import PortfolioIntelligenceEngine

router = APIRouter(prefix="/broker-gateway/ai-bridge", tags=["AI Context Bridge"])


@router.get("/portfolio-context")
async def get_portfolio_context_for_ai(
    broker: BrokerCode = Query(BrokerCode.ZERODHA),
    connection_id: str = Query("conn_zerodha_01")
) -> Dict[str, Any]:
    """
    Secure context provider endpoint called by QuantView AI Agents.
    Returns structured portfolio summary and intelligence metrics.
    """
    try:
        driver = BrokerFactory.get_driver(
            broker_code=broker,
            connection_id=connection_id,
            account_id="CLIENT_UCC",
            access_token="MOCK_ACCESS_TOKEN",
            api_key="MOCK_API_KEY"
        )

        portfolio = await driver.get_full_portfolio()
        intelligence = PortfolioIntelligenceEngine.analyze_portfolio(portfolio)

        return {
            "account_id": portfolio.account_id,
            "broker": portfolio.broker_code,
            "summary": {
                "total_investment": float(portfolio.total_investment),
                "current_value": float(portfolio.total_current_value),
                "total_pnl": float(portfolio.total_pnl),
                "pnl_pct": float(portfolio.total_pnl_percentage),
                "cash_available": float(portfolio.funds.net_available)
            },
            "intelligence": intelligence,
            "holdings_snapshot": [
                {
                    "symbol": h.trading_symbol,
                    "quantity": h.quantity,
                    "avg_price": float(h.average_price),
                    "current_price": float(h.current_price),
                    "pnl": float(h.pnl)
                }
                for h in portfolio.holdings
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch portfolio context for AI: {str(e)}")
