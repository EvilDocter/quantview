"""
QuantView — SQLAlchemy Model Registry

Imports all models so Alembic and the app can discover them.
"""

from app.models.company import Company
from app.models.financial import (
    FinancialStatement,
    FinancialRatio,
    ShareholdingPattern,
    CorporateAction,
    InsiderTrade,
    MutualFundHolding,
    InstitutionalActivity,
    AIScore,
)
from app.models.price import (
    StockPrice,
    IndexMaster,
    IndexPrice,
    IndexConstituent,
)
from app.models.document import (
    News,
    Document,
    ProcessedDocument,
    MacroData,
)
from app.models.user import (
    Watchlist,
    WatchlistItem,
    Portfolio,
    PortfolioHolding,
    ResearchHistory,
)

__all__ = [
    "Company",
    "FinancialStatement",
    "FinancialRatio",
    "ShareholdingPattern",
    "CorporateAction",
    "InsiderTrade",
    "MutualFundHolding",
    "InstitutionalActivity",
    "AIScore",
    "StockPrice",
    "IndexMaster",
    "IndexPrice",
    "IndexConstituent",
    "News",
    "Document",
    "ProcessedDocument",
    "MacroData",
    "Watchlist",
    "WatchlistItem",
    "Portfolio",
    "PortfolioHolding",
    "ResearchHistory",
]
