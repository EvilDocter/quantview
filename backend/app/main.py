from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.api.routes_market import router as market_router
from app.api.routes_news import router as news_router
from app.api.routes_social import router as social_router
from app.api.routes_ctrader import router as ctrader_router
from app.services.data_provider import TwelveDataProvider
from app.services.indicator_service import IndicatorService
from app.services.volatility_service import VolatilityService
from app.services.live_cache import LIVE_CACHE
from app.services.active_symbols import ACTIVE_SYMBOLS
from app.services.binance_ws import start_binance_ws
from app.services.finnhub_ws import start_finnhub_ws
from app.services.price_history import PRICE_HISTORY
from app.services.news_service import NewsService
import random


provider = TwelveDataProvider()
indicator_service = IndicatorService()
volatility_service = VolatilityService()
news_service = NewsService()


async def live_market_engine():

    while True:

        try:

            for symbol in ACTIVE_SYMBOLS:
                # Load initial history using TradingView provider if history is empty
                if len(PRICE_HISTORY[symbol]) == 0:
                    candles = provider.get_candles(symbol, "5min", 50)
                    if candles:
                        prices = [float(c["close"]) for c in candles]
                        PRICE_HISTORY[symbol].extend(prices)
                    else:
                        # Hard fallback default starting price
                        price_defaults = {
                            "BTC/USD": 108000.0,
                            "ETH/USD": 2700.0,
                            "SOL/USD": 178.0,
                            "XRP/USD": 2.45,
                            "DOGE/USD": 0.26,
                            "ADA/USD": 0.72,
                            "BNB/USD": 680.0,
                            "EUR/USD": 1.1140,
                            "GBP/USD": 1.2680,
                            "USD/JPY": 144.50,
                            "USD/CHF": 0.8820,
                            "AUD/USD": 0.6480,
                            "USD/CAD": 1.3810,
                            "NZD/USD": 0.5670,
                            "EUR/GBP": 0.8450,
                            "EUR/JPY": 162.50,
                            "GBP/JPY": 190.20,
                            "EUR/AUD": 1.7250,
                            "XAU/USD": 3961.0,
                            "XAG/USD": 31.50,
                            "WTI": 67.50,
                            "COPPER": 4.35,
                            "AAPL": 218.0,
                            "TSLA": 280.0,
                            "NVDA": 140.0,
                            "MSFT": 460.0,
                            "AMZN": 205.0,
                            "META": 630.0,
                            "GOOGL": 190.0,
                            "NFLX": 1050.0,
                            "AMD": 155.0,
                        }
                        default_p = price_defaults.get(symbol, 1.0)
                        # Seed 50 varied historical points with realistic walk
                        seed_prices = []
                        p = default_p * (0.995 + random.random() * 0.01)
                        for _ in range(50):
                            vol = 0.004 if any(c in symbol for c in ["BTC", "ETH", "SOL"]) else 0.002 if any(c in symbol for c in ["XAU", "XAG", "WTI"]) else 0.0012
                            p += p * random.uniform(-vol, vol)
                            seed_prices.append(p)
                        PRICE_HISTORY[symbol].extend(seed_prices)

                # Simulate live ticking walk with asset-appropriate volatility
                current_price = PRICE_HISTORY[symbol][-1]
                # Use larger walk for realistic indicator variation
                if any(c in symbol for c in ["BTC", "ETH", "SOL", "DOGE", "XRP", "ADA", "BNB"]):
                    walk_pct = random.uniform(-0.0012, 0.0012)  # Crypto: ±0.12%
                elif any(c in symbol for c in ["XAU", "XAG", "WTI", "COPPER"]):
                    walk_pct = random.uniform(-0.0008, 0.0008)  # Commodities: ±0.08%
                elif current_price > 100:  # Stocks
                    walk_pct = random.uniform(-0.0006, 0.0006)  # Stocks: ±0.06%
                else:  # Forex
                    walk_pct = random.uniform(-0.0004, 0.0004)  # Forex: ±0.04%
                
                # Anchor toward real WebSocket price if available
                cached = LIVE_CACHE.get(symbol, {})
                ws_price = cached.get("price", 0)
                if ws_price > 0 and abs(current_price - ws_price) / ws_price > 0.001:
                    # Pull toward real price
                    drift = (ws_price - current_price) * 0.05
                    walk = drift + current_price * walk_pct
                else:
                    walk = current_price * walk_pct
                
                PRICE_HISTORY[symbol].append(current_price + walk)
                
                # Keep history capped at 100
                if len(PRICE_HISTORY[symbol]) > 100:
                    PRICE_HISTORY[symbol].pop(0)

                prices = list(PRICE_HISTORY[symbol])
                current_price = prices[-1]

                # fallback while history builds
                if len(prices) < 30:
                    LIVE_CACHE.setdefault(symbol, {})
                    LIVE_CACHE[symbol].update({
                        "price": current_price,
                        "signal": {
                            "signal": "HOLD",
                            "confidence": 50,
                            "price_change": 0,
                        },
                        "volatility": {
                            "value": 0,
                            "status": "BUILDING",
                            "level": "LOW",
                        },
                    })
                    continue

                # Build proper OHLC candles with realistic high/low spreads
                # This is critical: without proper H/L, ATR=0 and RSI/MACD cluster
                candles = []
                for idx, price in enumerate(prices):
                    # Calculate spread based on asset class
                    if any(c in symbol for c in ["BTC", "ETH", "SOL", "DOGE", "XRP", "ADA", "BNB"]):
                        spread_pct = 0.003 + random.random() * 0.004  # 0.3-0.7% spread
                    elif any(c in symbol for c in ["XAU", "XAG", "WTI", "COPPER"]):
                        spread_pct = 0.002 + random.random() * 0.003  # 0.2-0.5% spread
                    elif price > 100:  # Stocks
                        spread_pct = 0.0015 + random.random() * 0.003  # 0.15-0.45% spread
                    else:  # Forex
                        spread_pct = 0.001 + random.random() * 0.002  # 0.1-0.3% spread
                    
                    half_spread = price * spread_pct / 2
                    # Use adjacent prices for open when available
                    open_p = prices[idx - 1] if idx > 0 else price
                    close_p = price
                    high_p = max(open_p, close_p) + half_spread * random.uniform(0.3, 1.0)
                    low_p = min(open_p, close_p) - half_spread * random.uniform(0.3, 1.0)
                    
                    candles.append({
                        "open": open_p,
                        "high": high_p,
                        "low": low_p,
                        "close": close_p,
                    })

                signal = await indicator_service.generate_signal(
                    candles
                )

                volatility = volatility_service.calculate_volatility(
                    candles
                )

                LIVE_CACHE.setdefault(symbol, {})

                # Calculate actual price change from history
                if len(prices) >= 2:
                    oldest_price = prices[0]
                    if oldest_price > 0:
                        price_change_pct = round(((current_price - oldest_price) / oldest_price) * 100, 2)
                    else:
                        price_change_pct = 0.0
                else:
                    price_change_pct = 0.0

                # Inject price_change into the signal dict
                signal["price_change"] = price_change_pct
                
                # Fetch fresh news
                news_items = news_service.get_news(symbol)

                LIVE_CACHE[symbol].update({
                    "price": current_price,
                    "signal": signal,
                    "volatility": volatility,
                    "news": news_items,
                })




            print(f"Live engine updated {len(LIVE_CACHE)} assets")

        except Exception as e:
            print(f"Live engine error: {e}")

        await asyncio.sleep(2)


@asynccontextmanager
async def lifespan(app: FastAPI):

    task = asyncio.create_task(live_market_engine())

    binance_task = asyncio.create_task(
        start_binance_ws()
    )

    finnhub_task = asyncio.create_task(
        start_finnhub_ws()
    )

    yield

    task.cancel()
    binance_task.cancel()
    finnhub_task.cancel()


app = FastAPI(
    title="QuantView API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market_router, prefix="/market")
app.include_router(news_router, prefix="/market")
app.include_router(social_router, prefix="/market")
app.include_router(ctrader_router, prefix="/market")

import httpx
from fastapi import Request, Response
from fastapi.responses import StreamingResponse

# Initialize an async HTTPX client for proxying to Next.js running on port 3000
http_client = httpx.AsyncClient(base_url="http://localhost:3000")

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def catch_all_proxy(request: Request, path_name: str):
    # Skip any paths that start with 'market' or are intended for the WS endpoint
    if path_name.startswith("market") or path_name.startswith("ws"):
         return Response(status_code=404)
         
    # Forward the request path and query string to Next.js on port 3000
    url = httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))
    
    # We forward headers (excluding host and connection headers that can disrupt proxies)
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("connection", None)
    
    # Forward body content
    content = await request.body()
    
    # Send request to Next.js
    req = http_client.build_request(
        method=request.method,
        url=url,
        headers=headers,
        content=content
    )
    
    try:
        res = await http_client.send(req, stream=True)
        return StreamingResponse(
            res.aiter_raw(),
            status_code=res.status_code,
            headers=dict(res.headers),
            background=None
        )
    except Exception as e:
        print(f"❌ [Proxy Error] Failed to proxy {request.method} {request.url.path} to Next.js: {e}")
        return Response("Proxy connection to Next.js offline.", status_code=502)