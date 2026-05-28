import pandas as pd
import ta
from app.services.ai_service import ai_service


class IndicatorService:

    def calculate_indicators(self, candles):
        df = pd.DataFrame(candles)

        if df.empty:
            return []

        required_columns = ["open", "high", "low", "close"]

        for col in required_columns:
            if col not in df.columns:
                return []

        try:
            # convert to float
            df["close"] = df["close"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)
            df["open"] = df["open"].astype(float)

            # RSI
            df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()

            # EMA
            df["ema_20"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()
            df["ema_50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()

            # ATR
            df["atr"] = ta.volatility.AverageTrueRange(
                df["high"], df["low"], df["close"], window=14
            ).average_true_range()

            # MACD
            macd = ta.trend.MACD(df["close"])
            df["macd"] = macd.macd()
            df["macd_signal"] = macd.macd_signal()

            # --- PRICE ACTION CONCEPTS (SMC LUXALGO TRANSLATION) ---
            window = 5
            df["pivot_high"] = 0.0
            df["pivot_low"] = 0.0
            
            # 1. Pivot Scanners
            for i in range(window, len(df) - window):
                highs_slice = df["high"].iloc[i - window : i + window + 1]
                lows_slice = df["low"].iloc[i - window : i + window + 1]
                if df["high"].iloc[i] == highs_slice.max():
                    df.loc[df.index[i], "pivot_high"] = float(df["high"].iloc[i])
                if df["low"].iloc[i] == lows_slice.min():
                    df.loc[df.index[i], "pivot_low"] = float(df["low"].iloc[i])

            # 2. Fair Value Gaps (FVG)
            df["fvg_bullish"] = False
            df["fvg_bearish"] = False
            df["fvg_gap"] = 0.0
            for i in range(2, len(df)):
                low_curr = float(df["low"].iloc[i])
                high_prev2 = float(df["high"].iloc[i - 2])
                high_curr = float(df["high"].iloc[i])
                low_prev2 = float(df["low"].iloc[i - 2])

                if low_curr > high_prev2:
                    df.loc[df.index[i], "fvg_bullish"] = True
                    df.loc[df.index[i], "fvg_gap"] = float(low_curr - high_prev2)
                elif high_curr < low_prev2:
                    df.loc[df.index[i], "fvg_bearish"] = True
                    df.loc[df.index[i], "fvg_gap"] = float(low_prev2 - high_curr)

            # 3. Market Structure (BOS & CHoCH)
            last_ph = 0.0
            last_pl = 0.0
            df["bos_bullish"] = False
            df["bos_bearish"] = False
            df["choch_bullish"] = False
            df["choch_bearish"] = False
            trend = 0  # 1 = Bullish, -1 = Bearish

            for i in range(len(df)):
                ph = float(df["pivot_high"].iloc[i])
                pl = float(df["pivot_low"].iloc[i])
                close_curr = float(df["close"].iloc[i])

                if ph > 0:
                    last_ph = ph
                if pl > 0:
                    last_pl = pl

                if last_ph > 0 and close_curr > last_ph:
                    if trend == -1:
                        df.loc[df.index[i], "choch_bullish"] = True
                    else:
                        df.loc[df.index[i], "bos_bullish"] = True
                    trend = 1
                    last_ph = 0.0  # Cleared after break

                elif last_pl > 0 and close_curr < last_pl:
                    if trend == 1:
                        df.loc[df.index[i], "choch_bearish"] = True
                    else:
                        df.loc[df.index[i], "bos_bearish"] = True
                    trend = -1
                    last_pl = 0.0  # Cleared after break

            df = df.fillna(0)

            return df.tail(100).to_dict(orient="records")

        except Exception as e:
            print(f"Indicator calculation failed: {e}")
            return []

    async def generate_signal(self, candles):
        data = self.calculate_indicators(candles)

        if not data:
            return {
                "signal": "HOLD",
                "confidence": 0,
                "rsi": 0,
                "macd": "Neutral",
                "sentiment": "Neutral",
            }

        latest = data[-1]

        rsi = round(float(latest.get("rsi", 0)), 2)
        macd = float(latest.get("macd", 0))
        macd_signal = float(latest.get("macd_signal", 0))

        signal = "HOLD"
        confidence = 50
        sentiment = "Neutral"
        macd_trend = "Neutral"

        ema20 = float(latest.get("ema_20", 0))
        ema50 = float(latest.get("ema_50", 0))
        atr = float(latest.get("atr", 0))
        close = float(latest.get("close", 0))

        volatility_strength = 0

        if close > 0:
            volatility_strength = (atr / close) * 100

        # RSI logic
        if rsi <= 30:
            signal = "BUY"
            confidence += 20
            sentiment = "Bullish"

        elif rsi >= 70:
            signal = "SELL"
            confidence += 20
            sentiment = "Bearish"

        elif 40 <= rsi <= 60:
            confidence -= 8

        # MACD momentum logic
        macd_diff = abs(macd - macd_signal)

        if macd > macd_signal:
            macd_trend = "Bullish"
            confidence += min(macd_diff * 120, 18)

            if signal == "HOLD" and macd_diff > 0.03:
                signal = "BUY"
                sentiment = "Bullish"

        elif macd < macd_signal:
            macd_trend = "Bearish"
            confidence += min(macd_diff * 120, 18)

            if signal == "HOLD" and macd_diff > 0.03:
                signal = "SELL"
                sentiment = "Bearish"

        # EMA trend strength
        trend_strength = abs(ema20 - ema50)

        if ema20 > ema50:
            confidence += min(trend_strength * 25, 15)

            if signal == "HOLD":
                signal = "BUY"
                sentiment = "Bullish"

        elif ema20 < ema50:
            confidence += min(trend_strength * 25, 15)

            if signal == "HOLD":
                signal = "SELL"
                sentiment = "Bearish"

        # volatility weighting
        if volatility_strength > 2:
            confidence += 8
        elif volatility_strength > 1:
            confidence += 4

        # stabilize confidence range
        confidence = max(int(confidence), 35)
        confidence = min(confidence, 95)

        # stabilize sentiment when HOLD
        if signal == "HOLD":
            sentiment = "Neutral"

        # Try to use Real AI Analysis
        try:
            symbol = candles[-1].get("symbol", "Asset") if candles else "Asset"
            current_price = close
            
            ai_result = await ai_service.get_market_analysis(
                symbol=symbol,
                current_price=current_price,
                indicators=latest
            )
            
            if ai_result:
                print(f"🧠 [Real AI] Successfully analyzed {symbol}: {ai_result}")
                return {
                    "signal": ai_result.get("signal", signal),
                    "confidence": int(ai_result.get("confidence", confidence)),
                    "rsi": rsi,
                    "macd": macd_trend, # Will get overwritten by AI macd_trend if present
                    "sentiment": ai_result.get("macd_trend", sentiment),
                    "is_real_ai": True,
                    "ai_reasoning": ai_result.get("reasoning", ""),
                    # Price Action Concepts
                    "bos_bullish": bool(latest.get("bos_bullish", False)),
                    "bos_bearish": bool(latest.get("bos_bearish", False)),
                    "choch_bullish": bool(latest.get("choch_bullish", False)),
                    "choch_bearish": bool(latest.get("choch_bearish", False)),
                    "fvg_bullish": bool(latest.get("fvg_bullish", False)),
                    "fvg_bearish": bool(latest.get("fvg_bearish", False)),
                    "fvg_gap": round(float(latest.get("fvg_gap", 0.0)), 4),
                }
        except Exception as e:
            print(f"⚠️ [IndicatorService] AI analysis failed, falling back to deterministic: {e}")

        # Fallback to deterministic
        return {
            "signal": signal,
            "confidence": confidence,
            "rsi": round(rsi, 2),
            "macd": macd_trend,
            "sentiment": sentiment,
            # Price Action Concepts
            "bos_bullish": bool(latest.get("bos_bullish", False)),
            "bos_bearish": bool(latest.get("bos_bearish", False)),
            "choch_bullish": bool(latest.get("choch_bullish", False)),
            "choch_bearish": bool(latest.get("choch_bearish", False)),
            "fvg_bullish": bool(latest.get("fvg_bullish", False)),
            "fvg_bearish": bool(latest.get("fvg_bearish", False)),
            "fvg_gap": round(float(latest.get("fvg_gap", 0.0)), 4),
        }