from typing import Optional
from datetime import datetime

class MarketAnalysisService:

    def analyze_asset(
        self,
        symbol: str,
        signal_data: Optional[dict] = None,
        volatility_data: Optional[dict] = None,
        positioning_data: Optional[dict] = None,
        macro_news: Optional[list] = None,
    ):
        signal_data = signal_data or {}
        volatility_data = volatility_data or {}
        positioning_data = positioning_data or {}
        macro_news = macro_news or []

        confidence = float(signal_data.get("confidence", 50))
        signal = signal_data.get("signal", "HOLD")

        movement = float(volatility_data.get("value", 50))

        regime = "BALANCED"

        if movement >= 75:
            regime = "VOLATILITY EXPANSION"
        elif movement <= 35:
            regime = "VOLATILITY COMPRESSION"

        smart_money = "ACCUMULATION"
        if signal == "SELL":
            smart_money = "DISTRIBUTION"

        liquidity_state = "BALANCED FLOW"
        if movement >= 80:
            liquidity_state = "HIGH VOLATILITY"

        confidence_projection = []
        
        # Deterministic projection based on current confidence and movement trend
        base_projection = confidence
        trend_factor = 2 if movement > 50 else -2
        
        for idx in range(6):
            # Smoothly project confidence changes based on volatility
            projected = max(15, min(99, base_projection + (idx * trend_factor)))
            confidence_projection.append({
                "interval": f"T+{idx + 1}",
                "confidence": int(projected),
            })
            
        breakout_prob = max(40, min(95, int(90 - min(movement, 50))))
        liquidity_score = max(40, min(99, int(movement * 0.8 + confidence * 0.4)))

        return {
            "symbol": symbol,
            "market_regime": {
                "name": regime,
                "strength": "HIGH" if confidence >= 70 else "MODERATE",
                "bias": signal,
                "confidence": confidence,
            },
            "smart_money": {
                "flow": smart_money,
                "pressure": signal,
            },
            "volatility_forecast": {
                "forecast": regime,
                "event_risk": "HIGH" if movement >= 70 else "MODERATE",
                "breakout_probability": breakout_prob,
            },
            "ai_narrative": {
                "headline": f"{symbol} institutional flow analysis active.",
                "summary": f"AI models detect {regime.lower()} with {signal.lower()} bias.",
                "macro_focus": "Institutional liquidity",
            },
            "confidence_evolution": confidence_projection,
            "liquidity_state": {
                "state": liquidity_state,
                "liquidity_score": liquidity_score,
            },
            "generated_at": datetime.utcnow().isoformat(),
        }