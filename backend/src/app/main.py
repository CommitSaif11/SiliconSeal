"""
FastAPI App Entry Point
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)

"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import router and core utilities
from app.routers import api
from core import settings, Database

# Pipeline initializer (loads KB index if available)
from pipeline.pipeline import initialize_pipeline

# Configure basic logging so startup messages are visible
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for Saif's app
    Handles startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting up Saif's application...")
    await Database.connect()

    try:
        # Initialize pipeline (loads KB index, optional detector/model preload)
        await initialize_pipeline()
    except Exception as e:
        logger.warning(f"Pipeline initialization warning: {e}")

    yield

    # Shutdown
    logger.info("👋 Shutting down Saif's application...")
    await Database.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Automated Optical Inspection for IC Marking Verification",
    lifespan=lifespan,
)

# CORS Middleware (For Frontend Integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint - Health check"""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "author": "Saif (CommitSaif11)",
        "mentor": "Zoe 💙",
    }


# Optional: Allow running with `python -m app.main`
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)