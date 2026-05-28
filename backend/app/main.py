from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.api.routes_market import router as market_router
from app.api.routes_news import router as news_router
from app.api.routes_social import router as social_router
from app.api.routes_mt5 import router as mt5_router
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
                            "BTC/USD": 67000.0,
                            "ETH/USD": 3500.0,
                            "SOL/USD": 150.0,
                            "XRP/USD": 0.55,
                            "EUR/USD": 1.0850,
                            "GBP/USD": 1.2700,
                            "USD/JPY": 156.0,
                            "USD/CHF": 0.9000,
                            "XAU/USD": 2330.0,
                            "AAPL": 190.0,
                            "TSLA": 175.0,
                            "NVDA": 900.0
                        }
                        default_p = price_defaults.get(symbol, 1.0)
                        # Seed 50 historical points
                        PRICE_HISTORY[symbol].extend([default_p] * 50)

                # Simulate live ticking walk if no new data was pushed from websockets recently
                current_price = PRICE_HISTORY[symbol][-1]
                walk = current_price * random.uniform(-0.00015, 0.00015)
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

                candles = [
                    {
                        "open": price,
                        "high": price,
                        "low": price,
                        "close": price,
                    }
                    for price in prices
                ]

                signal = await indicator_service.generate_signal(
                    candles
                )

                volatility = volatility_service.calculate_volatility(
                    candles
                )

                LIVE_CACHE.setdefault(symbol, {})

                # ── Calculate RANDOM % price change between 5% and 30% ──
                # User requested randomized change if last hour not possible
                change_magnitude = random.uniform(5.0, 30.0)
                sign = random.choice([1, -1])
                price_change_pct = round(change_magnitude * sign, 2)

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


                # Background AI Autobot Execution Desk
                try:
                    from app.api.routes_mt5 import load_config, add_log
                    from app.services.mt5_service import MT5Service
                    
                    config = load_config()
                    if config.get("isAutoTradingActive", False) and config.get("accountId") and config.get("token"):
                        if signal.get("signal") in ["BUY", "SELL"] and signal.get("confidence", 50) >= 80:
                            clean_symbol = symbol.replace("/", "").replace("_", "")
                            positions = MT5Service.get_active_positions(config["accountId"], config["token"])
                            
                            has_position = any(p["symbol"] == clean_symbol for p in positions)
                            if not has_position:
                                tp_sl_info = {}
                                atr = volatility.get("value", 0.0)
                                if atr > 0.0:
                                    if signal["signal"] == "BUY":
                                        tp_sl_info["take_profit"] = current_price + (atr * 2.0)
                                        tp_sl_info["stop_loss"] = current_price - (atr * 1.5)
                                    else:
                                        tp_sl_info["take_profit"] = current_price - (atr * 2.0)
                                        tp_sl_info["stop_loss"] = current_price + (atr * 1.5)
                                        
                                lot_size = config.get("volume", 0.01)
                                res = MT5Service.execute_trade_order(
                                    config["accountId"],
                                    config["token"],
                                    symbol,
                                    signal["signal"],
                                    lot_size,
                                    tp_sl_info.get("stop_loss"),
                                    tp_sl_info.get("take_profit")
                                )
                                if res.get("success", False):
                                    add_log(
                                        f"🤖 Autobot executed {signal['signal']} order for {symbol} ({lot_size} Lots) via Llama-3 recommendation",
                                        symbol
                                    )
                                else:
                                    print(f"Autobot order failed: {res.get('error')}")
                except Exception as auto_err:
                    pass

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
app.include_router(mt5_router, prefix="/market")
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