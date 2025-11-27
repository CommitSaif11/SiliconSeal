# Pipeline orchestrator: YOLO -> OCR -> Verify -> DB log
import asyncio
import base64
import logging
from typing import Optional, List, Dict, Any
from fastapi import UploadFile
import numpy as np
from core import get_database
from core.config import settings

from utils.image_utils import decode_image, resize_image_max
from pipeline.ocr.ocr import run_ocr_multi_pass
from pipeline.verify.verify import verify_with_aho, verify_with_regex

logger = logging.getLogger(__name__)

# Global KB index placeholder (attempt to load in initialize_pipeline)
kb_index = None


async def initialize_pipeline():
    """
    Attempt to load KB index (if engine.kb_index provides loader).
    This is optional; pipeline will still run with kb_index=None (auto-detection may be limited).
    """
    global kb_index
    try:
        from engine.kb_index import load_kb_index
        kb_index = load_kb_index()
        logger.info(f"Pipeline: KB index loaded (entries={len(kb_index.entries) if hasattr(kb_index, 'entries') else 'unknown'})")
    except Exception as e:
        kb_index = None
        logger.warning(f"Pipeline: Could not load KB index at startup: {e}. Pipeline will still run but auto-detection may be limited.")


async def _run_detector_get_crops(image: "np.ndarray") -> List[Any]:
    """
    Try to run YOLO detector to get crop regions.
    If detector is not present or fails, return the original full image as single crop.
    Detector module expected (if present): pipeline.detector.yolo_detector with a function detect or detect_crops.
    """
    try:
        # dynamic import to avoid hard dependency
        from pipeline.detector import yolo_detector as yolo
        # Try common function names
        if hasattr(yolo, "detect_crops"):
            crops = yolo.detect_crops(image)
        elif hasattr(yolo, "detect"):
            # some implementations return list of cropped images or bboxes
            result = yolo.detect(image)
            # If detect returns list of images, use that; otherwise attempt to extract crops if result has 'crops'
            if isinstance(result, list):
                crops = result
            elif isinstance(result, dict) and "crops" in result:
                crops = result["crops"]
            else:
                # fallback: use full image
                crops = [image]
        else:
            logger.warning("Detector found but no known detect function; using full image as crop")
            crops = [image]
        if not crops:
            return [image]
        return crops
    except Exception as e:
        logger.debug(f"No detector available or detector failed: {e}")
        # fallback to whole image
        return [image]


async def process_single_image(
    image_bytes: bytes,
    part_id: Optional[str],
    algorithm: str = "aho_corasick",
    db = None,
    resize_max: int = 1600
) -> Dict[str, Any]:
    """
    Full pipeline processing for a single image (async function).

    Steps:
      1. decode bytes -> OpenCV image
      2. optional resize
      3. YOLO detection -> get crop(s) (fallback to full image)
      4. OCR multi-pass on primary crop
      5. Verification (regex or aho)
      6. Log result to MongoDB (if db provided)
      7. Return dict matching VerificationResponse schema

    Note: kb_index is used by verification modules; it's loaded in initialize_pipeline() if available.
    """
    global kb_index

    # 1. Decode image
    try:
        img = decode_image(image_bytes)
    except Exception as e:
        raise ValueError(f"Failed to decode uploaded image: {e}")

    # 2. Resize if too large
    img = resize_image_max(img, max_dim=resize_max)

    # 3. Detection -> crops
    crops = await _run_detector_get_crops(img)
    # Prefer first crop (primary IC). If crops are not numpy images, try to handle gracefully.
    primary_crop = crops[0] if crops else img

    # 4. OCR (multi-pass)
    try:
        ocr_results = run_ocr_multi_pass(primary_crop)
    except Exception as e:
        # OCR is synchronous; wrap in thread if heavy — currently call directly
        logger.exception("OCR failed:", exc_info=e)
        raise

    # 5. Verification
    try:
        if algorithm == "regex" and part_id:
            verification = verify_with_regex(ocr_results, part_id, kb_index)
        else:
            # default to Aho auto-detection
            verification = verify_with_aho(ocr_results, part_id, kb_index)
    except Exception as e:
        logger.exception("Verification failed", exc_info=e)
        raise

    # Build response dict (lightweight conversion from VerificationResult dataclass)
    response = {
        "status": "success",
        "verdict": verification.verdict,
        "confidence_score": float(verification.confidence_score) if verification.confidence_score is not None else 0.0,
        "matches": verification.matches or {},
        "extracted_fields": verification.extracted_fields or {},
        "oem_info": verification.oem_info or {},
        "algorithm_used": verification.algorithm_used or algorithm,
        "flags": verification.flags or [],
        "requires_admin_review": verification.requires_admin_review,
        "candidate_parts": verification.candidate_parts or [],
    }

    # 6. Log to DB if provided
    try:
        if db is not None:
            log_doc = {
                "timestamp": __import__("datetime").datetime.utcnow(),
                "part_id": part_id,
                "algorithm_used": response["algorithm_used"],
                "ocr_text": " ".join([
                    ocr_results.get("full_alphanumeric", {}).get("text", ""),
                    ocr_results.get("numeric_only", {}).get("text", ""),
                    ocr_results.get("alpha_only", {}).get("text", "")
                ]).strip(),
                "ocr_confidence": float((ocr_results.get("full_alphanumeric", {}).get("confidence", 0.0) +
                                         ocr_results.get("numeric_only", {}).get("confidence", 0.0)) / 2.0),
                "verdict": response["verdict"],
                "confidence_score": response["confidence_score"],
                "matches": response["matches"],
                "extracted_fields": response["extracted_fields"],
                "oem_info": response["oem_info"],
                "flags": response["flags"],
                "requires_admin_review": response["requires_admin_review"],
            }
            await db.verification_logs.insert_one(log_doc)
    except Exception as e:
        logger.warning(f"Failed to write verification log to DB: {e}")

    return response


async def process_batch_images(
    files: List[UploadFile],
    part_id: Optional[str],
    algorithm: str,
    db = None
) -> List[Dict[str, Any]]:
    """
    Process multiple uploaded files in parallel and return list of responses.
    """
    # Read files concurrently
    loop = asyncio.get_event_loop()

    async def _process_upload(file: UploadFile):
        content = await file.read()
        return await process_single_image(content, part_id, algorithm, db)

    tasks = [_process_upload(f) for f in files]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    return results