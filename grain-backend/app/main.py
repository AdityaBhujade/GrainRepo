"""
Grain App — FastAPI Backend

Main application entry point with:
- CORS middleware (for React Native / web access)
- Database initialization on startup
- APScheduler cron job for periodic Google Sheet sync
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import get_settings
from app.database import init_db, SessionLocal
from app.routers import customers
from app.services.sync_service import sync_sheet_to_db

# ─── Logging ────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── Scheduler ──────────────────────────────────────────────

scheduler = BackgroundScheduler()
settings = get_settings()


def scheduled_sync():
    """Cron job callback — runs sync in its own DB session."""
    logger.info("⏰ Scheduled sync triggered")
    db = SessionLocal()
    try:
        result = sync_sheet_to_db(db)
        logger.info(f"⏰ Scheduled sync result: {result['message']}")
    except Exception as e:
        logger.error(f"⏰ Scheduled sync failed: {e}", exc_info=True)
    finally:
        db.close()


# ─── App Lifespan ───────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    # ── Startup ──
    logger.info("🚀 Starting Grain App Backend...")

    # Create database tables (if not exist)
    init_db()
    logger.info("✅ Database tables initialized")

    # Start the scheduler
    scheduler.add_job(
        scheduled_sync,
        "interval",
        minutes=settings.sync_interval_minutes,
        id="sheet_sync",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        f"✅ Scheduler started — syncing every {settings.sync_interval_minutes} minutes"
    )

    # Run an initial sync on startup
    logger.info("🔄 Running initial sync on startup...")
    db = SessionLocal()
    try:
        result = sync_sheet_to_db(db)
        logger.info(f"✅ Initial sync: {result['message']}")
    except Exception as e:
        logger.warning(f"⚠️ Initial sync failed (will retry on schedule): {e}")
    finally:
        db.close()

    yield

    # ── Shutdown ──
    scheduler.shutdown()
    logger.info("🛑 Scheduler shut down")


# ─── FastAPI App ────────────────────────────────────────────

app = FastAPI(
    title="Grain App API",
    description="Backend for the Grain App — syncs customer data from Google Sheets",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins for development (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ─────────────────────────────────────────────────

app.include_router(customers.router, tags=["Customers"])


# ─── Root ───────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "app": "Grain App API",
        "version": "1.0.0",
        "docs": "/docs",
    }
