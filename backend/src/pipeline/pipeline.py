# Pipeline orchestrator: YOLO -> OCR -> Verify -> DB log
import asyncio
import base64
import logging
from typing import Optional, List, Dict, Any
from fastapi import UploadFile
import numpy as np
from datetime import datetime, timezone

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
        logger.info(
            f"Pipeline: KB index loaded (entries={len(kb_index.entries) if hasattr(kb_index, 'entries') else 'unknown'})"
        )
    except Exception as e:
        kb_index = None
        logger.warning(
            f"Pipeline: Could not load KB index at startup: {e}. Pipeline will still run but auto-detection may be limited."
        )


async def _run_detector_get_crops(image: "np.ndarray") -> List[Any]:
    """
    Try to run YOLO detector to get crop regions.
    If detector is not present or fails, return the original full image as single crop.
    Detector module expected (if present): pipeline.detector.yolo_detector with a function detect or detect_crops.
    """
    try:
        from pipeline.detector import yolo_detector as yolo
        if hasattr(yolo, "detect_crops"):
            crops = yolo.detect_crops(image)
        elif hasattr(yolo, "detect"):
            result = yolo.detect(image)
            if isinstance(result, list):
                crops = result
            elif isinstance(result, dict) and "crops" in result:
                crops = result["crops"]
            else:
                crops = [image]
        else:
            logger.warning("Detector found but no known detect function; using full image as crop")
            crops = [image]
        if not crops:
            return [image]
        return crops
    except Exception as e:
        logger.debug(f"No detector available or detector failed: {e}")
        return [image]


async def process_single_image(
    image_bytes: bytes,
    part_id: Optional[str],
    algorithm: str = "aho_corasick",
    enable_preprocessing: bool = False,  # ← Kept for API compatibility (Saif's decision 💙)
    db = None,
    resize_max: int = 1600
) -> Dict[str, Any]:
    """
    Full pipeline processing for a single image (async function).
    """
    global kb_index

    try:
        img = decode_image(image_bytes)
    except Exception as e:
        raise ValueError(f"Failed to decode uploaded image: {e}")

    img = resize_image_max(img, max_dim=resize_max)

    crops = await _run_detector_get_crops(img)
    primary_crop = crops[0] if crops else img

    # Run OCR
    try:
        ocr_results = run_ocr_multi_pass(primary_crop, enable_preprocessing=enable_preprocessing)
        full_text = ocr_results.get('full_alphanumeric', {}).get('text', '')
        logger.info(f"[OCR] full_alphanumeric.text='{full_text}'")
        cleaned = ''.join(c for c in full_text if c.isalnum())
        logger.info(f"[OCR] full_alphanumeric.cleaned='{cleaned}'")
    except Exception as e:
        logger.exception("OCR failed:", exc_info=e)
        raise

    # Verify
    try:
        if algorithm == "regex" and part_id:
            verification = verify_with_regex(ocr_results, part_id, kb_index)
        else:
            verification = verify_with_aho(ocr_results, part_id, kb_index)
    except Exception as e:
        logger.exception("Verification failed", exc_info=e)
        raise

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
        "preprocessing_applied": enable_preprocessing,
    }

    # DB logging
    try:
        if db is not None:
            full_text = ocr_results.get("full_text", "")
            rec_scores = ocr_results.get("rec_scores", [])
            avg_confidence = sum(rec_scores) / len(rec_scores) if rec_scores else 0.0

            log_doc = {
                "timestamp": datetime.now(timezone.utc),
                "part_id": part_id,
                "algorithm_used": response["algorithm_used"],
                "preprocessing_applied": enable_preprocessing,
                "ocr_text": full_text,
                "ocr_confidence": float(avg_confidence),
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
    enable_preprocessing: bool = False,
    db = None
) -> List[Dict[str, Any]]:
    async def _process_upload(file: UploadFile):
        content = await file.read()
        return await process_single_image(
            content,
            part_id,
            algorithm,
            enable_preprocessing=enable_preprocessing,
            db=db
        )

    tasks = [_process_upload(f) for f in files]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    return results