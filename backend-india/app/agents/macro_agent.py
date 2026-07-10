"""
QuantView — Macroeconomic Agent

Queries PostgreSQL and RBI source files to resolve macro variables (Inflation, GDP growth).
"""

from sqlalchemy import select
from app.agents.state import AgentState
from app.db.postgres import AsyncSessionLocal
from app.models.document import MacroData

class MacroAgent:
    """Specialist agent node analyzing macroeconomic indices and monetary decisions."""

    @staticmethod
    async def execute(state: AgentState) -> dict:
        session = AsyncSessionLocal()
        evidence = []
        try:
            stmt = select(MacroData).order_by(MacroData.period.desc()).limit(3)
            res = await session.execute(stmt)
            records = res.scalars().all()
            for rec in records:
                evidence.append({
                    "indicator": rec.indicator,
                    "value": float(rec.value) if rec.value else 0.0,
                    "period": str(rec.period)
                })
        except Exception:
            pass
        finally:
            await session.close()

        return {
            "retrieved_evidence": [{
                "agent": "macro_agent",
                "evidence": evidence
            }]
        }
