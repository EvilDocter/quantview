"""
QuantView — Financial Data SQLAlchemy Models

Financial statements, ratios, shareholding patterns,
corporate actions, insider trades, and AI scores.
"""

from sqlalchemy import (
    Column, Integer, String, Text, BigInteger, Numeric,
    DateTime, Date, Boolean, ForeignKey, Index, UniqueConstraint,
    ARRAY, JSON,
    func,
)
from app.db.postgres import Base


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    period_type = Column(String(20), nullable=False)       # "annual", "quarterly"
    period_end = Column(Date, nullable=False)               # "2024-03-31"
    fiscal_year = Column(String(10))                        # "FY24"
    quarter = Column(String(5))                             # "Q1", "Q2", "Q3", "Q4"
    statement_type = Column(String(20), nullable=False)     # "standalone", "consolidated"
    currency = Column(String(3), default="INR")

    # Income Statement (all amounts in Crores)
    revenue = Column(Numeric(18, 2))
    other_income = Column(Numeric(18, 2))
    total_income = Column(Numeric(18, 2))
    raw_material_cost = Column(Numeric(18, 2))
    employee_cost = Column(Numeric(18, 2))
    other_expenses = Column(Numeric(18, 2))
    total_expenses = Column(Numeric(18, 2))
    ebitda = Column(Numeric(18, 2))
    depreciation = Column(Numeric(18, 2))
    ebit = Column(Numeric(18, 2))
    interest_expense = Column(Numeric(18, 2))
    profit_before_tax = Column(Numeric(18, 2))
    tax_expense = Column(Numeric(18, 2))
    net_profit = Column(Numeric(18, 2))
    eps = Column(Numeric(10, 2))
    diluted_eps = Column(Numeric(10, 2))

    # Balance Sheet
    total_assets = Column(Numeric(18, 2))
    fixed_assets = Column(Numeric(18, 2))
    current_assets = Column(Numeric(18, 2))
    investments = Column(Numeric(18, 2))
    cash_equivalents = Column(Numeric(18, 2))
    inventories = Column(Numeric(18, 2))
    trade_receivables = Column(Numeric(18, 2))
    total_equity = Column(Numeric(18, 2))
    share_capital = Column(Numeric(18, 2))
    reserves = Column(Numeric(18, 2))
    total_debt = Column(Numeric(18, 2))
    long_term_debt = Column(Numeric(18, 2))
    short_term_debt = Column(Numeric(18, 2))
    current_liabilities = Column(Numeric(18, 2))
    trade_payables = Column(Numeric(18, 2))

    # Cash Flow
    operating_cash_flow = Column(Numeric(18, 2))
    investing_cash_flow = Column(Numeric(18, 2))
    financing_cash_flow = Column(Numeric(18, 2))
    net_cash_flow = Column(Numeric(18, 2))
    free_cash_flow = Column(Numeric(18, 2))
    capex = Column(Numeric(18, 2))

    # Metadata
    source = Column(String(50))
    source_document_id = Column(Integer)
    data_hash = Column(String(64), unique=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("company_id", "period_end", "statement_type", "period_type",
                         name="uq_fs_company_period"),
        Index("idx_fs_company_period", "company_id", "period_end"),
    )


class FinancialRatio(Base):
    __tablename__ = "financial_ratios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    period_end = Column(Date, nullable=False)

    # Valuation
    pe_ratio = Column(Numeric(10, 2))
    pb_ratio = Column(Numeric(10, 2))
    ev_ebitda = Column(Numeric(10, 2))
    price_to_sales = Column(Numeric(10, 2))
    dividend_yield = Column(Numeric(5, 2))
    earnings_yield = Column(Numeric(5, 2))

    # Profitability
    roe = Column(Numeric(8, 2))
    roce = Column(Numeric(8, 2))
    roa = Column(Numeric(8, 2))
    operating_margin = Column(Numeric(8, 2))
    net_margin = Column(Numeric(8, 2))
    ebitda_margin = Column(Numeric(8, 2))

    # Growth
    revenue_growth_yoy = Column(Numeric(8, 2))
    profit_growth_yoy = Column(Numeric(8, 2))
    eps_growth_yoy = Column(Numeric(8, 2))

    # Leverage
    debt_to_equity = Column(Numeric(10, 2))
    interest_coverage = Column(Numeric(10, 2))
    current_ratio = Column(Numeric(10, 2))
    quick_ratio = Column(Numeric(10, 2))

    # Efficiency
    asset_turnover = Column(Numeric(10, 2))
    inventory_turnover = Column(Numeric(10, 2))
    receivable_days = Column(Numeric(10, 2))
    payable_days = Column(Numeric(10, 2))
    cash_conversion_cycle = Column(Numeric(10, 2))

    # Quality
    free_cash_flow_yield = Column(Numeric(8, 2))
    operating_cf_to_net_income = Column(Numeric(8, 2))

    __table_args__ = (
        UniqueConstraint("company_id", "period_end", name="uq_ratios_company_period"),
    )


class ShareholdingPattern(Base):
    __tablename__ = "shareholding_patterns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    quarter_end = Column(Date, nullable=False)

    promoter_pct = Column(Numeric(6, 2))
    promoter_pledge_pct = Column(Numeric(6, 2))
    fii_pct = Column(Numeric(6, 2))
    dii_pct = Column(Numeric(6, 2))
    mf_pct = Column(Numeric(6, 2))
    insurance_pct = Column(Numeric(6, 2))
    public_pct = Column(Numeric(6, 2))
    total_shares = Column(BigInteger)

    __table_args__ = (
        UniqueConstraint("company_id", "quarter_end", name="uq_shareholding_quarter"),
    )


class CorporateAction(Base):
    __tablename__ = "corporate_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    action_type = Column(String(50))  # "dividend", "split", "bonus", "rights", "buyback"
    ex_date = Column(Date)
    record_date = Column(Date)
    details = Column(Text)
    amount = Column(Numeric(12, 2))
    created_at = Column(DateTime, server_default=func.now())


class InsiderTrade(Base):
    __tablename__ = "insider_trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    insider_name = Column(String(200))
    category = Column(String(50))   # "Promoter", "Director", "KMP"
    trade_type = Column(String(10)) # "BUY", "SELL"
    quantity = Column(BigInteger)
    price = Column(Numeric(12, 2))
    value = Column(Numeric(18, 2))
    trade_date = Column(Date)
    disclosure_date = Column(Date)

    __table_args__ = (
        UniqueConstraint(
            "company_id", "insider_name", "trade_date", "trade_type", "quantity",
            name="uq_insider_trade",
        ),
    )


class MutualFundHolding(Base):
    __tablename__ = "mutual_fund_holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    fund_house = Column(String(200))
    scheme_name = Column(String(300))
    holding_date = Column(Date)
    shares_held = Column(BigInteger)
    holding_pct = Column(Numeric(6, 2))
    value_lakhs = Column(Numeric(18, 2))
    change_from_prev = Column(BigInteger)

    __table_args__ = (
        UniqueConstraint(
            "company_id", "scheme_name", "holding_date",
            name="uq_mf_holding",
        ),
    )


class InstitutionalActivity(Base):
    __tablename__ = "institutional_activity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    category = Column(String(10))  # "FII", "DII"
    buy_value = Column(Numeric(18, 2))  # in crores
    sell_value = Column(Numeric(18, 2))
    net_value = Column(Numeric(18, 2))

    __table_args__ = (
        UniqueConstraint("date", "category", name="uq_institutional_activity"),
    )


class AIScore(Base):
    __tablename__ = "ai_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    score_date = Column(Date, nullable=False)

    financial_health = Column(Numeric(3, 1))
    earnings_quality = Column(Numeric(3, 1))
    governance = Column(Numeric(3, 1))
    growth = Column(Numeric(3, 1))
    valuation = Column(Numeric(3, 1))
    momentum = Column(Numeric(3, 1))
    quality = Column(Numeric(3, 1))
    risk = Column(Numeric(3, 1))
    management_confidence = Column(Numeric(3, 1))
    competitive_moat = Column(Numeric(3, 1))
    overall_score = Column(Numeric(3, 1))

    # AI explanations
    health_explanation = Column(Text)
    quality_explanation = Column(Text)
    risk_explanation = Column(Text)
    moat_explanation = Column(Text)

    __table_args__ = (
        UniqueConstraint("company_id", "score_date", name="uq_ai_score_date"),
    )
