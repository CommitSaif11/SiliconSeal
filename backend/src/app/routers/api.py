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

from core.config import settings
from core import require_admin, PartsListResponse, KBEntryResponse

from engine.kb_loader import load_raw_kb, validate_entry
from pipeline.pipeline import process_single_image, process_batch_images, reload_kb_index
from app.routers import kb_admin

router = APIRouter()

MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
MAX_BASE64_BYTES = MAX_UPLOAD_BYTES * 4 // 3 + 100


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/parts", response_model=PartsListResponse)
async def get_parts_list():
    try:
        from pipeline.pipeline import kb_index as _idx
        if _idx is not None and hasattr(_idx, "entries"):
            part_ids = [e.part_id for e in _idx.entries]
        else:
            kb_data = load_raw_kb()
            part_ids = [entry["part_id"] for entry in kb_data]
        return {
            "status": "success",
            "count": len(part_ids),
            "parts": part_ids
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch parts: {str(e)}")


@router.post("/scan")
async def scan_image(
    file: UploadFile = File(...),
    part_id: Optional[str] = Form(None),
    algorithm: str = Form("aho_corasick"),
    enable_preprocessing: bool = Form(False),
    use_ai: bool = Form(False),
):
    image_bytes = await file.read()
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"File too large. Max {settings.MAX_UPLOAD_SIZE_MB}MB")

    try:
        result = await process_single_image(
            image_bytes=image_bytes,
            part_id=part_id,
            algorithm=algorithm,
            enable_preprocessing=enable_preprocessing,
        )

        if use_ai and settings.AI_ENABLED and settings.GROQ_API_KEY:
            from pipeline.intelligence.ai_agent import analyze_verification
            ai_result = await analyze_verification(result)
            result["ai_analysis"] = ai_result

        return result
    except Exception as e:
        raise HTTPException(500, f"Scan processing failed: {str(e)}")


@router.post("/scan/frame")
async def scan_frame(
    frame: str = Form(...),
    part_id: Optional[str] = Form(None),
    algorithm: str = Form("aho_corasick"),
    enable_preprocessing: bool = Form(False),
    use_ai: bool = Form(False),
):
    if len(frame) > MAX_BASE64_BYTES:
        raise HTTPException(413, f"Frame too large. Max {settings.MAX_UPLOAD_SIZE_MB}MB decoded")

    try:
        image_bytes = base64.b64decode(frame)
    except Exception:
        raise HTTPException(400, "Invalid base64 encoding")

    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"Decoded frame too large. Max {settings.MAX_UPLOAD_SIZE_MB}MB")

    try:
        result = await process_single_image(
            image_bytes=image_bytes,
            part_id=part_id,
            algorithm=algorithm,
            enable_preprocessing=enable_preprocessing,
        )

        if use_ai and settings.AI_ENABLED and settings.GROQ_API_KEY:
            from pipeline.intelligence.ai_agent import analyze_verification
            ai_result = await analyze_verification(result)
            result["ai_analysis"] = ai_result

        return result
    except Exception as e:
        raise HTTPException(500, f"Frame processing failed: {str(e)}")


@router.post("/scan/batch")
async def scan_batch(
    files: List[UploadFile] = File(...),
    part_id: Optional[str] = Form(None),
    algorithm: str = Form("regex"),
    enable_preprocessing: bool = Form(False),
):
    if len(files) > settings.MAX_BATCH_FILES:
        raise HTTPException(413, f"Too many files. Max {settings.MAX_BATCH_FILES} per batch")

    for f in files:
        content = await f.read()
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(413, f"File '{f.filename}' too large. Max {settings.MAX_UPLOAD_SIZE_MB}MB")
        await f.seek(0)

    try:
        results = await process_batch_images(
            files=files,
            part_id=part_id,
            algorithm=algorithm,
            enable_preprocessing=enable_preprocessing,
        )
        return {
            "status": "success",
            "total": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(500, f"Batch processing failed: {str(e)}")


# --- Admin endpoints (JWT required) ---

@router.get("/kb")
async def get_kb_list(_user: dict = Depends(require_admin)):
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


@router.get("/kb/{part_id}", response_model=KBEntryResponse)
async def get_kb_entry(part_id: str, _user: dict = Depends(require_admin)):
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


@router.post("/admin/reload-kb")
async def reload_knowledge_base(_user: dict = Depends(require_admin)):
    try:
        count = await reload_kb_index()
        return {
            "status": "success",
            "message": "KB reloaded and index rebuilt",
            "count": count
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to reload KB: {str(e)}")


router.include_router(kb_admin.router, prefix="", tags=["admin"])
