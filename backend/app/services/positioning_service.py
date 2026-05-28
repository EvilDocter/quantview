from typing import Optional

class PositioningService:

    def get_positioning(self, symbol: str, signal_data: Optional[dict] = None, volatility_data: Optional[dict] = None):
        signal_data = signal_data or {}
        volatility_data = volatility_data or {}
        
        clean_symbol = symbol.replace("/", "")
        positioning = self._generate_positioning(clean_symbol, signal_data, volatility_data)
        return positioning

    def _generate_positioning(self, symbol: str, signal_data: dict, volatility_data: dict):
        confidence = float(signal_data.get("confidence", 50))
        signal = signal_data.get("signal", "HOLD")
        movement = float(volatility_data.get("value", 50))

        # Heuristic: If there's a strong BUY signal (smart money buying), retail is usually shorting (contrarian).
        if signal == "BUY":
            short_ratio = max(40, min(85, int(confidence * 0.8 + movement * 0.2)))
            long_ratio = 100 - short_ratio
        elif signal == "SELL":
            long_ratio = max(40, min(85, int(confidence * 0.8 + movement * 0.2)))
            short_ratio = 100 - long_ratio
        else:
            # If HOLD, balanced with slight bias based on volatility
            long_ratio = max(45, min(55, int(50 + (movement % 10) - 5)))
            short_ratio = 100 - long_ratio

        crowd_bias = (
            "BULLISH"
            if long_ratio > 60
            else "BEARISH"
            if short_ratio > 60
            else "NEUTRAL"
        )

        smart_money_bias = self._smart_money_bias(long_ratio, short_ratio)
        squeeze_risk = self._squeeze_probability(long_ratio, short_ratio, movement)
        institutional_activity = self._institutional_flow(symbol, crowd_bias)
        ai_summary = self._generate_ai_summary(symbol, crowd_bias, smart_money_bias, squeeze_risk)

        return {
            "symbol": symbol,
            "retail_long": long_ratio,
            "retail_short": short_ratio,
            "crowd_bias": crowd_bias,
            "smart_money_bias": smart_money_bias,
            "squeeze_risk": squeeze_risk,
            "institutional_activity": institutional_activity,
            "ai_summary": ai_summary,
        }

    def _smart_money_bias(self, long_ratio, short_ratio):
        if long_ratio >= 65:
            return "SMART MONEY BEARISH"
        if short_ratio >= 65:
            return "SMART MONEY BULLISH"
        return "BALANCED FLOW"

    def _squeeze_probability(self, long_ratio, short_ratio, movement):
        risk = min(95, int(max(long_ratio, short_ratio) * 0.7 + movement * 0.4))
        
        if long_ratio >= 65:
            return {
                "type": "LONG SQUEEZE",
                "risk": risk,
            }

        if short_ratio >= 65:
            return {
                "type": "SHORT SQUEEZE",
                "risk": risk,
            }

        return {
            "type": "LOW",
            "risk": max(15, min(45, risk)),
        }

    def _institutional_flow(self, symbol, crowd_bias):
        if crowd_bias == "BULLISH":
            return {
                "activity": "Distribution",
                "description": (
                    "Institutional participants appear to be reducing exposure "
                    "into retail strength."
                )
            }
        if crowd_bias == "BEARISH":
            return {
                "activity": "Accumulation",
                "description": (
                    "Institutional participants appear to be accumulating "
                    "positions during retail weakness."
                )
            }

        return {
            "activity": "Neutral",
            "description": (
                "No significant institutional imbalance currently detected."
            )
        }

    def _generate_ai_summary(self, symbol, crowd_bias, smart_money_bias, squeeze_risk):
        return (
            f"Retail positioning for {symbol} currently shows a "
            f"{crowd_bias.lower()} market structure. "
            f"AI analysis indicates {smart_money_bias.lower()} with "
            f"elevated {squeeze_risk['type'].lower()} probability."
        )