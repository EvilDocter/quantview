"""
NSE Ingestion Service — Utility Functions
"""

import hashlib
import os
import re
from typing import Optional


def compute_sha256(file_path: str) -> str:
    """Compute SHA-256 hash of a file on disk."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_bytes_sha256(content: bytes) -> str:
    """Compute SHA-256 hash of bytes in memory."""
    return hashlib.sha256(content).hexdigest()


def sanitize_symbol(symbol: str) -> str:
    """Sanitize symbol string e.g. 'NSE:INFY-EQ' -> 'INFY'."""
    clean = symbol.upper().strip()
    clean = re.sub(r"^NSE:", "", clean)
    clean = re.sub(r"-EQ$", "", clean)
    return re.sub(r"[^A-Z0-9_]", "", clean)


def extract_year_from_text(text: str, default_year: int = 2025) -> int:
    """Extract 4-digit fiscal year from title/URL e.g. 'Annual Report 2023-24' -> 2024."""
    match_range = re.search(r"20(\d{2})[-_](\d{2,4})", text)
    if match_range:
        yy = match_range.group(2)
        if len(yy) == 2:
            return int(f"20{yy}")
        elif len(yy) == 4:
            return int(yy)

    matches = re.findall(r"20\d{2}", text)
    if matches:
        years = [int(y) for y in matches]
        return max(years)
    return default_year
