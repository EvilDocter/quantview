"""
QuantView — Portfolio Optimization & Factors Service

Computes Mean-Variance optimization allocations and correlation matrices using scipy/pandas.
"""

import logging
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sqlalchemy import select

from app.db.postgres import AsyncSessionLocal
from app.models.company import Company
from app.models.price import StockPrice

logger = logging.getLogger("portfolio_service")

class PortfolioService:
    """Calculates efficient frontiers and correlation coefficients for stock baskets."""

    @staticmethod
    async def calculate_portfolio_weights(symbols: list[str]) -> dict:
        """
        Uses standard Mean-Variance Optimization (Markowitz model)
        to calculate maximum Sharpe Ratio weight distributions.
        """
        session = AsyncSessionLocal()
        try:
            # Load price data
            price_series = {}
            for sym in symbols:
                stmt_comp = select(Company).where(Company.symbol == sym)
                comp = (await session.execute(stmt_comp)).scalar_one_or_none()
                if not comp:
                    continue

                stmt_p = select(StockPrice).where(StockPrice.company_id == comp.id).order_by(StockPrice.date.asc())
                prices = (await session.execute(stmt_p)).scalars().all()
                if prices:
                    price_series[sym] = [float(p.close) for p in prices]

            if not price_series:
                return {"error": "No historical price records found."}

            df = pd.DataFrame(price_series)
            returns = df.pct_change().dropna()
            
            # Mean EOD returns and Covariance Matrix
            mean_returns = returns.mean()
            cov_matrix = returns.cov()
            
            num_assets = len(symbols)
            
            # Optimization objective: Maximize Sharpe Ratio
            def portfolio_stats(weights):
                weights = np.array(weights)
                p_return = np.sum(mean_returns * weights) * 252
                p_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))
                sharpe = p_return / p_vol if p_vol > 0 else 0
                return -sharpe # Negative for minimization

            # Constraints: weights sum to 1
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0})
            bounds = tuple((0.0, 1.0) for _ in range(num_assets))
            initial_weights = [1.0 / num_assets] * num_assets

            opt = minimize(portfolio_stats, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)
            
            optimized_weights = opt.x.tolist()
            return {
                "symbols": symbols,
                "optimized_weights": {sym: round(w, 4) for sym, w in zip(symbols, optimized_weights)}
            }
        except Exception as e:
            logger.error(f"Portfolio optimization failure: {e}")
            return {"error": str(e)}
        finally:
            await session.close()
