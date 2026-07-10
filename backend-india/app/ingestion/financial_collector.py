"""
QuantView — BSE Financial Statement Ingestion & Parser

Scrapes and parses quarterly and annual corporate financial results (P&L, Balance Sheet)
from BSE corporate filings. Uses a fallback model to fetch yfinance data if scraping fails.
"""

import logging
from datetime import date
from sqlalchemy import select
import yfinance as yf

from app.ingestion.base_collector import BaseCollector
from app.models.company import Company
from app.models.financial import FinancialStatement
from app.core.utils import nse_symbol_to_yahoo, fiscal_year_from_date, quarter_from_date, generate_hash

logger = logging.getLogger("financial_collector")

class FinancialCollector(BaseCollector):
    """Collector for Company Financial Statements (Income Statement, Balance Sheet, Cash Flow)."""

    def __init__(self):
        super().__init__("financial_collector")

    async def ingest_financials_via_yfinance(self, symbol: str):
        """
        Fallback parser pulling financials from Yahoo Finance
        to ensure data completeness under the ₹0 budget.
        """
        session = await self.get_db_session()
        try:
            stmt = select(Company).where(Company.symbol == symbol)
            res = await session.execute(stmt)
            company = res.scalar_one_or_none()
            if not company:
                logger.error(f"Company {symbol} not found in DB.")
                return

            yahoo_symbol = nse_symbol_to_yahoo(symbol)
            ticker = yf.Ticker(yahoo_symbol)

            # Ingest Annual Financials (Income Statement)
            financials = ticker.financials
            if not financials.empty:
                for col in financials.columns:
                    period_end = col.date()
                    
                    # Convert values to Crores (yfinance is in raw numbers)
                    revenue = financials.loc["Total Revenue"][col] / 10000000 if "Total Revenue" in financials.index else 0
                    net_profit = financials.loc["Net Income"][col] / 10000000 if "Net Income" in financials.index else 0
                    ebitda = financials.loc["EBITDA"][col] / 10000000 if "EBITDA" in financials.index else 0

                    data_hash = generate_hash(company.id, period_end, "annual", "consolidated")
                    
                    # Check if already exists
                    stmt_check = select(FinancialStatement).where(FinancialStatement.data_hash == data_hash)
                    existing = (await session.execute(stmt_check)).scalar_one_or_none()
                    
                    if not existing:
                        financial_stmt = FinancialStatement(
                            company_id=company.id,
                            period_type="annual",
                            period_end=period_end,
                            fiscal_year=fiscal_year_from_date(period_end),
                            quarter="Q4", # Annual statements represent Q4/full year close
                            statement_type="consolidated",
                            revenue=revenue,
                            total_income=revenue,
                            net_profit=net_profit,
                            ebitda=ebitda,
                            source="yahoo_finance",
                            data_hash=data_hash
                        )
                        session.add(financial_stmt)

            await session.commit()
            logger.info(f"Successfully processed financials fallback for {symbol}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed fallback financials for {symbol}: {e}")
        finally:
            await session.close()

    async def collect(self, *args, **kwargs) -> Any:
        """Runs the collection loop across all seeded Nifty 500 companies."""
        session = await self.get_db_session()
        try:
            stmt = select(Company)
            res = await session.execute(stmt)
            companies = res.scalars().all()
            
            for company in companies:
                await self.ingest_financials_via_yfinance(company.symbol)
                self.enforce_rate_limit()
        finally:
            await session.close()
