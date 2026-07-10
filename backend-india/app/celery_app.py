"""
QuantView — Celery Application

Task queue configuration for background data ingestion,
knowledge extraction, and scheduled pipelines.
"""

from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "quantview_india",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone (IST)
    timezone="Asia/Kolkata",
    enable_utc=True,

    # Task execution
    task_soft_time_limit=300,     # 5 minutes soft limit
    task_time_limit=600,          # 10 minutes hard limit
    task_acks_late=True,          # Acknowledge after completion
    worker_prefetch_multiplier=1, # Don't prefetch, process one at a time

    # Retry
    task_default_retry_delay=60,  # 1 minute between retries
    task_max_retries=3,

    # Rate limiting (be gentle with free-tier services)
    task_default_rate_limit="10/m",

    # Periodic task schedule (Celery Beat)
    beat_schedule={
        # ── Daily after market close ──────────────────────
        "ingest-daily-prices": {
            "task": "app.ingestion.price_collector.ingest_daily_prices",
            "schedule": crontab(hour=11, minute=0),  # 4:30 PM IST = 11:00 UTC
        },
        "ingest-index-data": {
            "task": "app.ingestion.index_collector.ingest_index_data",
            "schedule": crontab(hour=11, minute=30),  # 5:00 PM IST
        },
        "ingest-fii-dii": {
            "task": "app.ingestion.fii_dii_collector.ingest_fii_dii_activity",
            "schedule": crontab(hour=12, minute=30),  # 6:00 PM IST
        },
        "ingest-insider-trades": {
            "task": "app.ingestion.insider_collector.ingest_insider_trades",
            "schedule": crontab(hour=13, minute=30),  # 7:00 PM IST
        },
        "ingest-corporate-actions": {
            "task": "app.ingestion.corporate_action_collector.ingest_corporate_actions",
            "schedule": crontab(hour=14, minute=30),  # 8:00 PM IST
        },

        # ── Frequent during market hours ──────────────────
        "ingest-live-news": {
            "task": "app.ingestion.news_collector.ingest_news",
            "schedule": crontab(minute="*/15", hour="3-10"),  # Every 15 min, 8:30 AM - 4 PM IST
        },

        # ── Nightly pipeline ──────────────────────────────
        "run-knowledge-extraction": {
            "task": "app.extraction.pipeline.run_extraction_pipeline",
            "schedule": crontab(hour=17, minute=30),  # 11:00 PM IST
        },
        "update-ai-scores": {
            "task": "app.services.score_service.update_all_scores",
            "schedule": crontab(hour=18, minute=30),  # 12:00 AM IST
        },
        "generate-daily-intelligence": {
            "task": "app.services.market_service.generate_daily_intelligence",
            "schedule": crontab(hour=19, minute=30),  # 1:00 AM IST
        },

        # ── Weekly ────────────────────────────────────────
        "ingest-shareholding": {
            "task": "app.ingestion.shareholding_collector.ingest_shareholding_patterns",
            "schedule": crontab(hour=18, minute=0, day_of_week="sun"),  # Sunday 11:30 PM IST
        },

        # ── Monthly ───────────────────────────────────────
        "ingest-mf-holdings": {
            "task": "app.ingestion.mf_holdings_collector.ingest_mf_holdings",
            "schedule": crontab(hour=18, minute=0, day_of_month="1"),  # 1st of month
        },

        # ── Keep-alive for Neo4j Aura Free ────────────────
        "neo4j-keep-alive": {
            "task": "app.db.neo4j.keep_alive",
            "schedule": crontab(hour=0, minute=30),  # 6:00 AM IST daily
        },
    },
)

# Auto-discover tasks from these modules
celery_app.autodiscover_tasks([
    "app.ingestion",
    "app.extraction",
    "app.services",
])
