"""
NSE Ingestion Service — Custom Exceptions Hierarchy
"""

class NSEIngestionError(Exception):
    """Base exception for all NSE ingestion service errors."""
    pass


class NSEClientError(NSEIngestionError):
    """Raised when HTTP network or API requests to NSE fail after max retries."""
    pass


class NSERateLimitError(NSEClientError):
    """Raised when NSE returns HTTP 429 Too Many Requests."""
    pass


class NSEValidationError(NSEIngestionError):
    """Raised when a downloaded file fails PDF format, size, or integrity checks."""
    pass


class NSEStorageError(NSEIngestionError):
    """Raised when file or directory operations fail."""
    pass


class NSEDeduplicationError(NSEIngestionError):
    """Raised when attempting duplicate processing of an already ingested report."""
    pass
