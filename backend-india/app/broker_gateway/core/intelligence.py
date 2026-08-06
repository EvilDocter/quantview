"""
QuantView Broker Gateway — Portfolio Intelligence & Risk Analytics Engine

Calculates Portfolio Health Score, Portfolio Beta relative to NIFTY 50,
Concentration Risk, and Sector Distribution over normalized holdings.
"""

from decimal import Decimal
from typing import Dict, List, Any
from app.broker_gateway.schemas.normalized import NormalizedPortfolio, NormalizedHolding


class PortfolioIntelligenceEngine:
    """Quantitative analytics engine calculating portfolio health & factor exposure."""

    SECTOR_MAPPING = {
        "RELIANCE": "Energy & Petrochemicals",
        "TCS": "IT Services",
        "INFY": "IT Services",
        "WIPRO": "IT Services",
        "HDFCBANK": "Private Banking",
        "ICICIBANK": "Private Banking",
        "KOTAKBANK": "Private Banking",
        "AXISBANK": "Private Banking",
        "SBIN": "Public Banking",
        "TATAMOTORS": "Automobiles",
        "MARUTI": "Automobiles",
        "BHARTIARTL": "Telecommunications",
        "ITC": "FMCG",
        "SUNPHARMA": "Pharmaceuticals",
        "LT": "Engineering & Construction",
    }

    STOCK_BETAS = {
        "RELIANCE": 1.05,
        "TCS": 0.85,
        "INFY": 0.92,
        "WIPRO": 0.90,
        "HDFCBANK": 1.10,
        "ICICIBANK": 1.15,
        "KOTAKBANK": 1.08,
        "AXISBANK": 1.20,
        "SBIN": 1.30,
        "TATAMOTORS": 1.45,
        "MARUTI": 1.10,
        "BHARTIARTL": 0.75,
        "ITC": 0.65,
        "SUNPHARMA": 0.70,
        "LT": 1.12,
    }

    @classmethod
    def analyze_portfolio(cls, portfolio: NormalizedPortfolio) -> Dict[str, Any]:
        total_val = float(portfolio.total_current_value)
        if total_val == 0:
            return {
                "portfolio_health_score": 0,
                "status": "EMPTY_PORTFOLIO",
                "portfolio_beta": 1.0,
                "sector_allocation": {},
                "risk_penalties": ["Portfolio contains no active holdings."],
                "ai_verdict": "NO_HOLDINGS",
            }

        sector_allocation: Dict[str, float] = {}
        weighted_beta = 0.0
        max_concentration = 0.0
        top_holding_symbol = ""

        for h in portfolio.holdings:
            weight = float(h.current_value) / total_val if total_val > 0 else 0
            sym = h.trading_symbol.upper()

            # Sector allocation
            sector = cls.SECTOR_MAPPING.get(sym, "Diversified / Others")
            sector_allocation[sector] = sector_allocation.get(sector, 0.0) + weight

            # Weighted Portfolio Beta
            beta = cls.STOCK_BETAS.get(sym, 1.0)
            weighted_beta += beta * weight

            # Concentration Risk Check
            if weight > max_concentration:
                max_concentration = weight
                top_holding_symbol = sym

        # Health Score Calculation (100 Base)
        health_score = 100
        penalties = []

        if max_concentration > 0.35:
            health_score -= 20
            penalties.append(
                f"High single-stock concentration: {top_holding_symbol} is {max_concentration * 100:.1f}% of total portfolio."
            )

        if weighted_beta > 1.3:
            health_score -= 15
            penalties.append(
                f"High portfolio volatility: Beta is {weighted_beta:.2f} relative to NIFTY 50."
            )

        top_sector = max(sector_allocation.items(), key=lambda x: x[1]) if sector_allocation else ("None", 0)
        if top_sector[1] > 0.50:
            health_score -= 15
            penalties.append(
                f"Sector Overexposure: {top_sector[0]} represents {top_sector[1] * 100:.1f}% of overall holdings."
            )

        return {
            "portfolio_health_score": max(health_score, 0),
            "portfolio_beta": round(weighted_beta, 2),
            "top_holding_concentration": {
                "symbol": top_holding_symbol,
                "percentage": round(max_concentration * 100, 2),
            },
            "sector_allocation": {k: round(v * 100, 2) for k, v in sector_allocation.items()},
            "risk_penalties": penalties,
            "ai_verdict": "STRONG_HEALTH"
            if health_score >= 80
            else ("MODERATE_RISK" if health_score >= 60 else "HIGH_CONCENTRATION_RISK"),
        }
