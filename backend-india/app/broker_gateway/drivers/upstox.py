"""
QuantView Broker Gateway — Upstox API v2 Driver Implementation
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


@BrokerFactory.register(BrokerCode.UPSTOX)
class UpstoxDriver(BaseBrokerDriver):
    """Upstox API v2 OAuth Driver Implementation."""

    BASE_URL = "https://api.upstox.com/v2"

    def get_broker_code(self) -> BrokerCode:
        return BrokerCode.UPSTOX

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

    async def get_profile(self) -> Dict[str, Any]:
        return {"user_id": self.account_id, "user_name": "Upstox User", "broker": "Upstox"}

    async def get_funds(self) -> NormalizedFunds:
        if self.access_token.startswith("MOCK"):
            return NormalizedFunds(
                net_available=Decimal("95000.00"),
                cash_balance=Decimal("90000.00"),
                utilised_margin=Decimal("5000.00")
            )
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.BASE_URL}/user/get-funds-and-margin", headers=self._headers())
            res.raise_for_status()
            equity_data = res.json().get("data", {}).get("equity", {})

            return NormalizedFunds(
                net_available=Decimal(str(equity_data.get("available_margin", 0.0))),
                cash_balance=Decimal(str(equity_data.get("used_margin", 0.0))),
                utilised_margin=Decimal(str(equity_data.get("used_margin", 0.0)))
            )

    async def get_holdings(self) -> List[NormalizedHolding]:
        if self.access_token.startswith("MOCK"):
            return [
                NormalizedHolding(
                    quantview_symbol="NSE:ICICIBANK-EQ",
                    trading_symbol="ICICIBANK",
                    exchange=Exchange.NSE,
                    isin="INE090A01021",
                    quantity=75,
                    average_price=Decimal("980.00"),
                    current_price=Decimal("1180.00"),
                    last_price=Decimal("1180.00"),
                    pnl=Decimal("15000.00"),
                    pnl_percentage=Decimal("20.41"),
                    current_value=Decimal("88500.00"),
                    investment_value=Decimal("73500.00")
                )
            ]
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.BASE_URL}/portfolio/long-term-holdings", headers=self._headers())
            res.raise_for_status()
            items = res.json().get("data", [])

            holdings = []
            for item in items:
                avg_price = Decimal(str(item.get("average_price", 0.0)))
                last_price = Decimal(str(item.get("last_price", 0.0)))
                qty = int(item.get("quantity", 0))

                inv_val = qty * avg_price
                curr_val = qty * last_price
                pnl = Decimal(str(item.get("pnl", 0.0)))

                holdings.append(NormalizedHolding(
                    quantview_symbol=f"NSE:{item['trading_symbol']}-EQ",
                    trading_symbol=item["trading_symbol"],
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
            last_price=Decimal("1180.00"),
            open_price=Decimal("1170.00"),
            high_price=Decimal("1190.00"),
            low_price=Decimal("1165.00"),
            close_price=Decimal("1170.00"),
            volume=1100000,
            net_change=Decimal("10.00"),
            percentage_change=Decimal("0.85")
        )

    async def get_historical_candles(self, quantview_symbol: str, interval: str, from_date: datetime, to_date: datetime) -> List[NormalizedCandle]:
        return []
