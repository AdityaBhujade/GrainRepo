"""
Grain App — FastAPI Backend

Main application entry point with:
- CORS middleware (for React Native / web access)
- Google Sheets-backed API endpoints
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import customers

# ─── Logging ────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─── App Lifespan ───────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    logger.info("🚀 Starting Grain App Backend in Google Sheets-only mode...")

    yield

    logger.info("🛑 Grain App Backend shut down")


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
