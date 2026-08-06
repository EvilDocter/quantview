"""
QuantView Broker Gateway — Unified Normalized Schemas

Provides clean, normalized Pydantic V2 schemas for holdings, positions,
funds, quotes, options, candles, and portfolios across all Indian brokers.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class BrokerCode(str, Enum):
    ZERODHA = "zerodha"
    ANGEL = "angel"
    FYERS = "fyers"
    UPSTOX = "upstox"
    DHAN = "dhan"


class Exchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"
    NFO = "NFO"
    MCX = "MCX"


class ProductType(str, Enum):
    CNC = "CNC"       # Cash & Carry / Delivery
    MIS = "MIS"       # Intraday
    NRML = "NRML"     # F&O Normal
    CO = "CO"         # Cover Order
    BO = "BO"         # Bracket Order
    MTF = "MTF"       # Margin Trading Facility


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class NormalizedHolding(BaseModel):
    model_config = ConfigDict(frozen=False)

    quantview_symbol: str = Field(description="Normalized symbol e.g. NSE:RELIANCE-EQ")
    trading_symbol: str = Field(description="Trading symbol e.g. RELIANCE")
    exchange: Exchange = Exchange.NSE
    isin: Optional[str] = None
    quantity: int
    t1_quantity: int = 0
    realised_quantity: int = 0
    average_price: Decimal
    current_price: Decimal
    last_price: Decimal
    pnl: Decimal
    pnl_percentage: Decimal
    day_change: Decimal = Decimal("0.0")
    day_change_percentage: Decimal = Decimal("0.0")
    current_value: Decimal
    investment_value: Decimal


class NormalizedPosition(BaseModel):
    model_config = ConfigDict(frozen=False)

    quantview_symbol: str
    trading_symbol: str
    exchange: Exchange = Exchange.NSE
    product: ProductType = ProductType.NRML
    quantity: int                  # Net quantity (+ for buy, - for sell)
    overnight_quantity: int = 0
    multiplier: int = 1
    buy_price: Decimal
    sell_price: Decimal
    last_price: Decimal
    realised_pnl: Decimal
    unrealised_pnl: Decimal
    total_pnl: Decimal


class NormalizedFunds(BaseModel):
    model_config = ConfigDict(frozen=False)

    net_available: Decimal
    cash_balance: Decimal
    collateral_margin: Decimal = Decimal("0.0")
    utilised_margin: Decimal = Decimal("0.0")
    unrealised_m2m: Decimal = Decimal("0.0")


class NormalizedQuote(BaseModel):
    model_config = ConfigDict(frozen=False)

    quantview_symbol: str
    trading_symbol: str
    exchange: Exchange = Exchange.NSE
    last_price: Decimal
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: int
    average_trade_price: Decimal = Decimal("0.0")
    oi: Optional[int] = None
    net_change: Decimal = Decimal("0.0")
    percentage_change: Decimal = Decimal("0.0")
    last_traded_time: Optional[datetime] = None


class OptionGreeks(BaseModel):
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    iv: Optional[float] = None


class OptionContract(BaseModel):
    quantview_symbol: str
    strike_price: Decimal
    option_type: str              # "CE" or "PE"
    expiry_date: str
    last_price: Decimal
    oi: int
    oi_change: int
    volume: int
    greeks: Optional[OptionGreeks] = None


class NormalizedOptionChain(BaseModel):
    underlying_symbol: str
    underlying_price: Decimal
    expiry_dates: List[str]
    selected_expiry: str
    contracts: List[OptionContract]


class NormalizedCandle(BaseModel):
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    oi: Optional[int] = 0


class NormalizedPortfolio(BaseModel):
    connection_id: str
    broker_code: BrokerCode
    account_id: str
    account_name: Optional[str] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    total_investment: Decimal
    total_current_value: Decimal
    total_pnl: Decimal
    total_pnl_percentage: Decimal
    today_pnl: Decimal = Decimal("0.0")
    funds: NormalizedFunds
    holdings: List[NormalizedHolding]
    positions: List[NormalizedPosition]
