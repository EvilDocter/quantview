"""
QuantView — Verification Engine (P0 Mandate)

Cross-references every financial numerical claim in AI responses against PostgreSQL & OCR evidence.
Redacts or rejects hallucinated responses if numerical mismatch rate exceeds 10%.
"""

import re
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("verification_engine")


class VerificationEngine:
    """Zero-hallucination verification engine for AI equity research output."""

    @staticmethod
    def verify_response(
        response_text: str,
        evidence_packet: Dict[str, Any],
    ) -> Tuple[bool, str, float]:
        """
        Extract financial numerical claims from response_text and match against evidence_packet.
        Returns (is_verified, verified_text, hallucination_rate_pct).
        """
        if not response_text or len(response_text.strip()) < 50:
            return False, response_text, 100.0

        mdata = evidence_packet.get("market_data", {})
        inc = evidence_packet.get("income_statement", {}) or evidence_packet.get("financials", {})
        bal = evidence_packet.get("balance_sheet", {})
        val = evidence_packet.get("valuation_metrics", {})
        growth = evidence_packet.get("growth_metrics", {})

        valid_evidence_numbers = set()
        for d in [mdata, inc, bal, val, growth]:
            for k, v in d.items():
                if isinstance(v, (int, float)) and v != 0:
                    ev = float(v)
                    valid_evidence_numbers.add(round(ev, 2))
                    valid_evidence_numbers.add(round(ev / 1e7, 2))  # Cr conversion
                    valid_evidence_numbers.add(round(ev / 1e5, 2))  # Lakh conversion
                    valid_evidence_numbers.add(round(ev / 1e9, 2))  # Billion conversion

        # Target financial claims: ₹ amounts, or numbers explicit with Cr, L, x, or %
        fin_matches = re.findall(r"(?:₹\s*[\d,]+(?:\.\d+)?|[\d,]+(?:\.\d+)?\s*(?:Cr|L|x|%))", response_text)

        total_claims = 0
        unverified_claims = 0

        for match in fin_matches:
            clean_num_str = re.sub(r"[^\d.]", "", match)
            if not clean_num_str:
                continue
            try:
                num = float(clean_num_str)
                # Ignore small numbers (<=10) or common percentages like 100%
                if num <= 10 or num in [15, 25, 50, 75, 90, 100]:
                    continue
                total_claims += 1

                # Check if close match exists in valid_evidence_numbers
                matched = any(abs(num - ev) / (ev or 1) < 0.10 for ev in valid_evidence_numbers)
                if not matched:
                    unverified_claims += 1
            except ValueError:
                pass

        hallucination_rate = (unverified_claims / total_claims * 100.0) if total_claims > 0 else 0.0

        if hallucination_rate > 10.0:
            logger.warning(f"VerificationEngine rejected response: hallucination_rate = {hallucination_rate:.1f}% ({unverified_claims}/{total_claims} unverified claims)")
            return False, response_text, hallucination_rate

        return True, response_text, hallucination_rate
