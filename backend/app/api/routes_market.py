from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import time
import asyncio
from app.services.data_provider import TwelveDataProvider
from app.services.indicator_service import IndicatorService
from app.services.volatility_service import VolatilityService
from app.services.forexfactory_service import ForexFactoryService
from app.services.positioning_service import PositioningService
from app.services.macro_news_service import MacroNewsService
from app.services.market_analysis_service import MarketAnalysisService
from app.services.signal_service import SignalService
from app.services.live_cache import LIVE_CACHE
from app.services.active_symbols import ACTIVE_SYMBOLS

router = APIRouter()
provider = TwelveDataProvider()
indicator_service = IndicatorService()
volatility_service = VolatilityService()
forexfactory_service = ForexFactoryService()
positioning_service = PositioningService()
macro_news_service = MacroNewsService()
market_analysis_service = MarketAnalysisService()
signal_service = SignalService()

ROUTE_CACHE = {}
ROUTE_CACHE_TTL = 30


def get_cached_route(key: str):
    if key in ROUTE_CACHE:
        data, ts = ROUTE_CACHE[key]

        if time.time() - ts < ROUTE_CACHE_TTL:
            return data

    return None


def set_cached_route(key: str, value):
    ROUTE_CACHE[key] = (value, time.time())

@router.get("/candles")
def get_candles(symbol: str = "EUR/USD", interval: str = "5min"):
    data = provider.get_candles(symbol, interval)

    # Ensure data exists
    if not data:
        return {
            "symbol": symbol,
            "data": []
        }

    # Convert values to float (remove any rounding issues)
    for candle in data:
        candle["open"] = float(candle["open"])
        candle["high"] = float(candle["high"])
        candle["low"] = float(candle["low"])
        candle["close"] = float(candle["close"])

    # Sort candles oldest -> newest
    data.sort(key=lambda x: x["datetime"])

    # Remove duplicate timestamps (important for chart stability)
    seen = set()
    cleaned = []
    for c in data:
        if c["datetime"] not in seen:
            cleaned.append(c)
            seen.add(c["datetime"])

    return {
        "symbol": symbol,
        "data": cleaned
    }


@router.get("/indicators")
def get_indicators(symbol: str = "EUR/USD", interval: str = "5min"):
    candles = provider.get_candles(symbol, interval)
    latest_close = 0
    previous_close = 0

    if candles and len(candles) >= 2:
        latest_close = float(candles[-1].get("close", 0))
        previous_close = float(candles[-2].get("close", 0))
        current_price = latest_close
    data = indicator_service.calculate_indicators(candles)

    return {
        "symbol": symbol,
        "indicators": data
    }


# New /signal endpoint
@router.get("/signal")
async def get_signal(symbol: str = "EUR/USD", interval: str = "5min"):
    cache_key = f"signal_{symbol}_{interval}"

    cached = get_cached_route(cache_key)

    if cached:
        return cached
    live_data = LIVE_CACHE.get(symbol)

    candles = provider.get_candles(symbol, interval)

    current_price = 0
    latest_close = 0
    previous_close = 0

    if candles and len(candles) >= 2:
        latest_close = float(candles[-1].get("close", 0))
        previous_close = float(candles[-2].get("close", 0))
        current_price = latest_close

    elif candles and len(candles) == 1:
        current_price = float(candles[-1].get("close", 0))
        latest_close = current_price
        previous_close = current_price

    signal_data = (
        live_data.get("signal")
        if live_data and live_data.get("signal")
        else await indicator_service.generate_signal(candles)
    )

    # real live price movement
    if previous_close > 0:
        calculated_change = round(
            ((latest_close - previous_close) / previous_close) * 100,
            2
        )

        signal_data["price_change"] = calculated_change
    else:
        signal_data["price_change"] = 0

    response = {
        "symbol": symbol,
        "interval": interval,
        "price": current_price,
        **signal_data
    }

    set_cached_route(cache_key, response)

    return response

@router.get("/volatility")
def get_volatility(symbol: str = "EUR/USD", interval: str = "5min"):
    cache_key = f"volatility_{symbol}_{interval}"

    cached = get_cached_route(cache_key)

    if cached:
        return cached
    live_data = LIVE_CACHE.get(symbol)

    candles = provider.get_candles(symbol, interval)

    volatility = (
        live_data.get("volatility")
        if live_data and live_data.get("volatility")
        else volatility_service.calculate_volatility(candles)
    )
    response = {
        "symbol": symbol,
        "volatility": volatility
    }

    set_cached_route(cache_key, response)

    return response
    
@router.get("/volatility/top")
def get_top_volatility(interval: str = "5min"):
    data = volatility_service.get_top_volatile(provider, interval)

    return {
        "top_volatile": data
    }


# Institutional macro news endpoint
@router.get("/news")
def get_market_news(symbol: str = "EUR/USD"):

    cache_key = f"macro_news_{symbol}"

    cached = get_cached_route(cache_key)

    if cached:
        return cached

    news = macro_news_service.get_news_for_symbol(symbol)

    response = {
        "symbol": symbol,
        "news": news,
        "total_articles": len(news)
    }

    set_cached_route(cache_key, response)

    return response


@router.get("/asset/details")
async def get_asset_details(
    symbol: str = "EUR/USD",
    interval: str = "5min"
):
    # route cache
    cache_key = f"asset_details_{symbol}_{interval}"

    cached = get_cached_route(cache_key)

    if cached:
        return cached

    # Live cache
    live_data = LIVE_CACHE.get(symbol)

    # Candles
    candles = provider.get_candles(symbol, interval)
    latest_close = 0
    previous_close = 0

    if candles and len(candles) >= 2:
        latest_close = float(candles[-1].get("close", 0))
        previous_close = float(candles[-2].get("close", 0))

    # Signal
    signal_data = (
        live_data.get("signal")
        if live_data and live_data.get("signal")
        else await indicator_service.generate_signal(candles)
    )

    if previous_close > 0:
        calculated_change = round(
            ((latest_close - previous_close) / previous_close) * 100,
            2
        )

        signal_data["price_change"] = calculated_change
    else:
        signal_data["price_change"] = 0

    # Volatility
    volatility = (
        live_data.get("volatility")
        if live_data and live_data.get("volatility")
        else volatility_service.calculate_volatility(candles)
    )

    # Institutional macro news
    news = macro_news_service.get_news_for_symbol(symbol)

    bullish_count = len([
        item for item in news
        if item.get("sentiment") == "Bullish"
    ])

    bearish_count = len([
        item for item in news
        if item.get("sentiment") == "Bearish"
    ])

    neutral_count = len(news) - bullish_count - bearish_count

    total = max(len(news), 1)

    bullish_pct = round((bullish_count / total) * 100)
    bearish_pct = round((bearish_count / total) * 100)
    neutral_pct = round((neutral_count / total) * 100)

    overall_sentiment = "Neutral"

    if bullish_pct > bearish_pct:
        overall_sentiment = "Bullish"

    if bearish_pct > bullish_pct:
        overall_sentiment = "Bearish"

    pulse = {
        "overall_sentiment": overall_sentiment,
        "bullish_percentage": bullish_pct,
        "bearish_percentage": bearish_pct,
        "neutral_percentage": neutral_pct,
        "total_articles": total
    }

    current_price = latest_close

    if live_data and live_data.get("price"):
        current_price = float(live_data.get("price"))

    positioning = positioning_service.get_positioning(symbol, signal_data, volatility)

    ai_analysis = market_analysis_service.analyze_asset(
        symbol=symbol,
        signal_data=signal_data,
        volatility_data=volatility,
        positioning_data=positioning,
        macro_news=news,
    )
    ai_projection = signal_service.generate_ai_projection(
        symbol=symbol,
        current_price=current_price,
        signal_data=signal_data,
        volatility_data=volatility,
    )

    response = {
        "symbol": symbol,
        "interval": interval,
        "price": current_price,
        "signal": signal_data,
        "volatility": volatility,
        "news": news,
        "market_pulse": pulse,
        "economic_events": forexfactory_service.get_events_for_symbol(symbol),
        "positioning": positioning,
        "ai_analysis": ai_analysis,
        "ai_projection": ai_projection,
    }

    set_cached_route(cache_key, response)

    return response

# Asset-specific economic calendar
@router.get("/events")
def get_asset_events(symbol: str = "EUR/USD"):

    cache_key = f"events_{symbol}"

    cached = get_cached_route(cache_key)

    if cached:
        return cached

    events = forexfactory_service.get_events_for_symbol(symbol)

    response = {
        "symbol": symbol,
        "events": events,
        "total_events": len(events)
    }

    set_cached_route(cache_key, response)

    return response

# Realtime live market websocket
@router.websocket("/ws/live")
async def websocket_live_market(websocket: WebSocket):

    await websocket.accept()

    try:

        while True:

            try:

                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=0.01
                )

                if data.get("type") == "subscribe":

                    symbols = data.get("symbols", [])

                    ACTIVE_SYMBOLS.clear()

                    for symbol in symbols:
                        ACTIVE_SYMBOLS.add(symbol)

            except:
                pass

            payload = {
                "assets": LIVE_CACHE,
                "timestamp": time.time()
            }

            await websocket.send_json(payload)

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Live websocket disconnected")

    except Exception as e:
        print(f"Websocket stream error: {e}")