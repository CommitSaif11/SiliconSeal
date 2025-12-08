"""
OCR Module - Based on Saif's Working Test Script
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)


This is a direct conversion of Saif's test script that works perfectly.
NO modifications to the core logic.
"""

import os
import tempfile
import logging
from typing import List, Dict, Any, Optional
import numpy as np
import cv2
from paddleocr import PaddleOCR
import paddle

logger = logging.getLogger(__name__)

# Singleton OCR instance
_ocr_instance = None


def safe_len(x):
    """Saif's helper function - unchanged"""
    try:
        return len(x)
    except Exception:
        return 0


def to_list(x):
    """Saif's helper function - unchanged"""
    try:
        import numpy as np
        if isinstance(x, np.ndarray):
            return x.tolist()
    except Exception:
        pass
    if isinstance(x, (list, tuple)):
        return [to_list(i) for i in x]
    return x


def get_ocr_instance() -> PaddleOCR:
    """Get singleton PaddleOCR instance - Saif's settings"""
    global _ocr_instance
    if _ocr_instance is None:
        try:
            paddle.set_device("cpu")
        except Exception as e:
            logger.warning(f"Device selection warning: {e}")

        _ocr_instance = PaddleOCR(lang="en", use_textline_orientation=True)
        logger.info("PaddleOCR initialized (Saif's config)")
    return _ocr_instance


def run_paddleocr(img: np.ndarray, min_score: float = 0.80) -> Dict[str, Any]:
    """
    Run PaddleOCR on image - Saif's logic exactly.

    Args:
        img: OpenCV image (numpy array)
        min_score: Minimum confidence threshold

    Returns:
        Dict with rec_texts, rec_scores, rec_polys, filtered_items
    """
    ocr = get_ocr_instance()

    # Save to temp file (required by ocr.predict)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        cv2.imwrite(tmp.name, img)
        temp_path = tmp.name

    try:
        res_list = ocr.predict(temp_path)
    finally:
        os.unlink(temp_path)

    if not res_list:
        logger.warning("No OCR results")
        return {
            "rec_texts": [],
            "rec_scores": [],
            "rec_polys": [],
            "rec_boxes": [],
            "filtered_items": []
        }

    ocr_result = res_list[0]

    rec_texts = ocr_result.get("rec_texts", [])
    rec_scores = ocr_result.get("rec_scores", [])
    rec_boxes = ocr_result.get("rec_boxes", [])
    rec_polys = ocr_result.get("rec_polys", [])

    n_texts = safe_len(rec_texts)
    n_scores = safe_len(rec_scores)
    n_boxes = safe_len(rec_boxes)
    n_polys = safe_len(rec_polys)
    n = min(n_texts, n_scores) if n_scores > 0 else n_texts

    def get_box_or_poly(i):
        """Saif's helper - unchanged"""
        if n_boxes > i:
            return rec_boxes[i]
        if n_polys > i:
            return rec_polys[i]
        return None

    # Filter by score - Saif's logic
    items = []
    for i in range(n):
        t = rec_texts[i]
        s = rec_scores[i] if n_scores > i else None
        b = get_box_or_poly(i)
        if s is not None and s < min_score:
            continue
        if isinstance(t, str) and t.strip() == "":
            continue
        items.append((t, s, b))

    logger.info(f"Found {len(items)} items after filtering (min_score={min_score})")

    return {
        "rec_texts": rec_texts,
        "rec_scores": rec_scores,
        "rec_polys": rec_polys,
        "rec_boxes": rec_boxes,
        "filtered_items": items
    }


def group_lines_by_y(items: List[tuple], tolerance: float = 6.0) -> List[Dict[str, Any]]:
    """
    Group items by Y coordinate - Saif's logic exactly.

    Args:
        items: List of (text, score, box/poly) tuples
        tolerance: Y-distance tolerance for grouping

    Returns:
        List of grouped lines with y center and texts
    """
    rows = []
    for (t, s, b) in items:
        if b is None:
            continue
        try:
            # poly case: [[x,y], ...]
            if hasattr(b, "__len__") and safe_len(b) > 0 and hasattr(b[0], "__len__"):
                y_vals = [pt[1] for pt in b]
                y_center = float(sum(y_vals) / len(y_vals))
            else:
                # box case: [x,y,w,h]
                y_center = float(b[1]) if safe_len(b) > 1 else 0.0
        except Exception:
            y_center = 0.0
        rows.append((y_center, t))

    rows.sort(key=lambda r: r[0])

    grouped = []
    for y, t in rows:
        if not grouped or abs(y - grouped[-1]["y"]) > tolerance:
            grouped.append({"y": y, "texts": [t]})
        else:
            grouped[-1]["texts"].append(t)

    return grouped


def extract_numeric_only(text: str) -> str:
    """Extract only numeric characters from text"""
    return ''.join(c for c in text if c.isdigit())


def extract_alpha_only(text: str) -> str:
    """Extract only alphabetic characters from text"""
    return ''.join(c for c in text if c.isalpha())


def run_ocr_multi_pass(
    img: np.ndarray,
    min_score: float = 0.80,
    enable_preprocessing: bool = False
) -> Dict[str, Any]:
    """
    Main OCR function for pipeline - based on Saif's script.

    Args:
        img: OpenCV image
        min_score: Minimum confidence threshold
        enable_preprocessing: Kept for API compatibility (unused - empirical testing showed raw images work best)

    Returns:
        Structured OCR result with grouped lines + verification-ready fields
    """
    _ = enable_preprocessing  # Suppress linter warning

    result = run_paddleocr(img, min_score=min_score)
    items = result["filtered_items"]

    if not items:
        return {
            "rec_texts": [],
            "rec_scores": [],
            "grouped_lines": [],
            "full_text": "",
            "full_alphanumeric": {"text": "", "confidence": 0.0},
            "numeric_only": {"text": "", "confidence": 0.0},
            "alpha_only": {"text": "", "confidence": 0.0}
        }

    grouped = group_lines_by_y(items, tolerance=6.0)

    full_text = " ".join([" ".join(g["texts"]) for g in grouped])
    full_text_upper = full_text.upper()

    scores = result["rec_scores"]
    avg_conf = sum(scores) / len(scores) if scores else 0.0

    numeric_text = extract_numeric_only(full_text_upper)
    alpha_text = extract_alpha_only(full_text_upper)

    return {
        "rec_texts": result["rec_texts"],
        "rec_scores": result["rec_scores"],
        "grouped_lines": grouped,
        "full_text": full_text_upper,
        "full_alphanumeric": {
            "text": full_text_upper,
            "confidence": avg_conf
        },
        "numeric_only": {
            "text": numeric_text,
            "confidence": avg_conf
        },
        "alpha_only": {
            "text": alpha_text,
            "confidence": avg_conf
        }
    }


def run_ocr(img: np.ndarray, enable_preprocessing: bool = False) -> tuple:
    """
    Simple wrapper for backward compatibility.

    Returns:
        (text, confidence)
    """
    _ = enable_preprocessing  # Suppress linter warning

    result = run_ocr_multi_pass(img)
    text = result.get("full_text", "")

    scores = result.get("rec_scores", [])
    avg_conf = sum(scores) / len(scores) if scores else 0.0

    return text, avg_conf