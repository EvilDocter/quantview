"""
QuantView Broker Gateway — Master Symbol Registry Service

Translates QuantView standard symbols (e.g. NSE:RELIANCE-EQ)
into individual broker-specific instrument tokens and symbols.
"""

from typing import Dict
from app.broker_gateway.schemas.normalized import BrokerCode


class SymbolRegistryService:
    """High-speed cross-broker symbol token resolution service."""

    # Built-in symbol token map for key Indian market equities & indices
    SYMBOL_MAP: Dict[str, Dict[str, str]] = {
        "NSE:RELIANCE-EQ": {
            "zerodha": "738561",
            "angel": "2885",
            "fyers": "NSE:RELIANCE-EQ",
            "upstox": "NSE_EQ|INE002A01018",
            "dhan": "1333",
        },
        "NSE:TCS-EQ": {
            "zerodha": "2953217",
            "angel": "11536",
            "fyers": "NSE:TCS-EQ",
            "upstox": "NSE_EQ|INE467B01029",
            "dhan": "11536",
        },
        "NSE:INFY-EQ": {
            "zerodha": "408065",
            "angel": "1594",
            "fyers": "NSE:INFY-EQ",
            "upstox": "NSE_EQ|INE009A01021",
            "dhan": "1594",
        },
        "NSE:HDFCBANK-EQ": {
            "zerodha": "341249",
            "angel": "1333",
            "fyers": "NSE:HDFCBANK-EQ",
            "upstox": "NSE_EQ|INE040A01034",
            "dhan": "1333",
        },
        "NSE:TATAMOTORS-EQ": {
            "zerodha": "884737",
            "angel": "3456",
            "fyers": "NSE:TATAMOTORS-EQ",
            "upstox": "NSE_EQ|INE155A01022",
            "dhan": "3456",
        },
    }

    async def to_broker_token(self, quantview_symbol: str, broker: BrokerCode) -> str:
        """Translates QuantView Symbol -> Broker Token."""
        broker_str = broker.value if isinstance(broker, BrokerCode) else str(broker)
        symbol_info = self.SYMBOL_MAP.get(quantview_symbol, {})
        return symbol_info.get(broker_str, quantview_symbol)


symbol_registry = SymbolRegistryService()
