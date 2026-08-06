"""
QuantView — Tests for NSE Ingestion Service (curl_cffi Akamai Bypass)
"""

import pytest
import asyncio
from pathlib import Path
from app.knowledge.crawler.nse.parser import PDFValidator
from app.knowledge.crawler.nse.exceptions import NSEValidationError
from app.knowledge.crawler.nse.utils import sanitize_symbol, extract_year_from_text, compute_bytes_sha256
from app.knowledge.crawler.nse.models import ReportMetadata, ExchangeType, DocumentType
from app.knowledge.crawler.nse.storage import StorageManager
from app.knowledge.crawler.nse.client import NSEClient
from app.knowledge.crawler.nse import sync_company, discover_company_reports


# ── Unit Tests (no network) ──────────────────────────────────────

def test_sanitize_symbol():
    assert sanitize_symbol("NSE:INFY-EQ") == "INFY"
    assert sanitize_symbol("RELIANCE") == "RELIANCE"
    assert sanitize_symbol("  tcs-eq ") == "TCS"


def test_extract_year_from_text():
    assert extract_year_from_text("Infosys Annual Report 2023-24.pdf") == 2024
    assert extract_year_from_text("Reliance_AR_2025.pdf") == 2025
    assert extract_year_from_text("No year title", default_year=2025) == 2025


def test_pdf_validator_valid():
    fake_pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF" + b" " * 1000
    sha, pages = PDFValidator.validate_pdf_bytes(fake_pdf)
    assert len(sha) == 64
    assert pages >= 1


def test_pdf_validator_empty():
    with pytest.raises(NSEValidationError, match="empty"):
        PDFValidator.validate_pdf_bytes(b"")


def test_pdf_validator_html_error():
    html_bytes = b"<!DOCTYPE html><html><head><title>403 Forbidden</title></head><body>Forbidden</body></html>" + b" " * 1000
    with pytest.raises(NSEValidationError, match="HTML error page"):
        PDFValidator.validate_pdf_bytes(html_bytes)


def test_sha256_hash():
    h = compute_bytes_sha256(b"test data for hashing")
    assert len(h) == 64
    assert h == compute_bytes_sha256(b"test data for hashing")


def test_storage_manager(tmp_path):
    storage = StorageManager(base_dir=tmp_path)
    report = ReportMetadata(
        company="Infosys Limited",
        symbol="INFY",
        exchange=ExchangeType.NSE,
        year=2025,
        document_type=DocumentType.ANNUAL_REPORT,
        source="NSE",
        pdf_url="http://example.com/infy2025.pdf",
    )
    fake_pdf = b"%PDF-1.4\n" + b"x" * 2000
    pdf_path, meta_path = storage.store_report(report, fake_pdf, "dummyhash123", 45)

    assert pdf_path.exists()
    assert meta_path.exists()
    assert pdf_path.name == "raw.pdf"
    assert meta_path.name == "metadata.json"
    assert storage.is_already_stored("INFY", 2025) is True
    assert storage.is_already_stored("INFY", 2024) is False


# ── Live Network Integration Tests (curl_cffi Akamai Bypass) ──────

@pytest.mark.asyncio
async def test_live_nse_discovery():
    """Test live discovery from NSE API using curl_cffi TLS impersonation."""
    client = NSEClient()
    try:
        reports = await client.discover_annual_reports("INFY")
        assert len(reports) > 0
        assert reports[0].symbol == "INFY"
        assert "nsearchives.nseindia.com" in reports[0].pdf_url
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_live_sync_company():
    """Test full sync pipeline: discover, download, validate & save INFY annual report."""
    result = await sync_company("INFY")
    assert result.symbol == "INFY"
    assert result.reports_discovered > 0
    assert (result.reports_downloaded + result.reports_skipped) > 0
