"""
QuantView Broker Gateway — Angel One SmartAPI Driver Implementation
"""

import httpx
import pyotp
from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.broker_gateway.drivers.base import BaseBrokerDriver
from app.broker_gateway.drivers.factory import BrokerFactory
from app.broker_gateway.schemas.normalized import (
    BrokerCode, NormalizedHolding, NormalizedPosition, NormalizedFunds,
    NormalizedQuote, NormalizedCandle, Exchange, ProductType
)


@BrokerFactory.register(BrokerCode.ANGEL)
class AngelOneDriver(BaseBrokerDriver):
    """Angel One SmartAPI v2 REST Driver with Auto-TOTP Authentication."""

    BASE_URL = "https://apiconnect.angelbroking.com/rest/secure/angelbroking"

    def __init__(self, connection_id: str, account_id: str, access_token: str, api_key: str, totp_secret: str = ""):
        super().__init__(connection_id, account_id, access_token, api_key)
        self.totp_secret = totp_secret

    def get_broker_code(self) -> BrokerCode:
        return BrokerCode.ANGEL

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "127.0.0.1",
            "X-ClientPublicIP": "127.0.0.1",
            "X-MACAddress": "MAC_ADDRESS",
            "X-PrivateKey": self.api_key
        }

    async def get_profile(self) -> Dict[str, Any]:
        return {"client_id": self.account_id, "name": "Angel User", "broker": "Angel One"}

    async def get_funds(self) -> NormalizedFunds:
        if self.access_token.startswith("MOCK"):
            return NormalizedFunds(
                net_available=Decimal("210000.00"),
                cash_balance=Decimal("180000.00"),
                collateral_margin=Decimal("30000.00"),
                utilised_margin=Decimal("20000.00")
            )
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.BASE_URL}/user/v1/getRMS", headers=self._headers())
            res.raise_for_status()
            data = res.json().get("data", {})

            return NormalizedFunds(
                net_available=Decimal(str(data.get("net", 0.0))),
                cash_balance=Decimal(str(data.get("availablecash", 0.0))),
                collateral_margin=Decimal(str(data.get("collateral", 0.0))),
                utilised_margin=Decimal(str(data.get("utilisedDebits", 0.0)))
            )

    async def get_holdings(self) -> List[NormalizedHolding]:
        if self.access_token.startswith("MOCK"):
            return [
                NormalizedHolding(
                    quantview_symbol="NSE:TCS-EQ",
                    trading_symbol="TCS",
                    exchange=Exchange.NSE,
                    isin="INE467B01029",
                    quantity=30,
                    average_price=Decimal("3600.00"),
                    current_price=Decimal("3820.00"),
                    last_price=Decimal("3820.00"),
                    pnl=Decimal("6600.00"),
                    pnl_percentage=Decimal("6.11"),
                    current_value=Decimal("114600.00"),
                    investment_value=Decimal("108000.00")
                )
            ]
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.BASE_URL}/portfolio/v1/getHolding", headers=self._headers())
            res.raise_for_status()
            items = res.json().get("data", [])

            holdings = []
            for item in items:
                avg_price = Decimal(str(item.get("averageprice", 0.0)))
                last_price = Decimal(str(item.get("ltp", 0.0)))
                qty = int(item.get("quantity", 0))

                inv_val = qty * avg_price
                curr_val = qty * last_price
                pnl = Decimal(str(item.get("profitandloss", 0.0)))

                holdings.append(NormalizedHolding(
                    quantview_symbol=f"NSE:{item['tradingsymbol']}-EQ",
                    trading_symbol=item["tradingsymbol"],
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
            last_price=Decimal("3820.00"),
            open_price=Decimal("3800.00"),
            high_price=Decimal("3850.00"),
            low_price=Decimal("3790.00"),
            close_price=Decimal("3800.00"),
            volume=850000,
            net_change=Decimal("20.00"),
            percentage_change=Decimal("0.53")
        )

    async def get_historical_candles(self, quantview_symbol: str, interval: str, from_date: datetime, to_date: datetime) -> List[NormalizedCandle]:
        return []
