"""
QuantView — Quantitative Strategy Backtester Service

Runs vectorised and event-driven backtesting models using pandas and numpy historical EOD data.
"""

import logging
import pandas as pd
import numpy as np
from sqlalchemy import select
from app.db.postgres import AsyncSessionLocal
from app.models.price import StockPrice
from app.models.company import Company

logger = logging.getLogger("quant_service")

class QuantService:
    """Provides calculation logic for historical strategy backtests and factor analysis."""

    @staticmethod
    async def run_ma_crossover_backtest(
        symbol: str,
        short_window: int = 50,
        long_window: int = 200
    ) -> dict:
        """
        Runs a standard Moving Average Crossover strategy over a stock's history.
        Returns performance returns and drawdown metrics.
        """
        session = AsyncSessionLocal()
        try:
            stmt_comp = select(Company).where(Company.symbol == symbol)
            company = (await session.execute(stmt_comp)).scalar_one_or_none()
            if not company:
                return {}

            # Query historical EOD prices
            stmt_prices = select(StockPrice).where(StockPrice.company_id == company.id).order_by(StockPrice.date.asc())
            price_records = (await session.execute(stmt_prices)).scalars().all()

            if len(price_records) < long_window:
                return {"error": "Insufficient historical data points for indicators window."}

            # Build DataFrame
            df = pd.DataFrame([{
                "date": p.date,
                "close": float(p.close)
            } for p in price_records])

            df.set_index("date", inplace=True)
            
            # Indicators
            df["short_mavg"] = df["close"].rolling(window=short_window, min_periods=1).mean()
            df["long_mavg"] = df["close"].rolling(window=long_window, min_periods=1).mean()
            
            # Signals
            df["signal"] = 0.0
            df["signal"] = np.where(df["short_mavg"] > df["long_mavg"], 1.0, 0.0)
            df["positions"] = df["signal"].diff()

            # Returns
            df["market_returns"] = np.log(df["close"] / df["close"].shift(1))
            df["strategy_returns"] = df["market_returns"] * df["signal"].shift(1)

            # Cumulative returns
            cum_market_returns = np.exp(df["market_returns"].sum()) - 1.0
            cum_strat_returns = np.exp(df["strategy_returns"].sum()) - 1.0

            # Max drawdown calculation
            cum_returns = np.exp(df["strategy_returns"].cumsum())
            running_max = cum_returns.cummax()
            drawdowns = (cum_returns - running_max) / running_max
            max_drawdown = float(drawdowns.min())

            return {
                "symbol": symbol,
                "strategy": f"{short_window}/{long_window} MA Crossover",
                "market_returns_pct": round(cum_market_returns * 100, 2),
                "strategy_returns_pct": round(cum_strat_returns * 100, 2),
                "max_drawdown_pct": round(max_drawdown * 100, 2)
            }
        except Exception as e:
            logger.error(f"Backtest engine failed: {e}")
            return {"error": str(e)}
        finally:
            await session.close()
