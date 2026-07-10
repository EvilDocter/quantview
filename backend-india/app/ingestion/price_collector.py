"""
QuantView — Stock Price Collector

Ingests historical and daily end-of-day stock prices using Yahoo Finance.
"""

import logging
from datetime import datetime, date, timedelta
from sqlalchemy import select
import yfinance as yf

from app.ingestion.base_collector import BaseCollector
from app.models.company import Company
from app.models.price import StockPrice
from app.core.utils import nse_symbol_to_yahoo

logger = logging.getLogger("price_collector")

class PriceCollector(BaseCollector):
    """Collector for EOD stock price data using Yahoo Finance."""

    def __init__(self):
        super().__init__("price_collector")

    async def collect_historical_prices(self, symbol: str, years: int = 10):
        """Fetches historical price data for a company and saves it to Postgres."""
        session = await self.get_db_session()
        try:
            # Resolve Company from Database
            stmt = select(Company).where(Company.symbol == symbol)
            res = await session.execute(stmt)
            company = res.scalar_one_or_none()
            if not company:
                logger.error(f"Company {symbol} not found in DB. Skip price ingestion.")
                return

            yahoo_symbol = nse_symbol_to_yahoo(symbol)
            end_date = date.today()
            start_date = end_date - timedelta(days=365 * years)
            
            logger.info(f"Fetching historical prices for {yahoo_symbol} from {start_date} to {end_date}...")
            
            # Fetch using yfinance wrapper
            ticker = yf.Ticker(yahoo_symbol)
            df = ticker.history(start=start_date, end=end_date, interval="1d")
            
            if df.empty:
                logger.warning(f"No price data retrieved for {yahoo_symbol}")
                return

            prices_added = 0
            for dt, row in df.iterrows():
                trade_date = dt.date()
                
                # Check if price already exists
                price_check = await session.execute(
                    select(StockPrice).where(
                        StockPrice.company_id == company.id,
                        StockPrice.date == trade_date
                    )
                )
                if price_check.scalar_one_or_none():
                    continue

                stock_price = StockPrice(
                    company_id=company.id,
                    date=trade_date,
                    open=row["Open"],
                    high=row["High"],
                    low=row["Low"],
                    close=row["Close"],
                    adj_close=row.get("Adj Close", row["Close"]),
                    volume=int(row["Volume"])
                )
                session.add(stock_price)
                prices_added += 1

            await session.commit()
            logger.info(f"Loaded {prices_added} new price records for {symbol}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error collecting prices for {symbol}: {e}")
        finally:
            await session.close()

    async def collect(self, *args, **kwargs) -> Any:
        """Daily collection trigger across all companies in symbol master."""
        session = await self.get_db_session()
        try:
            stmt = select(Company)
            res = await session.execute(stmt)
            companies = res.scalars().all()
            
            for company in companies:
                await self.collect_historical_prices(company.symbol, years=1)
                self.enforce_rate_limit()
        finally:
            await session.close()
