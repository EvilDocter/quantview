

import requests
from bs4 import BeautifulSoup
from datetime import datetime


class ForexFactoryService:

    def __init__(self):
        self.url = "https://www.forexfactory.com/calendar"

    def get_events_for_symbol(self, symbol: str):

        try:
            events = self._fetch_calendar()

            related_currencies = self._extract_related_currencies(symbol)

            filtered = [
                event
                for event in events
                if event.get("currency") in related_currencies
            ]

            return filtered

        except Exception as e:
            print("ForexFactory error:", e)
            return []

    def _extract_related_currencies(self, symbol: str):

        mapping = {
            "EUR/USD": ["EUR", "USD"],
            "GBP/USD": ["GBP", "USD"],
            "USD/JPY": ["USD", "JPY"],
            "USD/CHF": ["USD", "CHF"],
            "AUD/USD": ["AUD", "USD"],
            "USD/CAD": ["USD", "CAD"],
            "NZD/USD": ["NZD", "USD"],
            "EUR/GBP": ["EUR", "GBP"],
            "EUR/JPY": ["EUR", "JPY"],
            "GBP/JPY": ["GBP", "JPY"],
            "XAU/USD": ["USD"],
            "XAG/USD": ["USD"],
            "WTI": ["USD"],
            "BTC/USD": ["USD"],
            "ETH/USD": ["USD"],
        }

        return mapping.get(symbol, ["USD"])

    def _generate_event_intelligence(
        self,
        currency,
        event_name,
        impact
    ):

        high_volatility_keywords = [
            "CPI",
            "Inflation",
            "Interest Rate",
            "FOMC",
            "Non-Farm",
            "GDP",
            "Employment",
            "Powell",
            "ECB",
            "BOJ",
        ]

        bullish_keywords = [
            "GDP",
            "Employment",
            "Retail Sales",
            "PMI",
        ]

        bearish_keywords = [
            "Inflation",
            "Unemployment",
            "Rate Cut",
        ]

        volatility = "LOW"
        risk_score = 35

        if impact == "HIGH":
            volatility = "EXTREME"
            risk_score = 90
        elif impact == "MEDIUM":
            volatility = "HIGH"
            risk_score = 70

        if any(k.lower() in event_name.lower() for k in high_volatility_keywords):
            volatility = "EXTREME"
            risk_score = min(risk_score + 10, 100)

        market_bias = "NEUTRAL"

        if any(k.lower() in event_name.lower() for k in bullish_keywords):
            market_bias = "BULLISH"

        if any(k.lower() in event_name.lower() for k in bearish_keywords):
            market_bias = "BEARISH"

        affected_assets = []

        if currency == "USD":
            affected_assets.extend([
                "EUR/USD",
                "GBP/USD",
                "XAU/USD",
                "BTC/USD",
                "ETH/USD",
            ])

        if currency == "EUR":
            affected_assets.extend([
                "EUR/USD",
                "EUR/JPY",
                "EUR/GBP",
            ])

        if currency == "JPY":
            affected_assets.extend([
                "USD/JPY",
                "EUR/JPY",
                "GBP/JPY",
            ])

        ai_summary = (
            f"{impact} impact macroeconomic event for {currency}. "
            f"Expected market volatility: {volatility}. "
            f"Current AI directional bias: {market_bias}."
        )

        return {
            "market_bias": market_bias,
            "volatility_expectation": volatility,
            "risk_score": risk_score,
            "ai_summary": ai_summary,
            "affected_assets": affected_assets,
        }

    def _fetch_calendar(self):

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        }

        response = requests.get(
            self.url,
            headers=headers,
            timeout=15
        )

        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.select("tr.calendar__row")

        parsed_events = []

        current_date = datetime.utcnow().strftime("%Y-%m-%d")

        for row in rows:

            try:
                currency = row.select_one(
                    ".calendar__currency"
                )

                impact = row.select_one(
                    ".calendar__impact"
                )

                event = row.select_one(
                    ".calendar__event-title"
                )

                actual = row.select_one(
                    ".calendar__actual"
                )

                forecast = row.select_one(
                    ".calendar__forecast"
                )

                previous = row.select_one(
                    ".calendar__previous"
                )

                time = row.select_one(
                    ".calendar__time"
                )

                if not currency or not event:
                    continue

                impact_level = "LOW"

                impact_classes = impact.get("class", [])

                if any("high" in c.lower() for c in impact_classes):
                    impact_level = "HIGH"
                elif any("medium" in c.lower() for c in impact_classes):
                    impact_level = "MEDIUM"

                event_name = event.text.strip()
                currency_text = currency.text.strip()

                intelligence = self._generate_event_intelligence(
                    currency_text,
                    event_name,
                    impact_level
                )

                parsed_events.append({
                    "currency": currency_text,
                    "event": event_name,
                    "impact": impact_level,
                    "actual": actual.text.strip() if actual else "",
                    "forecast": forecast.text.strip() if forecast else "",
                    "previous": previous.text.strip() if previous else "",
                    "time": time.text.strip() if time else "",
                    "date": current_date,
                    "market_bias": intelligence["market_bias"],
                    "volatility_expectation": intelligence["volatility_expectation"],
                    "risk_score": intelligence["risk_score"],
                    "ai_summary": intelligence["ai_summary"],
                    "affected_assets": intelligence["affected_assets"],
                })

            except Exception as row_error:
                print("ForexFactory row parse error:", row_error)
                continue

        return parsed_events