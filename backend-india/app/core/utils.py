"""
QuantView — Core Utilities

Helper functions used across the application.
"""

import hashlib
from datetime import datetime, date
from typing import Optional


def generate_hash(*args) -> str:
    """Generate a SHA-256 hash from multiple values. Used for deduplication."""
    combined = "|".join(str(a) for a in args)
    return hashlib.sha256(combined.encode()).hexdigest()


def fiscal_year_from_date(d: date) -> str:
    """
    Convert a date to Indian fiscal year string.
    Indian FY runs April to March.
    e.g., March 2024 → "FY24", June 2024 → "FY25"
    """
    if d.month >= 4:
        return f"FY{(d.year + 1) % 100:02d}"
    else:
        return f"FY{d.year % 100:02d}"


def quarter_from_date(d: date) -> str:
    """
    Convert a date to Indian fiscal quarter.
    Q1: Apr-Jun, Q2: Jul-Sep, Q3: Oct-Dec, Q4: Jan-Mar
    """
    month = d.month
    if month in (4, 5, 6):
        return "Q1"
    elif month in (7, 8, 9):
        return "Q2"
    elif month in (10, 11, 12):
        return "Q3"
    else:  # 1, 2, 3
        return "Q4"


def format_crores(value: float) -> str:
    """Format a number in Indian Crores notation."""
    if value is None:
        return "N/A"
    if abs(value) >= 10000:
        return f"₹{value / 10000:,.1f}L Cr"  # Lakh Crores
    elif abs(value) >= 100:
        return f"₹{value:,.0f} Cr"
    else:
        return f"₹{value:,.2f} Cr"


def format_lakhs(value: float) -> str:
    """Format a number in Indian Lakhs notation."""
    if value is None:
        return "N/A"
    if abs(value) >= 10000000:
        return f"₹{value / 10000000:,.2f} Cr"
    elif abs(value) >= 100000:
        return f"₹{value / 100000:,.2f} L"
    else:
        return f"₹{value:,.0f}"


def safe_divide(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    """Safe division returning None if denominator is zero or None."""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def safe_pct_change(current: Optional[float], previous: Optional[float]) -> Optional[float]:
    """Calculate percentage change, returning None for invalid inputs."""
    if current is None or previous is None or previous == 0:
        return None
    return round(((current - previous) / abs(previous)) * 100, 2)


def nse_symbol_to_yahoo(symbol: str) -> str:
    """Convert NSE symbol to Yahoo Finance format (append .NS)."""
    return f"{symbol}.NS"


def bse_code_to_yahoo(bse_code: str) -> str:
    """Convert BSE code to Yahoo Finance format (append .BO)."""
    return f"{bse_code}.BO"


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max_length, adding ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
