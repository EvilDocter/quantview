import asyncio
import json
import websockets

from app.services.live_cache import LIVE_CACHE
from app.services.price_history import PRICE_HISTORY

BINANCE_STREAMS = [
    "btcusdt",
    "ethusdt",
    "solusdt",
    "xrpusdt",
    "dogeusdt",
    "adausdt",
    "bnbusdt",
    "avaxusdt",
    "dotusdt",
    "linkusdt",
    "maticusdt",
]

SYMBOL_MAP = {
    "BTCUSDT": "BTC/USD",
    "ETHUSDT": "ETH/USD",
    "SOLUSDT": "SOL/USD",
    "XRPUSDT": "XRP/USD",
    "DOGEUSDT": "DOGE/USD",
    "ADAUSDT": "ADA/USD",
    "BNBUSDT": "BNB/USD",
    "AVAXUSDT": "AVAX/USD",
    "DOTUSDT": "DOT/USD",
    "LINKUSDT": "LINK/USD",
    "MATICUSDT": "MATIC/USD",
}


async def start_binance_ws():

    stream_names = "/".join(
        [f"{s}@ticker" for s in BINANCE_STREAMS]
    )

    url = (
        f"wss://stream.binance.com:9443/stream?streams="
        f"{stream_names}"
    )

    while True:

        try:

            async with websockets.connect(url) as ws:

                print("Binance websocket connected")

                async for message in ws:

                    data = json.loads(message)

                    payload = data.get("data", {})

                    symbol = payload.get("s")

                    if symbol not in SYMBOL_MAP:
                        continue

                    mapped_symbol = SYMBOL_MAP[symbol]

                    price = float(payload.get("c", 0))

                    LIVE_CACHE.setdefault(
                        mapped_symbol,
                        {}
                    )

                    LIVE_CACHE[mapped_symbol]["price"] = price
                    PRICE_HISTORY[
                        mapped_symbol
                    ].append(price)

        except Exception as e:
            print(f"Binance websocket error: {e}")

            await asyncio.sleep(5)