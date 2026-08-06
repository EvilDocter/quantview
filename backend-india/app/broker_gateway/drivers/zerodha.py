"""
QuantView Broker Gateway — Zerodha Kite Driver Implementation
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
from app.broker_gateway.core.symbol_registry import symbol_registry


@BrokerFactory.register(BrokerCode.ZERODHA)
class ZerodhaDriver(BaseBrokerDriver):
    """Zerodha Kite Connect v3 REST API Driver Implementation."""

    BASE_URL = "https://api.kite.trade"

    def get_broker_code(self) -> BrokerCode:
        return BrokerCode.ZERODHA

    def _headers(self) -> Dict[str, str]:
        return {
            "X-Kite-Version": "3",
            "Authorization": f"token {self.api_key}:{self.access_token}"
        }

    async def get_profile(self) -> Dict[str, Any]:
        if self.access_token.startswith("MOCK"):
            return {"user_id": self.account_id, "user_name": "Demo User", "email": "demo@quantview.in"}
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.BASE_URL}/user/profile", headers=self._headers())
            res.raise_for_status()
            return res.json().get("data", {})

    async def get_funds(self) -> NormalizedFunds:
        if self.access_token.startswith("MOCK"):
            return NormalizedFunds(
                net_available=Decimal("150000.00"),
                cash_balance=Decimal("120000.00"),
                collateral_margin=Decimal("30000.00"),
                utilised_margin=Decimal("15000.00")
            )
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.BASE_URL}/user/margins", headers=self._headers())
            res.raise_for_status()
            equity_data = res.json().get("data", {}).get("equity", {})

            return NormalizedFunds(
                net_available=Decimal(str(equity_data.get("net", 0.0))),
                cash_balance=Decimal(str(equity_data.get("cash", 0.0))),
                collateral_margin=Decimal(str(equity_data.get("collateral", 0.0))),
                utilised_margin=Decimal(str(equity_data.get("utilised", {}).get("debits", 0.0)))
            )

    async def get_holdings(self) -> List[NormalizedHolding]:
        if self.access_token.startswith("MOCK"):
            return [
                NormalizedHolding(
                    quantview_symbol="NSE:RELIANCE-EQ",
                    trading_symbol="RELIANCE",
                    exchange=Exchange.NSE,
                    isin="INE002A01018",
                    quantity=50,
                    average_price=Decimal("2200.00"),
                    current_price=Decimal("2450.00"),
                    last_price=Decimal("2450.00"),
                    pnl=Decimal("12500.00"),
                    pnl_percentage=Decimal("11.36"),
                    current_value=Decimal("122500.00"),
                    investment_value=Decimal("110000.00")
                ),
                NormalizedHolding(
                    quantview_symbol="NSE:INFY-EQ",
                    trading_symbol="INFY",
                    exchange=Exchange.NSE,
                    isin="INE009A01021",
                    quantity=100,
                    average_price=Decimal("1400.00"),
                    current_price=Decimal("1560.00"),
                    last_price=Decimal("1560.00"),
                    pnl=Decimal("16000.00"),
                    pnl_percentage=Decimal("11.43"),
                    current_value=Decimal("156000.00"),
                    investment_value=Decimal("140000.00")
                )
            ]
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.BASE_URL}/portfolio/holdings", headers=self._headers())
            res.raise_for_status()
            items = res.json().get("data", [])

            holdings = []
            for item in items:
                symbol = f"NSE:{item['tradingsymbol']}-EQ"
                avg_price = Decimal(str(item.get("average_price", 0.0)))
                last_price = Decimal(str(item.get("last_price", 0.0)))
                qty = int(item.get("quantity", 0))

                inv_val = qty * avg_price
                curr_val = qty * last_price
                pnl = Decimal(str(item.get("pnl", 0.0)))
                pnl_pct = (pnl / inv_val * 100) if inv_val > 0 else Decimal("0.0")

                holdings.append(NormalizedHolding(
                    quantview_symbol=symbol,
                    trading_symbol=item["tradingsymbol"],
                    exchange=Exchange.NSE,
                    isin=item.get("isin"),
                    quantity=qty,
                    t1_quantity=int(item.get("t1_quantity", 0)),
                    average_price=avg_price,
                    current_price=last_price,
                    last_price=last_price,
                    pnl=pnl,
                    pnl_percentage=pnl_pct,
                    current_value=curr_val,
                    investment_value=inv_val
                ))
            return holdings

    async def get_positions(self) -> List[NormalizedPosition]:
        if self.access_token.startswith("MOCK"):
            return [
                NormalizedPosition(
                    quantview_symbol="NSE:TATAMOTORS-EQ",
                    trading_symbol="TATAMOTORS",
                    exchange=Exchange.NSE,
                    product=ProductType.MIS,
                    quantity=200,
                    buy_price=Decimal("945.00"),
                    sell_price=Decimal("0.00"),
                    last_price=Decimal("980.50"),
                    realised_pnl=Decimal("0.00"),
                    unrealised_pnl=Decimal("7100.00"),
                    total_pnl=Decimal("7100.00")
                )
            ]
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.BASE_URL}/portfolio/positions", headers=self._headers())
            res.raise_for_status()
            net_positions = res.json().get("data", {}).get("net", [])

            positions = []
            for item in net_positions:
                symbol = f"{item['exchange']}:{item['tradingsymbol']}"
                qty = int(item.get("quantity", 0))
                positions.append(NormalizedPosition(
                    quantview_symbol=symbol,
                    trading_symbol=item["tradingsymbol"],
                    exchange=Exchange(item["exchange"]),
                    product=ProductType.NRML if item.get("product") == "NRML" else ProductType.MIS,
                    quantity=qty,
                    buy_price=Decimal(str(item.get("buy_price", 0.0))),
                    sell_price=Decimal(str(item.get("sell_price", 0.0))),
                    last_price=Decimal(str(item.get("last_price", 0.0))),
                    realised_pnl=Decimal(str(item.get("realised", 0.0))),
                    unrealised_pnl=Decimal(str(item.get("unrealised", 0.0))),
                    total_pnl=Decimal(str(item.get("m2m", 0.0)))
                ))
            return positions

    async def get_quote(self, quantview_symbol: str) -> NormalizedQuote:
        z_token = await symbol_registry.to_broker_token(quantview_symbol, BrokerCode.ZERODHA)
        if self.access_token.startswith("MOCK"):
            return NormalizedQuote(
                quantview_symbol=quantview_symbol,
                trading_symbol=quantview_symbol.split(":")[-1].replace("-EQ", ""),
                exchange=Exchange.NSE,
                last_price=Decimal("2450.00"),
                open_price=Decimal("2420.00"),
                high_price=Decimal("2465.00"),
                low_price=Decimal("2410.00"),
                close_price=Decimal("2400.00"),
                volume=1250000,
                net_change=Decimal("50.00"),
                percentage_change=Decimal("2.08")
            )
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.BASE_URL}/quote?i={z_token}", headers=self._headers())
            res.raise_for_status()
            q = res.json().get("data", {}).get(z_token, {})

            return NormalizedQuote(
                quantview_symbol=quantview_symbol,
                trading_symbol=str(q.get("instrument_token", "")),
                exchange=Exchange.NSE,
                last_price=Decimal(str(q.get("last_price", 0.0))),
                open_price=Decimal(str(q.get("ohlc", {}).get("open", 0.0))),
                high_price=Decimal(str(q.get("ohlc", {}).get("high", 0.0))),
                low_price=Decimal(str(q.get("ohlc", {}).get("low", 0.0))),
                close_price=Decimal(str(q.get("ohlc", {}).get("close", 0.0))),
                volume=int(q.get("volume", 0)),
                net_change=Decimal(str(q.get("net_change", 0.0))),
                percentage_change=Decimal(str(q.get("net_change", 0.0)))
            )

    async def get_historical_candles(self, quantview_symbol: str, interval: str, from_date: datetime, to_date: datetime) -> List[NormalizedCandle]:
        return []
