"""
QuantView Indian Market Backend — FastAPI Application

Main entry point for the Indian market backend service.
Mounts all API routers and initializes database connections.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.config import get_settings
from app.core.exceptions import QuantViewError
from app.db.postgres import async_engine, Base
from app.db.qdrant import init_qdrant_collection
from app.db.opensearch import init_opensearch_index
from app.db.neo4j import init_neo4j_schema, close_neo4j
from app.db.redis import close_redis

# Import all models so SQLAlchemy knows about them
import app.models  # noqa: F401

# Import API routers
from app.api.routes_market import router as market_router
from app.api.routes_company import router as company_router
from app.api.routes_ai import router as ai_router
from app.api.routes_screener import router as screener_router
from app.api.routes_graph import router as graph_router
from app.api.routes_quant import router as quant_router
from app.api.routes_portfolio import router as portfolio_router
from app.api.routes_watchlist import router as watchlist_router
from app.api.routes_sectors import router as sectors_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan — initialize and teardown resources.
    Runs once at startup and shutdown.
    """
    print("🚀 QuantView India Backend starting up...")

    # Initialize PostgreSQL tables (for development)
    if settings.app_env == "development":
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("  ✅ PostgreSQL tables created/verified")

    # Initialize external services (gracefully handle failures)
    try:
        init_qdrant_collection()
    except Exception as e:
        print(f"  ⚠️ Qdrant init failed (will retry on first use): {e}")

    try:
        await init_neo4j_schema()
    except Exception as e:
        print(f"  ⚠️ Neo4j init failed (will retry on first use): {e}")

    try:
        init_opensearch_index()
    except Exception as e:
        print(f"  ⚠️ OpenSearch init failed (will retry on first use): {e}")

    print("✅ QuantView India Backend ready!")

    yield

    # Cleanup
    print("🛑 Shutting down...")
    await close_neo4j()
    await close_redis()
    await async_engine.dispose()
    print("✅ Shutdown complete")


# ── Create FastAPI App ───────────────────────────────────────────

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="AI-Powered Financial Research Platform for Indian Markets",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS Middleware ──────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "https://quantview.com",
        "https://www.quantview.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Timing Middleware ────────────────────────────────────

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    return response


# ── Exception Handlers ──────────────────────────────────────────

@app.exception_handler(QuantViewError)
async def quantview_exception_handler(request: Request, exc: QuantViewError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.code,
            "message": exc.message,
        },
    )


# ── Mount API Routers ───────────────────────────────────────────

app.include_router(market_router, prefix="/api/v1/market", tags=["Market Data"])
app.include_router(company_router, prefix="/api/v1/company", tags=["Company Data"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["AI Research"])
app.include_router(screener_router, prefix="/api/v1/screener", tags=["Screener"])
app.include_router(graph_router, prefix="/api/v1/graph", tags=["Knowledge Graph"])
app.include_router(quant_router, prefix="/api/v1/quant", tags=["Quant Lab"])
app.include_router(portfolio_router, prefix="/api/v1/portfolio", tags=["Portfolio"])
app.include_router(watchlist_router, prefix="/api/v1/watchlist", tags=["Watchlist"])
app.include_router(sectors_router, prefix="/api/v1/sectors", tags=["Sectors"])


# ── Health Check ─────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "quantview-india",
        "version": settings.app_version,
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "service": "QuantView India API",
        "version": settings.app_version,
        "docs": "/docs",
    }
