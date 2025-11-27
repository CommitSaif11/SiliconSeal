"""
API Router - Core Endpoints
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)
Mentor: Zoe 💙
"""


from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

# Import from new core module
from core import get_database, PartsListResponse, KBEntryResponse, ErrorResponse
from core.config import settings

# Import KB functions (will update these to work with single JSON file)
from engine.kb_loader import load_raw_kb, validate_entry


router = APIRouter()

# ============================================================
# 1️⃣ GET /health - Public Access
# ============================================================
@router.get("/health")
async def health_check():
    """
    Health check endpoint
    Access: Public
    Purpose: Check service status and database connection
    """
    try:
        # Try to ping database
        db = await get_database()
        await db.command('ping')
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
    
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_status,
        "author": "Saif (CommitSaif11)",
        "mentor": "Zoe 💙"
    }


# ============================================================
# 2️⃣ GET /parts - Operator Access (PUBLIC)
# ============================================================
@router.get("/parts", response_model=PartsListResponse)
async def get_parts_list():
    """
    Get list of available part IDs for dropdown
    Access: Operator (Public)
    Purpose: Returns ONLY part_ids (not full KB data)
    
    Returns: List of part IDs without . json extension
    """
    try:
        # Load KB from single JSON file
        kb_data = load_raw_kb()
        
        # Extract part_ids from the array
        part_ids = [entry["part_id"] for entry in kb_data]
        
        # Handle empty KB case
        if not part_ids:
            return {
                "status": "success",
                "count": 0,
                "parts": []
            }
        
        # Return successful response with part list
        return {
            "status": "success",
            "count": len(part_ids),
            "parts": part_ids
        }
        
    except Exception as e:
        # Handle any KB loader failures
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch parts list: {str(e)}"
        )


# ============================================================
# 3️⃣ POST /scan - Operator Access (One-shot scanning)
# ============================================================
@router.post("/scan")
async def scan_image(
    file: UploadFile = File(...),
    part_id: Optional[str] = Form(None),  # Made optional for auto-detection
    algorithm: str = Form("aho_corasick"),  # Added algorithm selection
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    One-shot image scanning with uploaded file
    Access: Operator
    Purpose: Upload image and verify IC marking
    
    Args:
        file: Uploaded image file
        part_id: IC part identifier (optional - for auto-detection mode)
        algorithm: "regex" or "aho_corasick" (default: aho_corasick)
    
    Returns: Verification result
    
    Note for Saif:
        Pipeline integration will be added in Phase 2
    """
    # TODO (Saif - Phase 2): Add YOLO detection + OCR + verification logic
    # Placeholder response for now
    return {
        "status": "success",
        "message": "Scan endpoint ready (pipeline integration pending)",
        "received": {
            "filename": file.filename,
            "content_type": file.content_type,
            "part_id": part_id,
            "algorithm": algorithm
        },
        "note": "Pipeline integration (YOLO → OCR → Verify) will be added in Phase 2"
    }


# ============================================================
# 4️⃣ POST /scan/frame - Operator Access (Live camera scanning)
# ============================================================
@router.post("/scan/frame")
async def scan_frame(
    frame: str = Form(...),
    part_id: Optional[str] = Form(None),
    algorithm: str = Form("aho_corasick"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Live camera frame scanning (continuous mode)
    Access: Operator
    Purpose: Real-time IC marking verification from camera feed
    
    Args:
        frame: Base64 encoded image frame
        part_id: IC part identifier (optional)
        algorithm: "regex" or "aho_corasick"
    
    Returns: Verification result
    
    Note for Saif:
        Pipeline integration will be added in Phase 2
    """
    # TODO (Saif - Phase 2): Add base64 decode + YOLO detection + OCR + verification logic
    return {
        "status": "success",
        "message": "Frame scan endpoint ready (pipeline integration pending)",
        "received": {
            "frame_length": len(frame),
            "part_id": part_id,
            "algorithm": algorithm
        },
        "note": "Real-time detection logic will be added in Phase 2"
    }


# ============================================================
# 5️⃣ POST /scan/batch - Operator Access (Batch scanning)
# ============================================================
@router.post("/scan/batch")
async def scan_batch(
    files: List[UploadFile] = File(...),
    part_id: str = Form(...),
    algorithm: str = Form("regex"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Batch image scanning with multiple uploaded files
    Access: Operator
    Purpose: Upload multiple images and verify IC markings in batch
    
    Args:
        files: List of uploaded image files
        part_id: IC part identifier
        algorithm: "regex" or "aho_corasick"
    
    Returns: Batch verification results
    
    Note for Saif:
        Pipeline integration will be added in Phase 2
    """
    # TODO (Saif - Phase 2): Add batch processing with YOLO + OCR + verification logic
    filenames = [file.filename for file in files]
    
    return {
        "status": "success",
        "message": "Batch scan endpoint ready (pipeline integration pending)",
        "received": {
            "file_count": len(files),
            "filenames": filenames,
            "part_id": part_id,
            "algorithm": algorithm
        },
        "note": "Batch detection and verification logic will be added in Phase 2"
    }


# ============================================================
# 6️⃣ GET /kb - ADMIN ONLY
# ============================================================
@router.get("/kb")
async def get_kb_list():
    """
    List all available KB entries (ADMIN ONLY)
    Access: Admin
    Purpose: View all KB entries in the system
    
    Returns: List of all KB entries with metadata
    
    Note for Saif:
        JWT authentication will be added in Phase 5
    """
    # TODO (Saif - Phase 5): Add authentication/authorization check for admin
    try:
        # Load entire KB from single JSON file
        kb_data = load_raw_kb()
        
        # Return all entries
        return {
            "status": "success",
            "access": "admin",
            "count": len(kb_data),
            "entries": kb_data,
            "note": "Admin authentication will be added in Phase 5"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to list KB entries: {str(e)}"
        )


# ============================================================
# 7️⃣ GET /kb/{part_id} - ADMIN ONLY
# ============================================================
@router. get("/kb/{part_id}", response_model=KBEntryResponse)
async def get_kb_entry(part_id: str):
    """
    Load full KB entry by part ID (ADMIN ONLY)
    Access: Admin
    Purpose: View complete OEM pattern data for a specific IC
    
    Args:
        part_id: The IC part identifier (e.g., "stm32f030c8t6")
    
    Returns: Full KB entry data as JSON
    
    Note for Saif:
        JWT authentication will be added in Phase 5
    """
    # TODO (Saif - Phase 5): Add authentication/authorization check for admin
    try:
        # Load entire KB
        kb_data = load_raw_kb()
        
        # Find the specific part_id
        kb_entry = None
        for entry in kb_data:
            if entry["part_id"] == part_id:
                kb_entry = entry
                break
        
        if kb_entry is None:
            raise HTTPException(
                status_code=404, 
                detail=f"KB entry not found for part_id: {part_id}"
            )
        
        # Validate KB structure
        try:
            validate_entry(kb_entry)
        except Exception as validation_error:
            raise HTTPException(
                status_code=500, 
                detail=f"Invalid KB structure for part_id: {part_id} - {str(validation_error)}"
            )
        
        return {
            "status": "success",
            "access": "admin",
            "part_id": part_id,
            "data": kb_entry
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to load KB entry: {str(e)}"
        )


# ============================================================
# 8️⃣ POST /admin/reload-kb - ADMIN ONLY (New Endpoint!)
# ============================================================
@router.post("/admin/reload-kb")
async def reload_knowledge_base():
    """
    Reload KB index from JSON file
    Access: Admin
    Purpose: Refresh KB index after manual updates to kb.json
    
    Returns: Success message with entry count
    
    Note for Saif:
        Useful during development when updating kb/kb.json
        Will add JWT auth in Phase 5
    """
    # TODO (Saif - Phase 5): Add authentication/authorization check for admin
    try:
        # This will be implemented when we create the pipeline orchestrator
        # For now, just validate KB can be loaded
        kb_data = load_raw_kb()
        
        return {
            "status": "success",
            "message": "KB reload endpoint ready",
            "count": len(kb_data),
            "note": "KB index reload logic will be added in Phase 2"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload KB: {str(e)}"
        )