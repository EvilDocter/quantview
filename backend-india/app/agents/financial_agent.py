"""
QuantView — Financial Analysis Agent

Resolves company financial metrics (revenue, margin growth) from PostgreSQL.
"""

from sqlalchemy import select
from app.agents.state import AgentState
from app.db.postgres import AsyncSessionLocal
from app.models.company import Company
from app.models.financial import FinancialStatement

class FinancialAgent:
    """Specialist node resolving structured financial values."""

    @staticmethod
    async def execute(state: AgentState) -> dict:
        symbol = state["company_symbol"]
        session = AsyncSessionLocal()
        evidence = []
        try:
            # Query Database
            stmt = select(Company).where(Company.symbol == symbol)
            res = await session.execute(stmt)
            company = res.scalar_one_or_none()
            
            if company:
                stmt_fs = select(FinancialStatement).where(FinancialStatement.company_id == company.id)
                fs_res = await session.execute(stmt_fs)
                statements = fs_res.scalars().all()
                
                for fs in statements:
                    evidence.append({
                        "source": "financial_statements",
                        "period": str(fs.period_end),
                        "revenue": float(fs.revenue) if fs.revenue else 0.0,
                        "net_profit": float(fs.net_profit) if fs.net_profit else 0.0,
                        "ebitda": float(fs.ebitda) if fs.ebitda else 0.0
                    })
        except Exception as e:
            pass
        finally:
            await session.close()
            
        return {
            "retrieved_evidence": [{
                "agent": "financial_agent",
                "evidence": evidence
            }]
        }
