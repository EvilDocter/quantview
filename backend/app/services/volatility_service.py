import pandas as pd

import time

CACHE = {
    "data": None,
    "timestamp": 0
}

CACHE_DURATION = 30  # seconds

SYMBOLS = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "XAU/USD"
]

class VolatilityService:

    def calculate_volatility(self, candles):
        df = pd.DataFrame(candles)
        if df.empty:
            return {
                "value": 0,
                "status": "NO_DATA",
                "level": "LOW",
            }

        if "close" not in df.columns:
            return {
                "value": 0,
                "status": "INVALID_DATA",
                "level": "LOW",
            }

        # ensure OHLC fields exist
        if "high" not in df.columns:
            df["high"] = df["close"]

        if "low" not in df.columns:
            df["low"] = df["close"]

        # convert to float
        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)

        # ATR-style candle movement volatility
        closes = df["close"]
        highs = df["high"]
        lows = df["low"]

        candle_range = ((highs - lows) / closes.replace(0, 1)) * 100

        candle_range = candle_range.replace(
            [float("inf"), -float("inf")], 0
        ).fillna(0)

        avg_range = float(candle_range.mean())

        pct_changes = closes.pct_change().replace(
            [float("inf"), -float("inf")], 0
        ).fillna(0)

        momentum = abs(float(pct_changes.mean() * 100))

        # stronger readable movement scaling
        volatility = (
            (avg_range * 350)
            + (momentum * 180)
        )

        # classify volatility
        if volatility > 35:
            level = "HIGH"
        elif volatility > 15:
            level = "MEDIUM"
        else:
            level = "LOW"

        # market status
        if level == "HIGH":
            status = "ACTIVE"
        elif level == "MEDIUM":
            status = "WATCH"
        else:
            status = "STABLE"

        # kill NaN values
        if volatility != volatility:
            volatility = 0.0

        volatility = float(volatility)

        return {
            "value": float(round(volatility, 1)),
            "level": level,
            "status": status
        }
    
    def get_top_volatile(self, provider, interval="5min"):
        current_time = time.time()

        # return cached data if still valid
        if CACHE["data"] is not None and (current_time - CACHE["timestamp"] < CACHE_DURATION):
            return CACHE["data"]

        results = []

        for symbol in SYMBOLS:
            try:
                candles = provider.get_candles(symbol, interval)

                # skip if no data
                if not candles or len(candles) == 0:
                    continue

                volatility = self.calculate_volatility(candles)

                results.append({
                    "symbol": symbol,
                    "volatility": volatility
                })

            except Exception as e:
                print(f"Error for {symbol}: {e}")
                continue

        # sort highest volatility first
        results = sorted(results, key=lambda x: x["volatility"]["value"], reverse=True)

        # store in cache
        CACHE["data"] = results
        CACHE["timestamp"] = current_time

        return results