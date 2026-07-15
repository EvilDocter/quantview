"""
QuantView — Index Data Collector

Ingests historical and daily index level closing values for Nifty 50, Sensex, etc.
"""

import logging
from datetime import date, timedelta
from typing import Any
from sqlalchemy import select
import yfinance as yf

from app.ingestion.base_collector import BaseCollector
from app.models.price import IndexMaster, IndexPrice
from app.core.constants import INDICES

logger = logging.getLogger("index_collector")

class IndexCollector(BaseCollector):
    """Collector for stock index levels (Nifty 50, Sensex, etc.) using Yahoo Finance."""

    def __init__(self):
        super().__init__("index_collector")

    async def initialize_indices(self):
        """Ensures index master table is populated with default configuration."""
        session = await self.get_db_session()
        try:
            for symbol, details in INDICES.items():
                stmt = select(IndexMaster).where(IndexMaster.symbol == symbol)
                res = await session.execute(stmt)
                existing = res.scalar_one_or_none()
                if not existing:
                    idx = IndexMaster(
                        symbol=symbol,
                        name=details["name"],
                        exchange=details["exchange"]
                    )
                    session.add(idx)
            await session.commit()
        finally:
            await session.close()

    async def collect_historical_index(self, symbol: str, years: int = 5):
        """Fetches historical prices for a specific index."""
        session = await self.get_db_session()
        try:
            stmt = select(IndexMaster).where(IndexMaster.symbol == symbol)
            res = await session.execute(stmt)
            idx_master = res.scalar_one_or_none()
            if not idx_master:
                logger.error(f"Index master not found for {symbol}")
                return

            yahoo_symbol = INDICES[symbol]["yahoo_symbol"]
            end_date = date.today()
            start_date = end_date - timedelta(days=365 * years)

            ticker = yf.Ticker(yahoo_symbol)
            df = ticker.history(start=start_date, end=end_date, interval="1d")

            prices_added = 0
            for dt, row in df.iterrows():
                trade_date = dt.date()
                price_check = await session.execute(
                    select(IndexPrice).where(
                        IndexPrice.index_id == idx_master.id,
                        IndexPrice.date == trade_date
                    )
                )
                if price_check.scalar_one_or_none():
                    continue

                idx_price = IndexPrice(
                    index_id=idx_master.id,
                    date=trade_date,
                    open=row["Open"],
                    high=row["High"],
                    low=row["Low"],
                    close=row["Close"],
                    volume=int(row["Volume"])
                )
                session.add(idx_price)
                prices_added += 1

            await session.commit()
            logger.info(f"Loaded {prices_added} price records for Index {symbol}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error collecting index prices for {symbol}: {e}")
        finally:
            await session.close()

    async def collect(self, *args, **kwargs) -> Any:
        """Trigger update on all configured indices."""
        await self.initialize_indices()
        for symbol in INDICES.keys():
            await self.collect_historical_index(symbol, years=1)
            self.enforce_rate_limit()
