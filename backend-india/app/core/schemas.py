"""
QuantView — Pydantic Response Schemas

API response models for type-safe, documented API responses.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


# ── Company Schemas ──────────────────────────────────────────────


class CompanyBase(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[int] = None
    market_cap_category: Optional[str] = None


class CompanyOverview(CompanyBase):
    bse_code: Optional[str] = None
    isin: Optional[str] = None
    listing_date: Optional[date] = None
    face_value: Optional[float] = None
    website: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_moat_score: Optional[float] = None
    ai_health_score: Optional[float] = None

    # Latest price info (populated at API level)
    current_price: Optional[float] = None
    price_change: Optional[float] = None
    price_change_pct: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    volume: Optional[int] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None

    model_config = {"from_attributes": True}


class CompanyListItem(CompanyBase):
    current_price: Optional[float] = None
    price_change_pct: Optional[float] = None
    pe_ratio: Optional[float] = None
    market_cap_category: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Financial Schemas ────────────────────────────────────────────


class FinancialStatementResponse(BaseModel):
    period_end: date
    fiscal_year: Optional[str] = None
    quarter: Optional[str] = None
    period_type: str
    statement_type: str

    # Income Statement
    revenue: Optional[float] = None
    total_income: Optional[float] = None
    total_expenses: Optional[float] = None
    ebitda: Optional[float] = None
    ebit: Optional[float] = None
    profit_before_tax: Optional[float] = None
    net_profit: Optional[float] = None
    eps: Optional[float] = None

    # Balance Sheet
    total_assets: Optional[float] = None
    total_equity: Optional[float] = None
    total_debt: Optional[float] = None
    cash_equivalents: Optional[float] = None

    # Cash Flow
    operating_cash_flow: Optional[float] = None
    free_cash_flow: Optional[float] = None
    capex: Optional[float] = None

    model_config = {"from_attributes": True}


class RatioResponse(BaseModel):
    period_end: date
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    roe: Optional[float] = None
    roce: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    revenue_growth_yoy: Optional[float] = None
    profit_growth_yoy: Optional[float] = None
    dividend_yield: Optional[float] = None

    model_config = {"from_attributes": True}


# ── Shareholding Schema ─────────────────────────────────────────


class ShareholdingResponse(BaseModel):
    quarter_end: date
    promoter_pct: Optional[float] = None
    promoter_pledge_pct: Optional[float] = None
    fii_pct: Optional[float] = None
    dii_pct: Optional[float] = None
    mf_pct: Optional[float] = None
    public_pct: Optional[float] = None

    model_config = {"from_attributes": True}


# ── Market Overview Schema ───────────────────────────────────────


class IndexData(BaseModel):
    name: str
    symbol: str
    close: Optional[float] = None
    change: Optional[float] = None
    change_pct: Optional[float] = None


class MarketOverview(BaseModel):
    indices: list[IndexData] = []
    top_gainers: list[CompanyListItem] = []
    top_losers: list[CompanyListItem] = []
    most_active: list[CompanyListItem] = []
    fii_net: Optional[float] = None
    dii_net: Optional[float] = None
    advances: Optional[int] = None
    declines: Optional[int] = None
    unchanged: Optional[int] = None


# ── AI Research Schemas ──────────────────────────────────────────


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000)
    company_symbol: Optional[str] = None
    conversation_id: Optional[str] = None


class Citation(BaseModel):
    source_type: str     # "financial_statement", "annual_report", "news", etc.
    source_id: str
    content: str
    relevance_score: float
    url: Optional[str] = None
    page_number: Optional[int] = None


class ResearchResponse(BaseModel):
    query: str
    answer: str
    confidence: float
    citations: list[Citation] = []
    agents_used: list[str] = []
    charts_data: Optional[dict] = None
    processing_time_ms: int


# ── AI Scores Schema ────────────────────────────────────────────


class AIScoreResponse(BaseModel):
    score_date: date
    financial_health: Optional[float] = None
    earnings_quality: Optional[float] = None
    governance: Optional[float] = None
    growth: Optional[float] = None
    valuation: Optional[float] = None
    momentum: Optional[float] = None
    quality: Optional[float] = None
    risk: Optional[float] = None
    management_confidence: Optional[float] = None
    competitive_moat: Optional[float] = None
    overall_score: Optional[float] = None

    health_explanation: Optional[str] = None
    quality_explanation: Optional[str] = None
    risk_explanation: Optional[str] = None
    moat_explanation: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Knowledge Graph Schema ──────────────────────────────────────


class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # "Company", "Person", "Product", "Sector"
    primary: bool = False
    properties: dict = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str  # "COMPETES_WITH", "SUPPLIES_TO", etc.
    properties: dict = {}


class KnowledgeGraphResponse(BaseModel):
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []


# ── News Schema ──────────────────────────────────────────────────


class NewsItem(BaseModel):
    id: int
    title: str
    source: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[datetime] = None
    sentiment_label: Optional[str] = None
    sentiment_score: Optional[float] = None
    category: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Screener Schema ─────────────────────────────────────────────


class ScreenerRequest(BaseModel):
    query: str = Field(..., min_length=3)


class ScreenerResult(BaseModel):
    companies: list[CompanyListItem] = []
    query_interpretation: str = ""
    total_results: int = 0


# ── Portfolio Schema ─────────────────────────────────────────────


class PortfolioHoldingItem(BaseModel):
    symbol: str
    name: str
    quantity: int
    avg_buy_price: float
    current_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    weight_pct: Optional[float] = None


class PortfolioResponse(BaseModel):
    id: int
    name: str
    holdings: list[PortfolioHoldingItem] = []
    total_invested: float = 0
    current_value: float = 0
    total_pnl: float = 0
    total_pnl_pct: float = 0


# ── Generic Response ─────────────────────────────────────────────


class APIResponse(BaseModel):
    success: bool = True
    message: str = ""
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
