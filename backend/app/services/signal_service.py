from typing import Optional

class SignalService:

    def generate_ai_projection(
        self,
        symbol: str,
        current_price: float,
        signal_data: Optional[dict] = None,
        volatility_data: Optional[dict] = None,
    ):
        signal_data = signal_data or {}
        volatility_data = volatility_data or {}

        signal = signal_data.get("signal", "HOLD")
        confidence = float(signal_data.get("confidence", 50))
        
        # In volatility_service, it returns 'value', not 'movement_intensity' directly to here, but checking both just in case.
        movement = float(volatility_data.get("value", 50))

        projected_move = self._calculate_projected_move(
            current_price,
            signal,
            confidence,
            movement,
        )

        support_resistance = self._generate_key_levels(
            current_price,
            movement,
        )

        institutional_zones = self._institutional_zones(
            current_price,
            signal,
            movement,
        )

        probability_map = self._probability_engine(
            signal,
            confidence,
        )

        breakout_projection = self._breakout_projection(
            current_price,
            movement,
            signal,
        )

        return {
            "symbol": symbol,
            "signal": signal,
            "confidence": confidence,
            "current_price": current_price,
            "projected_move": projected_move,
            "support_resistance": support_resistance,
            "institutional_zones": institutional_zones,
            "probability_map": probability_map,
            "breakout_projection": breakout_projection,
        }

    def _calculate_projected_move(
        self,
        current_price,
        signal,
        confidence,
        movement,
    ):
        volatility_factor = max(movement / 100, 0.5)
        confidence_factor = max(confidence / 100, 0.4)

        # Base move derived from volatility and confidence, strictly deterministic
        move_percent = round(2.5 * volatility_factor * confidence_factor, 2)

        if signal == "BUY":
            target_price = round(current_price * (1 + (move_percent / 100)), 4)
        elif signal == "SELL":
            target_price = round(current_price * (1 - (move_percent / 100)), 4)
        else:
            target_price = round(current_price, 4)
            move_percent = 0.0

        return {
            "direction": signal,
            "move_percent": move_percent,
            "target_price": target_price,
        }

    def _generate_key_levels(
        self,
        current_price,
        movement,
    ):
        volatility = max(movement / 100, 0.5)

        support_1 = round(current_price * (1 - (0.008 * volatility)), 4)
        support_2 = round(current_price * (1 - (0.016 * volatility)), 4)

        resistance_1 = round(current_price * (1 + (0.008 * volatility)), 4)
        resistance_2 = round(current_price * (1 + (0.016 * volatility)), 4)

        return {
            "support": [support_1, support_2],
            "resistance": [resistance_1, resistance_2],
        }

    def _institutional_zones(
        self,
        current_price,
        signal,
        movement,
    ):
        volatility = max(movement / 100, 0.5)
        
        accumulation_low = round(current_price * (1 - (0.015 * volatility)), 4)
        accumulation_high = round(current_price * (1 - (0.005 * volatility)), 4)

        distribution_low = round(current_price * (1 + (0.005 * volatility)), 4)
        distribution_high = round(current_price * (1 + (0.018 * volatility)), 4)

        dominant_zone = (
            "ACCUMULATION"
            if signal == "BUY"
            else "DISTRIBUTION"
            if signal == "SELL"
            else "NEUTRAL"
        )

        return {
            "dominant_zone": dominant_zone,
            "accumulation_zone": {
                "low": accumulation_low,
                "high": accumulation_high,
            },
            "distribution_zone": {
                "low": distribution_low,
                "high": distribution_high,
            },
        }

    def _probability_engine(
        self,
        signal,
        confidence,
    ):
        bullish_probability = confidence if signal == "BUY" else max(100 - confidence, 5) if signal == "SELL" else 50
        bearish_probability = max(100 - confidence, 5) if signal == "BUY" else confidence if signal == "SELL" else 50

        neutral_probability = max(5, 100 - bullish_probability - bearish_probability)

        return {
            "bullish": bullish_probability,
            "bearish": bearish_probability,
            "neutral": neutral_probability,
        }

    def _breakout_projection(
        self,
        current_price,
        movement,
        signal,
    ):
        expansion_factor = max(movement / 100, 0.5)

        breakout_upside = round(current_price * (1 + (0.025 * expansion_factor)), 4)
        breakout_downside = round(current_price * (1 - (0.025 * expansion_factor)), 4)

        # Breakout probability based purely on movement (volatility squeeze indicator proxy)
        # Higher movement = lower breakout probability (already broken out)
        # Lower movement = higher breakout probability (compression)
        base_prob = 90 - min(movement, 50)
        breakout_probability = max(40, min(95, int(base_prob)))

        volatility_state = (
            "EXPANSION"
            if movement >= 70
            else "COMPRESSION"
            if movement <= 35
            else "BALANCED"
        )

        return {
            "volatility_state": volatility_state,
            "breakout_probability": breakout_probability,
            "upside_target": breakout_upside,
            "downside_target": breakout_downside,
            "preferred_direction": signal,
        }