import asyncio
import json
import os
import websockets

from app.services.live_cache import LIVE_CACHE
from app.services.price_history import PRICE_HISTORY

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")

SYMBOL_MAP = {
    "BINANCE:BTCUSDT": "BTC/USD",
    "BINANCE:ETHUSDT": "ETH/USD",

    # FOREX
    "OANDA:EUR_USD": "EUR/USD",
    "OANDA:GBP_USD": "GBP/USD",
    "OANDA:USD_JPY": "USD/JPY",
    "OANDA:USD_CHF": "USD/CHF",
    "OANDA:AUD_USD": "AUD/USD",
    "OANDA:USD_CAD": "USD/CAD",
    "OANDA:NZD_USD": "NZD/USD",
    "OANDA:EUR_GBP": "EUR/GBP",
    "OANDA:EUR_JPY": "EUR/JPY",
    "OANDA:GBP_JPY": "GBP/JPY",
    "OANDA:EUR_AUD": "EUR/AUD",
    "OANDA:EUR_CAD": "EUR/CAD",
    "OANDA:CHF_JPY": "CHF/JPY",
    "OANDA:AUD_JPY": "AUD/JPY",
    "OANDA:CAD_JPY": "CAD/JPY",
    "OANDA:NZD_JPY": "NZD/JPY",

    # STOCKS
    "AAPL": "AAPL",
    "TSLA": "TSLA",
    "NVDA": "NVDA",
    "MSFT": "MSFT",
    "GOOGL": "GOOGL",
    "AMZN": "AMZN",
    "META": "META",
    "NFLX": "NFLX",
    "AMD": "AMD",
    "INTC": "INTC",
    "UBER": "UBER",
    "PLTR": "PLTR",
    "NIO": "NIO",
    "COIN": "COIN",
}


async def start_finnhub_ws():

    url = (
        f"wss://ws.finnhub.io"
        f"?token={FINNHUB_API_KEY}"
    )

    while True:

        try:

            async with websockets.connect(url) as ws:

                print("Finnhub websocket connected")

                for symbol in SYMBOL_MAP.keys():

                    await ws.send(json.dumps({
                        "type": "subscribe",
                        "symbol": symbol
                    }))

                async for message in ws:

                    data = json.loads(message)

                    if data.get("type") != "trade":
                        continue

                    for trade in data.get("data", []):

                        symbol = trade.get("s")

                        if symbol not in SYMBOL_MAP:
                            continue

                        mapped_symbol = SYMBOL_MAP[symbol]

                        price = float(
                            trade.get("p", 0)
                        )

                        LIVE_CACHE.setdefault(
                            mapped_symbol,
                            {}
                        )

                        LIVE_CACHE[mapped_symbol]["price"] = price
                        PRICE_HISTORY[
                            mapped_symbol
                        ].append(price)

        except Exception as e:

            print(f"Finnhub websocket error: {e}")

            await asyncio.sleep(5)