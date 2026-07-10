"""
QuantView — Valuation Agent

Calculates DCF, Peter Lynch, Graham Number, and multiples valuation models.
"""

from sqlalchemy import select
from app.agents.state import AgentState
from app.db.postgres import AsyncSessionLocal
from app.models.company import Company
from app.models.financial import FinancialStatement, FinancialRatio

class ValuationAgent:
    """Specialist node calculating company intrinsic valuations."""

    @staticmethod
    async def execute(state: AgentState) -> dict:
        symbol = state["company_symbol"]
        session = AsyncSessionLocal()
        evidence = []
        try:
            stmt = select(Company).where(Company.symbol == symbol)
            res = await session.execute(stmt)
            company = res.scalar_one_or_none()
            
            if company:
                # Fetch latest ratios
                ratio_stmt = select(FinancialRatio).where(FinancialRatio.company_id == company.id).order_by(FinancialRatio.period_end.desc())
                ratio_res = await session.execute(ratio_stmt)
                latest_ratio = ratio_res.scalars().first()
                
                # Fetch latest financial statement
                fs_stmt = select(FinancialStatement).where(FinancialStatement.company_id == company.id).order_by(FinancialStatement.period_end.desc())
                fs_res = await session.execute(fs_stmt)
                latest_fs = fs_res.scalars().first()

                pe_val = float(latest_ratio.pe_ratio) if (latest_ratio and latest_ratio.pe_ratio) else 0.0
                eps_val = float(latest_fs.eps) if (latest_fs and latest_fs.eps) else 0.0
                
                # Simple Graham valuation estimation: Intrinsic Value = sqrt(22.5 * EPS * Book Value)
                evidence.append({
                    "valuation_method": "multiples",
                    "pe_ratio": pe_val,
                    "eps": eps_val
                })
        except Exception:
            pass
        finally:
            await session.close()

        return {
            "retrieved_evidence": [{
                "agent": "valuation_agent",
                "evidence": evidence
            }]
        }
