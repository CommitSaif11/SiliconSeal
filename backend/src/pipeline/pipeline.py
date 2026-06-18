import asyncio
import logging
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from fastapi import UploadFile
import numpy as np

from utils.image_utils import decode_image, resize_image_max
from pipeline.ocr.ocr import run_ocr_multi_pass
from pipeline.verify.verify import verify_with_aho, verify_with_regex

logger = logging.getLogger(__name__)

kb_index = None
_ocr_executor = ThreadPoolExecutor(max_workers=4)


async def initialize_pipeline():
    global kb_index
    try:
        from engine.kb_index import load_kb_index
        kb_index = load_kb_index()
        logger.info(
            f"Pipeline: KB index loaded (entries={len(kb_index.entries) if hasattr(kb_index, 'entries') else 'unknown'})"
        )
    except Exception as e:
        kb_index = None
        logger.warning(f"Pipeline: Could not load KB index at startup: {e}")


async def reload_kb_index() -> int:
    global kb_index
    from engine.kb_index import load_kb_index
    kb_index = load_kb_index()
    count = len(kb_index.entries) if hasattr(kb_index, "entries") else 0
    logger.info(f"Pipeline: KB index reloaded (entries={count})")
    return count


async def _run_detector_get_crops(image: "np.ndarray") -> List[Any]:
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
            crops = [image]
        if not crops:
            return [image]
        return crops
    except Exception as e:
        logger.debug(f"No detector available or detector failed: {e}")
        return [image]


def _run_ocr_sync(crop: np.ndarray, enable_preprocessing: bool) -> Dict[str, Any]:
    return run_ocr_multi_pass(crop, enable_preprocessing=enable_preprocessing)


async def process_single_image(
    image_bytes: bytes,
    part_id: Optional[str],
    algorithm: str = "aho_corasick",
    enable_preprocessing: bool = False,
    resize_max: int = 1600
) -> Dict[str, Any]:
    global kb_index

    try:
        img = decode_image(image_bytes)
    except Exception as e:
        raise ValueError(f"Failed to decode uploaded image: {e}")

    img = resize_image_max(img, max_dim=resize_max)
    crops = await _run_detector_get_crops(img)
    primary_crop = crops[0] if crops else img

    loop = asyncio.get_running_loop()
    try:
        ocr_results = await loop.run_in_executor(
            _ocr_executor, _run_ocr_sync, primary_crop, enable_preprocessing
        )
        full_text = ocr_results.get('full_alphanumeric', {}).get('text', '')
        logger.info(f"[OCR] full_alphanumeric.text='{full_text}'")
    except Exception as e:
        logger.exception("OCR failed:", exc_info=e)
        raise

    try:
        if algorithm == "regex" and part_id:
            verification = verify_with_regex(ocr_results, part_id, kb_index)
        else:
            verification = verify_with_aho(ocr_results, part_id, kb_index)
    except Exception as e:
        logger.exception("Verification failed", exc_info=e)
        raise

    return {
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


async def process_batch_images(
    files: List[UploadFile],
    part_id: Optional[str],
    algorithm: str,
    enable_preprocessing: bool = False,
) -> List[Dict[str, Any]]:
    async def _process_upload(file: UploadFile) -> Dict[str, Any]:
        try:
            content = await file.read()
            result = await process_single_image(
                content,
                part_id,
                algorithm,
                enable_preprocessing=enable_preprocessing,
            )
            result["filename"] = file.filename
            return result
        except Exception as e:
            return {
                "status": "error",
                "filename": file.filename,
                "error": str(e),
                "verdict": "ERROR",
                "confidence_score": 0.0,
            }

    tasks = [_process_upload(f) for f in files]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    return results
