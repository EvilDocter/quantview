"""
QuantView Broker Gateway — FYERS API v3 Driver Implementation
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


@BrokerFactory.register(BrokerCode.FYERS)
class FYERSDriver(BaseBrokerDriver):
    """FYERS API v3 Driver Implementation."""

    BASE_URL = "https://api-v3.fyers.in/api/v3"

    def get_broker_code(self) -> BrokerCode:
        return BrokerCode.FYERS

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"{self.api_key}:{self.access_token}"}

    async def get_profile(self) -> Dict[str, Any]:
        return {"client_id": self.account_id, "name": "FYERS User", "broker": "FYERS"}

    async def get_funds(self) -> NormalizedFunds:
        if self.access_token.startswith("MOCK"):
            return NormalizedFunds(
                net_available=Decimal("180000.00"),
                cash_balance=Decimal("150000.00"),
                collateral_margin=Decimal("30000.00"),
                utilised_margin=Decimal("10000.00")
            )
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.BASE_URL}/funds", headers=self._headers())
            res.raise_for_status()
            data = res.json().get("fund_limit", [])
            fund_dict = {f["title"]: f["amount"] for f in data}

            return NormalizedFunds(
                net_available=Decimal(str(fund_dict.get("Net Available", 0.0))),
                cash_balance=Decimal(str(fund_dict.get("Total Balance", 0.0))),
                collateral_margin=Decimal(str(fund_dict.get("Collateral Margin", 0.0)))
            )

    async def get_holdings(self) -> List[NormalizedHolding]:
        if self.access_token.startswith("MOCK"):
            return [
                NormalizedHolding(
                    quantview_symbol="NSE:BHARTIARTL-EQ",
                    trading_symbol="BHARTIARTL",
                    exchange=Exchange.NSE,
                    quantity=80,
                    average_price=Decimal("1200.00"),
                    current_price=Decimal("1450.00"),
                    last_price=Decimal("1450.00"),
                    pnl=Decimal("20000.00"),
                    pnl_percentage=Decimal("20.83"),
                    current_value=Decimal("116000.00"),
                    investment_value=Decimal("96000.00")
                )
            ]
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.BASE_URL}/holdings", headers=self._headers())
            res.raise_for_status()
            items = res.json().get("holdings", [])

            holdings = []
            for item in items:
                avg_price = Decimal(str(item.get("costPrice", 0.0)))
                last_price = Decimal(str(item.get("marketVal", 0.0))) / Decimal(str(max(item.get("quantity", 1), 1)))
                qty = int(item.get("quantity", 0))

                inv_val = Decimal(str(item.get("totalCost", 0.0)))
                curr_val = Decimal(str(item.get("marketVal", 0.0)))
                pnl = curr_val - inv_val

                holdings.append(NormalizedHolding(
                    quantview_symbol=f"NSE:{item['symbol']}-EQ",
                    trading_symbol=item["symbol"],
                    exchange=Exchange.NSE,
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
            last_price=Decimal("1450.00"),
            open_price=Decimal("1440.00"),
            high_price=Decimal("1460.00"),
            low_price=Decimal("1435.00"),
            close_price=Decimal("1440.00"),
            volume=500000,
            net_change=Decimal("10.00"),
            percentage_change=Decimal("0.69")
        )

    async def get_historical_candles(self, quantview_symbol: str, interval: str, from_date: datetime, to_date: datetime) -> List[NormalizedCandle]:
        return []
