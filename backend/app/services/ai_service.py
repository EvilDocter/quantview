import os
import json
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        # We use Groq's API which is 100% FREE and compatible with the OpenAI SDK
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        ) if self.api_key else None
        
        self._analysis_cache = {}

    async def get_market_analysis(self, symbol: str, current_price: float, indicators: dict):
        """
        Uses OpenAI to generate a real AI market analysis.
        If no API key is provided, returns None (allowing a fallback to deterministic logic).
        """
        if not self.client:
            print(f"⚠️ [AIService] No GROQ_API_KEY found. Falling back to deterministic logic for {symbol}.")
            return None

        # Prepare the data payload for the AI
        payload = {
            "symbol": symbol,
            "current_price": current_price,
            "rsi": indicators.get("rsi"),
            "macd": indicators.get("macd"),
            "macd_signal": indicators.get("macd_signal"),
            "ema_20": indicators.get("ema_20"),
            "ema_50": indicators.get("ema_50"),
            "atr": indicators.get("atr"),
            # LuxAlgo Price Action Concepts / SMC Parameters
            "bos_bullish": bool(indicators.get("bos_bullish", False)),
            "bos_bearish": bool(indicators.get("bos_bearish", False)),
            "choch_bullish": bool(indicators.get("choch_bullish", False)),
            "choch_bearish": bool(indicators.get("choch_bearish", False)),
            "fvg_bullish": bool(indicators.get("fvg_bullish", False)),
            "fvg_bearish": bool(indicators.get("fvg_bearish", False)),
            "fvg_gap": float(indicators.get("fvg_gap", 0.0)),
        }

        prompt = f"""
You are an expert quantitative trading AI for 'QuantView', an institutional trading terminal.
Analyze the following real-time technical indicators and Smart Money / Price Action Concepts (LuxAlgo model) for the asset '{symbol}'.

DATA:
{json.dumps(payload, indent=2)}

INSTRUCTIONS:
1. Determine the market signal ("BUY", "SELL", or "HOLD").
2. Calculate your confidence level from 0 to 100 based on technical indicators (RSI, MACD, EMAs) and Smart Money Concepts (BOS, CHoCH, and Fair Value Gaps).
3. If a bullish Break of Structure (bos_bullish), Change of Character (choch_bullish), or bullish Fair Value Gap (fvg_bullish) is detected, heavily favor a BULLISH BUY bias.
4. If a bearish Break of Structure (bos_bearish), Change of Character (choch_bearish), or bearish Fair Value Gap (fvg_bearish) is detected, heavily favor a BEARISH SELL bias.
5. Determine the MACD trend ("Bullish", "Bearish", or "Neutral").
6. In your "reasoning", refer directly to any active Smart Money Concepts or Price Action triggers you noticed.
7. Output STRICTLY in JSON format with NO markdown wrapping.

EXPECTED FORMAT:
{{
    "signal": "BUY",
    "confidence": 85,
    "macd_trend": "Bullish",
    "reasoning": "Brief one sentence explanation referencing the technicals and active Price Action triggers."
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile", # State of the art premium model on Groq (100% Free)
                messages=[
                    {"role": "system", "content": "You are a specialized trading AI that outputs strictly valid JSON without any markdown formatting like ```json."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2, # Low temperature for more deterministic analysis
                response_format={ "type": "json_object" }
            )
            
            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)
            
            return result_json
            
        except Exception as e:
            print(f"❌ [AIService] Error calling OpenAI API: {e}")
            return None

ai_service = AIService()
