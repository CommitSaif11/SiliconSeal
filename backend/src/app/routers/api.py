"""
API Router - Core Endpoints (Final Merged Version)
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)


This file integrates:
- Pipeline (YOLO → OCR → Verify)
- KB loader
- MongoDB logging
- Admin tools
- Public operator endpoints

This is the final merged and stable version.
"""

import base64
from typing import Optional, List

from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    File,
    Form,
    Depends
)

from motor.motor_asyncio import AsyncIOMotorDatabase

# Core config + DB
from core.config import settings
from core import (
    get_database,
    PartsListResponse,
    KBEntryResponse
)

# KB loader (works with single kb.json file)
from engine.kb_loader import load_raw_kb, validate_entry

# Pipeline functions (YOLO → OCR → VERIFY)
from pipeline.pipeline import process_single_image, process_batch_images
from app.routers import kb_admin

router = APIRouter()

# =====================================================================================
# 1️⃣ HEALTH CHECK (App + Database)
# =====================================================================================
@router.get("/health")
async def health_check():
    """
    Health check endpoint for FastAPI + MongoDB status.
    Shown on dashboard & used by frontend for initial boot status.
    """
    try:
        db = await get_database()
        await db.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected ({str(e)})"

    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_status,
        "author": "Saif (CommitSaif11)",
        "mentor": "Zoe 💙"
    }


# =====================================================================================
# 2️⃣ GET /parts — Public operator endpoint
# =====================================================================================
@router.get("/parts", response_model=PartsListResponse)
async def get_parts_list():
    """
    Returns list of all part IDs in KB.
    
    NOTE:
    - Used for dropdown in frontend.
    - Does NOT expose OEM patterns (admin-only).
    """
    try:
        kb_data = load_raw_kb()
        part_ids = [entry["part_id"] for entry in kb_data]
        return {
            "status": "success",
            "count": len(part_ids),
            "parts": part_ids
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch parts: {str(e)}")


# =====================================================================================
# 3️⃣ POST /scan — Single image upload
# =====================================================================================
@router.post("/scan")
async def scan_image(
    file: UploadFile = File(...),
    part_id: Optional[str] = Form(None),        # Optional → auto-detect mode supported
    algorithm: str = Form("aho_corasick"),      # "regex" or "aho_corasick"
    enable_preprocessing: bool = Form(False),   # ← NEW: OCR preprocessing toggle 💙
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Performs the FULL pipeline on one uploaded image.
    Calls process_single_image() → YOLO → OCR → VERIFY → DB log.
    
    Args:
        file: Uploaded image file
        part_id: Optional part ID (auto-detect if None)
        algorithm: Verification algorithm ("regex" or "aho_corasick")
        enable_preprocessing: Apply OCR preprocessing (default: False)
        db: MongoDB database instance
    
    Returns:
        Complete verification result with OCR data, YOLO detection, and verification status
    
    Note for Saif:
        - enable_preprocessing=False (default): Raw image OCR - best for high-quality IC images
        - enable_preprocessing=True: Minimal preprocessing - may help low-quality images
    """
    try:
        image_bytes = await file.read()
        result = await process_single_image(
            image_bytes=image_bytes,
            part_id=part_id,
            algorithm=algorithm,
            enable_preprocessing=enable_preprocessing,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"Scan processing failed: {str(e)}")


# =====================================================================================
# 4️⃣ POST /scan/frame — Base64 image from live camera stream
# =====================================================================================
@router.post("/scan/frame")
async def scan_frame(
    frame: str = Form(...),                     # Base64 string
    part_id: Optional[str] = Form(None),
    algorithm: str = Form("aho_corasick"),
    enable_preprocessing: bool = Form(False),   # ← NEW: OCR preprocessing toggle 💙
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Used for continuous live-camera mode (webcam, mobile camera streaming).
    Base64 → decoded → pipeline. 
    
    Args:
        frame: Base64-encoded image string
        part_id: Optional part ID (auto-detect if None)
        algorithm: Verification algorithm ("regex" or "aho_corasick")
        enable_preprocessing: Apply OCR preprocessing (default: False)
        db: MongoDB database instance
    
    Returns:
        Complete verification result
    
    Note for Saif:
        - enable_preprocessing=False (default): Raw image OCR - recommended
        - enable_preprocessing=True: Minimal preprocessing for low-quality frames
    """
    try:
        image_bytes = base64.b64decode(frame)
        result = await process_single_image(
            image_bytes=image_bytes,
            part_id=part_id,
            algorithm=algorithm,
            enable_preprocessing=enable_preprocessing,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"Frame processing failed: {str(e)}")


# =====================================================================================
# 5️⃣ POST /scan/batch — Multiple images uploaded
# =====================================================================================
@router.post("/scan/batch")
async def scan_batch(
    files: List[UploadFile] = File(...),
    part_id: str = Form(...),
    algorithm: str = Form("regex"),             # Batch mode defaults to regex
    enable_preprocessing: bool = Form(False),   # ← NEW: OCR preprocessing toggle 💙
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Batch verification. Processes multiple uploads in parallel.
    
    Args:
        files: List of uploaded image files
        part_id: Part ID to verify against
        algorithm: Verification algorithm ("regex" or "aho_corasick")
        enable_preprocessing: Apply OCR preprocessing (default: False)
        db: MongoDB database instance
    
    Returns:
        Batch results with individual verification statuses
    
    Note for Saif:
        - enable_preprocessing=False (default): Raw image OCR for all images
        - enable_preprocessing=True: Applies preprocessing to all batch images
    """
    try:
        results = await process_batch_images(
            files=files,
            part_id=part_id,
            algorithm=algorithm,
            enable_preprocessing=enable_preprocessing,
            db=db
        )
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        raise HTTPException(500, f"Batch processing failed: {str(e)}")


# =====================================================================================
# 6️⃣ ADMIN: GET /kb — View full KB entries
# =====================================================================================
@router.get("/kb")
async def get_kb_list():
    """
    ADMIN ONLY — Show full KB entries (includes regex / metadata)
    🚨 AUTH WILL BE ADDED LATER using JWT.
    """
    try:
        kb_data = load_raw_kb()
        return {
            "status": "success",
            "access": "admin",
            "count": len(kb_data),
            "entries": kb_data
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to list KB: {str(e)}")


# =====================================================================================
# 7️⃣ ADMIN: GET /kb/{part_id} — Detailed OEM pattern
# =====================================================================================
@router.get("/kb/{part_id}", response_model=KBEntryResponse)
async def get_kb_entry(part_id: str):
    """
    ADMIN ONLY — Fetch full KB record for a single part.
    """
    try:
        kb_data = load_raw_kb()
        kb_entry = next((i for i in kb_data if i["part_id"] == part_id), None)
        if kb_entry is None:
            raise HTTPException(404, f"KB entry not found: {part_id}")
        validate_entry(kb_entry)
        return {
            "status": "success",
            "access": "admin",
            "part_id": part_id,
            "data": kb_entry
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to load KB entry: {str(e)}")


# =====================================================================================
# 8️⃣ ADMIN: POST /admin/reload-kb — Reload KB (for future dynamic updates)
# =====================================================================================
@router.post("/admin/reload-kb")
async def reload_knowledge_base():
    """
    Reload KB from disk. Useful during development.
    In future: This will trigger rebuilding Aho-Corasick automaton.
    """
    try:
        kb_data = load_raw_kb()
        return {
            "status": "success",
            "message": "KB reload successful",
            "count": len(kb_data)
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to reload KB: {str(e)}")
    

router.include_router(kb_admin.router, prefix="", tags=["admin"])