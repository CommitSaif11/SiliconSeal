"""
FastAPI App Entry Point
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)
Mentor: Zoe 💙
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# FIX: Changed import paths for Saif
from . routers import api  # Changed from "app.routers"
from core import settings, Database  # This stays the same


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for Saif's app
    Handles startup and shutdown events
    """
    # Startup: Connect to MongoDB
    print("🚀 Starting up Saif's application...")
    await Database.connect()
    yield
    # Shutdown: Disconnect from MongoDB
    print("👋 Shutting down Saif's application...")
    await Database.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Automated Optical Inspection for IC Marking Verification",
    lifespan=lifespan
)

# CORS Middleware (For Frontend Integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with Vercel domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api. router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint - Health check"""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "author": "Saif (CommitSaif11)",
        "mentor": "Zoe 💙"
    }


# Optional: Allow running with `python src/app/main.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0. 0",
        port=8000,
        reload=True
    )