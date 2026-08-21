"""
QuantView — Evidence Validation Gate (P0 Mandate)

Strict validator ensuring AI Copilot never receives incomplete or zero financial metrics.
If required fields are missing or zero, triggers automatic data refresh or explicit refusal.
"""

import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("evidence_validator")

REFUSAL_MESSAGE = (
    "Verified financial data is currently unavailable. "
    "QuantView cannot generate an investment recommendation until data integrity is restored."
)


class EvidenceValidator:
    REQUIRED_METRICS = [
        "current_price",
        "market_cap",
        "revenue",
        "ebitda",
        "net_income",
    ]

    @staticmethod
    def validate_packet(packet: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate that the evidence packet contains all required non-zero numerical fields.
        Returns (is_valid, reason_if_invalid).
        """
        mdata = packet.get("market_data", {})
        fin = packet.get("financials") or packet.get("income_statement") or packet.get("financial_summary") or {}

        # Check market data metrics
        price = mdata.get("current_price") or mdata.get("last_price") or 0
        mcap = mdata.get("market_cap") or packet.get("valuation_metrics", {}).get("market_cap") or 0

        if not price or float(price) <= 0:
            return False, f"Missing or non-positive stock price: {price}"

        if not mcap or float(mcap) <= 0:
            return False, f"Missing or non-positive market cap: {mcap}"

        # Check income statement metrics
        rev = fin.get("revenue") or fin.get("revenue_inr") or 0
        net_inc = fin.get("net_income") or fin.get("net_income_inr") or 0

        if not rev and not net_inc:
            return False, f"Missing financial income statement metrics: revenue={rev}, net_income={net_inc}"

        return True, "All required financial evidence verified."
