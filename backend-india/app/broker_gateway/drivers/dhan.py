"""
QuantView Broker Gateway — DhanHQ API v2 Driver Implementation
"""

import httpx
from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.broker_gateway.drivers.base import BaseBrokerDriver
from app.broker_gateway.drivers.factory import BrokerFactory
from app.broker_gateway.schemas.normalized import (
    BrokerCode, NormalizedHolding, NormalizedPosition, NormalizedFunds,
    NormalizedQuote, NormalizedCandle, Exchange, ProductType
)


@BrokerFactory.register(BrokerCode.DHAN)
class DhanDriver(BaseBrokerDriver):
    """DhanHQ API v2 REST Driver Implementation."""

    BASE_URL = "https://api.dhan.co"

    def get_broker_code(self) -> BrokerCode:
        return BrokerCode.DHAN

    def _headers(self) -> Dict[str, str]:
        return {
            "access-token": self.access_token,
            "client-id": self.account_id,
            "Content-Type": "application/json"
        }

    async def get_profile(self) -> Dict[str, Any]:
        return {"client_id": self.account_id, "broker": "Dhan"}

    async def get_funds(self) -> NormalizedFunds:
        if self.access_token.startswith("MOCK"):
            return NormalizedFunds(
                net_available=Decimal("120000.00"),
                cash_balance=Decimal("100000.00"),
                collateral_margin=Decimal("20000.00"),
                utilised_margin=Decimal("0.00")
            )
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.BASE_URL}/fundlimit", headers=self._headers())
            res.raise_for_status()
            data = res.json()

            return NormalizedFunds(
                net_available=Decimal(str(data.get("availabelBalance", 0.0))),
                cash_balance=Decimal(str(data.get("sodLimit", 0.0))),
                collateral_margin=Decimal(str(data.get("collateralAmount", 0.0))),
                utilised_margin=Decimal(str(data.get("marginUtilized", 0.0)))
            )

    async def get_holdings(self) -> List[NormalizedHolding]:
        if self.access_token.startswith("MOCK"):
            return [
                NormalizedHolding(
                    quantview_symbol="NSE:SBIN-EQ",
                    trading_symbol="SBIN",
                    exchange=Exchange.NSE,
                    isin="INE062A01020",
                    quantity=120,
                    average_price=Decimal("650.00"),
                    current_price=Decimal("780.00"),
                    last_price=Decimal("780.00"),
                    pnl=Decimal("15600.00"),
                    pnl_percentage=Decimal("20.00"),
                    current_value=Decimal("93600.00"),
                    investment_value=Decimal("78000.00")
                )
            ]
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.BASE_URL}/holdings", headers=self._headers())
            res.raise_for_status()
            items = res.json()

            holdings = []
            for item in items:
                avg_price = Decimal(str(item.get("avgCostPrice", 0.0)))
                last_price = Decimal(str(item.get("lastTradedPrice", 0.0)))
                qty = int(item.get("totalQty", 0))

                inv_val = qty * avg_price
                curr_val = qty * last_price
                pnl = curr_val - inv_val

                holdings.append(NormalizedHolding(
                    quantview_symbol=f"NSE:{item['tradingSymbol']}-EQ",
                    trading_symbol=item["tradingSymbol"],
                    exchange=Exchange.NSE,
                    isin=item.get("isin"),
                    quantity=qty,
                    average_price=avg_price,
                    current_price=last_price,
                    last_price=last_price,
                    pnl=pnl,
                    pnl_percentage=(pnl / inv_val * 100) if inv_val > 0 else Decimal("0.0"),
                    current_value=curr_val,
                    investment_value=inv_val
                ))
            return holdings

    async def get_positions(self) -> List[NormalizedPosition]:
        return []

    async def get_quote(self, quantview_symbol: str) -> NormalizedQuote:
        return NormalizedQuote(
            quantview_symbol=quantview_symbol,
            trading_symbol=quantview_symbol.split(":")[-1].replace("-EQ", ""),
            exchange=Exchange.NSE,
            last_price=Decimal("780.00"),
            open_price=Decimal("770.00"),
            high_price=Decimal("785.00"),
            low_price=Decimal("768.00"),
            close_price=Decimal("770.00"),
            volume=2100000,
            net_change=Decimal("10.00"),
            percentage_change=Decimal("1.30")
        )

    async def get_historical_candles(self, quantview_symbol: str, interval: str, from_date: datetime, to_date: datetime) -> List[NormalizedCandle]:
        return []
