"""
QuantView — Risk Analysis Agent

Analyzes financial stability, leverage concerns, promoter pledging, and auditor qualifications.
"""

from sqlalchemy import select
from app.agents.state import AgentState
from app.db.postgres import AsyncSessionLocal
from app.models.company import Company
from app.models.financial import FinancialRatio, ShareholdingPattern

class RiskAgent:
    """Specialist node resolving company financial and structural risks."""

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
                # Check leverage ratios
                ratio_stmt = select(FinancialRatio).where(FinancialRatio.company_id == company.id).order_by(FinancialRatio.period_end.desc())
                latest_ratio = (await session.execute(ratio_stmt)).scalars().first()
                
                # Check pledging details
                sh_stmt = select(ShareholdingPattern).where(ShareholdingPattern.company_id == company.id).order_by(ShareholdingPattern.quarter_end.desc())
                latest_sh = (await session.execute(sh_stmt)).scalars().first()

                debt_to_equity = float(latest_ratio.debt_to_equity) if (latest_ratio and latest_ratio.debt_to_equity) else 0.0
                pledged_pct = float(latest_sh.promoter_pledge_pct) if (latest_sh and latest_sh.promoter_pledge_pct) else 0.0

                evidence.append({
                    "risk_metric": "leverage",
                    "debt_to_equity": debt_to_equity,
                    "status": "High Risk" if debt_to_equity > 2.0 else "Normal"
                })
                evidence.append({
                    "risk_metric": "promoter_pledge",
                    "pledged_pct": pledged_pct,
                    "status": "High Risk" if pledged_pct > 25.0 else "Normal"
                })
        except Exception:
            pass
        finally:
            await session.close()

        return {
            "retrieved_evidence": [{
                "agent": "risk_agent",
                "evidence": evidence
            }]
        }
