"""
QuantView Indian Market Backend — Custom Exceptions

Structured exception hierarchy for consistent error handling
across the application.
"""


class QuantViewError(Exception):
    """Base exception for all QuantView errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


# ── Data Layer Exceptions ────────────────────────────────────────


class DatabaseError(QuantViewError):
    """Database connection or query errors."""

    def __init__(self, message: str):
        super().__init__(message, code="DATABASE_ERROR", status_code=500)


class CompanyNotFoundError(QuantViewError):
    """Requested company does not exist in the database."""

    def __init__(self, symbol: str):
        super().__init__(
            f"Company with symbol '{symbol}' not found",
            code="COMPANY_NOT_FOUND",
            status_code=404,
        )


class DocumentNotFoundError(QuantViewError):
    """Requested document does not exist."""

    def __init__(self, document_id: int):
        super().__init__(
            f"Document with ID {document_id} not found",
            code="DOCUMENT_NOT_FOUND",
            status_code=404,
        )


# ── Ingestion Exceptions ────────────────────────────────────────


class IngestionError(QuantViewError):
    """Data ingestion pipeline errors."""

    def __init__(self, message: str, source: str = "unknown"):
        self.source = source
        super().__init__(
            f"Ingestion error from {source}: {message}",
            code="INGESTION_ERROR",
            status_code=500,
        )


class ScraperError(IngestionError):
    """Web scraping failures (rate limits, blocked, timeouts)."""

    def __init__(self, message: str, source: str, url: str = ""):
        self.url = url
        super().__init__(f"{message} (URL: {url})", source=source)


class DataValidationError(QuantViewError):
    """Ingested data fails validation rules."""

    def __init__(self, message: str, field: str = ""):
        self.field = field
        super().__init__(
            f"Data validation failed for '{field}': {message}",
            code="VALIDATION_ERROR",
            status_code=422,
        )


# ── AI/Agent Exceptions ─────────────────────────────────────────


class AIServiceError(QuantViewError):
    """AI model server or LLM inference errors."""

    def __init__(self, message: str):
        super().__init__(message, code="AI_SERVICE_ERROR", status_code=503)


class AgentError(QuantViewError):
    """Agent execution failure."""

    def __init__(self, agent_name: str, message: str):
        self.agent_name = agent_name
        super().__init__(
            f"Agent '{agent_name}' failed: {message}",
            code="AGENT_ERROR",
            status_code=500,
        )


class AgentTimeoutError(AgentError):
    """Agent took too long to respond."""

    def __init__(self, agent_name: str, timeout_seconds: int):
        super().__init__(
            agent_name, f"Timed out after {timeout_seconds}s"
        )


# ── Search Exceptions ───────────────────────────────────────────


class SearchError(QuantViewError):
    """Search service failure (Qdrant, OpenSearch)."""

    def __init__(self, message: str, service: str = "unknown"):
        self.service = service
        super().__init__(
            f"Search error ({service}): {message}",
            code="SEARCH_ERROR",
            status_code=500,
        )


# ── External Service Exceptions ─────────────────────────────────


class ExternalServiceError(QuantViewError):
    """External API/service failure."""

    def __init__(self, service: str, message: str):
        self.service = service
        super().__init__(
            f"External service '{service}' error: {message}",
            code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
        )


class RateLimitError(ExternalServiceError):
    """Rate limited by external service."""

    def __init__(self, service: str, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(service, f"Rate limited, retry after {retry_after}s")
