"""
QuantView Broker Gateway — Abstract Base Broker Driver

All broker implementations (Zerodha, Angel, FYERS, Upstox, Dhan)
must inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import asyncio

from app.broker_gateway.schemas.normalized import (
    NormalizedHolding, NormalizedPosition, NormalizedFunds,
    NormalizedQuote, NormalizedOptionChain, NormalizedCandle,
    NormalizedPortfolio, BrokerCode
)


class BaseBrokerDriver(ABC):
    """Abstract Broker Driver Interface."""

    def __init__(self, connection_id: str, account_id: str, access_token: str, api_key: str):
        self.connection_id = connection_id
        self.account_id = account_id
        self.access_token = access_token
        self.api_key = api_key

    @abstractmethod
    def get_broker_code(self) -> BrokerCode:
        """Returns unique broker code enum."""
        pass

    @abstractmethod
    async def get_profile(self) -> Dict[str, Any]:
        """Fetch user broker profile details."""
        pass

    @abstractmethod
    async def get_funds(self) -> NormalizedFunds:
        """Fetch available margins, cash, and collateral balance."""
        pass

    @abstractmethod
    async def get_holdings(self) -> List[NormalizedHolding]:
        """Fetch delivery holdings and map to normalized schema."""
        pass

    @abstractmethod
    async def get_positions(self) -> List[NormalizedPosition]:
        """Fetch intraday and F&O open positions."""
        pass

    @abstractmethod
    async def get_quote(self, quantview_symbol: str) -> NormalizedQuote:
        """Fetch normalized live quote for a symbol."""
        pass

    @abstractmethod
    async def get_historical_candles(
        self,
        quantview_symbol: str,
        interval: str,
        from_date: datetime,
        to_date: datetime
    ) -> List[NormalizedCandle]:
        """Fetch OHLCV historical candle data."""
        pass

    async def get_full_portfolio(self) -> NormalizedPortfolio:
        """Asynchronously compiles total portfolio snapshot."""
        funds, holdings, positions = await asyncio.gather(
            self.get_funds(),
            self.get_holdings(),
            self.get_positions()
        )

        total_investment = sum((h.investment_value for h in holdings), Decimal("0"))
        total_current = sum((h.current_value for h in holdings), Decimal("0"))
        total_holdings_pnl = sum((h.pnl for h in holdings), Decimal("0"))
        total_pos_pnl = sum((p.total_pnl for p in positions), Decimal("0"))
        total_pnl = total_holdings_pnl + total_pos_pnl

        pnl_pct = (total_pnl / total_investment * 100) if total_investment > 0 else Decimal("0")

        return NormalizedPortfolio(
            connection_id=self.connection_id,
            broker_code=self.get_broker_code(),
            account_id=self.account_id,
            total_investment=total_investment,
            total_current_value=total_current,
            total_pnl=total_pnl,
            total_pnl_percentage=pnl_pct,
            today_pnl=Decimal("0.0"),
            funds=funds,
            holdings=holdings,
            positions=positions
        )
