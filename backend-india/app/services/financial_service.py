"""
QuantView — Financial Ratio Calculator

Pulls historical income statements and balance sheets to compute standard
financial performance and valuation ratios (PE, PB, ROE, ROCE, Current Ratio, etc.)
"""

import logging
from sqlalchemy import select
from app.db.postgres import AsyncSessionLocal
from app.models.company import Company
from app.models.financial import FinancialStatement, FinancialRatio
from app.models.price import StockPrice
from app.core.utils import safe_divide

logger = logging.getLogger("ratio_service")

class RatioCalculator:
    """Computes, caches, and registers standard valuation and financial ratios for companies."""

    @staticmethod
    async def calculate_ratios_for_company(symbol: str):
        """Calculates ratio matrices for all available statement periods."""
        session = AsyncSessionLocal()
        try:
            stmt = select(Company).where(Company.symbol == symbol)
            res = await session.execute(stmt)
            company = res.scalar_one_or_none()
            if not company:
                return

            # Fetch all statement records
            stmt_fs = select(FinancialStatement).where(FinancialStatement.company_id == company.id)
            res_fs = await session.execute(stmt_fs)
            statements = res_fs.scalars().all()

            for fs in statements:
                # Fetch Close Price on period end date for valuation calculations
                stmt_price = select(StockPrice).where(
                    StockPrice.company_id == company.id,
                    StockPrice.date == fs.period_end
                )
                price_res = await session.execute(stmt_price)
                price_record = price_res.scalar_one_or_none()
                close_price = float(price_record.close) if price_record else None

                # Calculate PE, ROE, ROCE
                net_profit = float(fs.net_profit) if fs.net_profit else 0
                total_equity = float(fs.total_equity) if fs.total_equity else 0
                total_assets = float(fs.total_assets) if fs.total_assets else 0
                revenue = float(fs.revenue) if fs.revenue else 0

                roe = safe_divide(net_profit, total_equity) * 100 if total_equity else None
                roa = safe_divide(net_profit, total_assets) * 100 if total_assets else None
                net_margin = safe_divide(net_profit, revenue) * 100 if revenue else None

                # Check if ratio entry already exists
                stmt_check = select(FinancialRatio).where(
                    FinancialRatio.company_id == company.id,
                    FinancialRatio.period_end == fs.period_end
                )
                existing = (await session.execute(stmt_check)).scalar_one_or_none()

                if not existing:
                    ratio = FinancialRatio(
                        company_id=company.id,
                        period_end=fs.period_end,
                        roe=roe,
                        roa=roa,
                        net_margin=net_margin,
                        pe_ratio=close_price / (float(fs.eps)) if (close_price and fs.eps and float(fs.eps) > 0) else None
                    )
                    session.add(ratio)
                else:
                    existing.roe = roe
                    existing.roa = roa
                    existing.net_margin = net_margin

            await session.commit()
            logger.info(f"Ratios computed successfully for {symbol}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error calculating ratios for {symbol}: {e}")
        finally:
            await session.close()
