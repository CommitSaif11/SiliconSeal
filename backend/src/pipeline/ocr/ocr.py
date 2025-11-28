"""
OCR Module - PaddleOCR-Based IC Text Extraction
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)
Mentor: Zoe 💙

Complete rewrite using PaddleOCR v3.3+ for IC chip text recognition.

Features:
- Multi-pass OCR with confidence thresholding
- Intelligent multi-line merging using pattern matching
- CLAHE preprocessing for low-contrast enhancement
- Line grouping by Y-coordinate
"""

import cv2
import numpy as np
import re
from typing import Tuple, Dict, List, Optional, Any
from dataclasses import dataclass
from paddleocr import PaddleOCR
import logging

# Import pattern matching utilities
from .patterns import (
    matches_known_pattern,
    is_valid_part_code_format,
    get_manufacturer_prefix
)


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIDENCE THRESHOLDS
# ============================================================================

class ConfidenceThresholds:
    """
    OCR confidence thresholds for different field types.
    """
    PART_CODE = 0.92
    LOT_CODE = 0.85
    MANUFACTURER = 0.80
    COUNTRY = 0.80
    DATE_CODE = 0.85
    OVERALL_PASS = 0.85


# ============================================================================
# PROCESSING PARAMETERS
# ============================================================================

class ProcessingParams:
    """Parameters for OCR processing pipeline."""
    # Line grouping tolerance (pixels)
    LINE_GROUP_Y_TOLERANCE = 10.0

    # Partial match threshold
    PARTIAL_MATCH_THRESHOLD = 0.80  # Accept if ≥80% of expected code matches

    # Minimum part code length
    MIN_PART_CODE_LENGTH = 6

    # Noise removal threshold (connected component area)
    MIN_COMPONENT_AREA = 10

    # CLAHE parameters
    CLAHE_CLIP_LIMIT = 3.0
    CLAHE_TILE_SIZE = (8, 8)

    # Denoising parameters
    DENOISE_H = 10
    DENOISE_TEMPLATE_WINDOW = 7
    DENOISE_SEARCH_WINDOW = 21

    # Sharpening parameters
    SHARPEN_GAUSSIAN_SIGMA = 2.0
    SHARPEN_WEIGHT_ORIGINAL = 1.5
    SHARPEN_WEIGHT_GAUSSIAN = -0.5

    # Adaptive threshold parameters
    ADAPTIVE_BLOCK_SIZE = 25
    ADAPTIVE_C = 10


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class OCRToken:
    """Represents a single OCR detection result."""
    text: str
    confidence: float
    bbox: List[List[float]]  # 4 corner points [[x,y], [x,y], [x,y], [x,y]]
    y_center: float
    x_center: float


@dataclass
class GroupedLine:
    """Represents a group of tokens on the same line."""
    line_number: int
    tokens: List[OCRToken]
    merged_text: str
    avg_confidence: float
    y_position: float


# ============================================================================
# PADDLEOCR INITIALIZATION
# ============================================================================

# Global OCR instance (initialized once for performance)
_ocr_instance = None

def get_ocr_instance() -> PaddleOCR:
    """
    Get or create PaddleOCR instance (singleton pattern).

    Returns:
        PaddleOCR instance configured for IC text recognition

    Note:
        - Uses CPU by default (set use_gpu=True for CUDA acceleration)
        - use_textline_orientation=True enables auto-rotation
        - lang='en' optimized for alphanumeric text
    """
    global _ocr_instance

    if _ocr_instance is None:
        try:
            logger.info("Initializing PaddleOCR (first run may download models)...")
            _ocr_instance = PaddleOCR(
                lang='en',
                use_textline_orientation=True,  # Auto-rotation enabled
                show_log=False  # Suppress verbose logs
            )
            logger.info("PaddleOCR initialized successfully!")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            raise

    return _ocr_instance


# ============================================================================
# PREPROCESSING FUNCTIONS
# ============================================================================

def preprocess(img: np.ndarray, use_adaptive: bool = True) -> np.ndarray:
    """
    Enhanced preprocessing for IC chip OCR.

    Pipeline:
    1. Grayscale conversion
    2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    3. Non-local means denoising
    4. Unsharp masking (sharpening)
    5. Morphological cleanup
    6. Adaptive/Otsu thresholding
    7. Auto-inversion (dark-on-light → light-on-dark)
    8. Small component removal

    Args:
        img: Input BGR image
        use_adaptive: Use adaptive thresholding (True) or Otsu (False)

    Returns:
        Binary preprocessed image (uint8)
    """
    # Input validation
    if img is None or img.size == 0:
        raise ValueError("Input image is empty or None")

    # Step 1: Convert BGR to grayscale
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()

    # Step 2: CLAHE (Contrast enhancement)
    clahe = cv2.createCLAHE(
        clipLimit=ProcessingParams.CLAHE_CLIP_LIMIT,
        tileGridSize=ProcessingParams.CLAHE_TILE_SIZE
    )
    enhanced = clahe.apply(gray)

    # Step 3: Non-local means denoising (preserves edges)
    denoised = cv2.fastNlMeansDenoising(
        enhanced,
        None,
        h=ProcessingParams.DENOISE_H,
        templateWindowSize=ProcessingParams.DENOISE_TEMPLATE_WINDOW,
        searchWindowSize=ProcessingParams.DENOISE_SEARCH_WINDOW
    )

    # Step 4: Unsharp masking (sharpening)
    gaussian = cv2.GaussianBlur(denoised, (0, 0), ProcessingParams.SHARPEN_GAUSSIAN_SIGMA)
    sharpened = cv2.addWeighted(
        denoised,
        ProcessingParams.SHARPEN_WEIGHT_ORIGINAL,
        gaussian,
        ProcessingParams.SHARPEN_WEIGHT_GAUSSIAN,
        0
    )

    # Step 5: Morphological cleanup (close small gaps)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    morph = cv2.morphologyEx(sharpened, cv2.MORPH_CLOSE, kernel)

    # Step 6: Thresholding
    if use_adaptive:
        binary = cv2.adaptiveThreshold(
            morph,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            ProcessingParams.ADAPTIVE_BLOCK_SIZE,
            ProcessingParams.ADAPTIVE_C
        )
    else:
        _, binary = cv2.threshold(
            morph,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

    # Step 7: Auto-invert if text is darker than background
    white_pixels = np.sum(binary == 255)
    black_pixels = np.sum(binary == 0)

    if black_pixels > white_pixels:
        binary = cv2.bitwise_not(binary)
        logger.debug("Image auto-inverted (dark text detected)")

    # Step 8: Remove tiny noise components
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    for i in range(1, num_labels):  # Skip background (label 0)
        area = stats[i, cv2.CC_STAT_AREA]
        if area < ProcessingParams.MIN_COMPONENT_AREA:
            binary[labels == i] = 0

    return binary

# ============================================================================
# PADDLEOCR EXECUTION
# ============================================================================

def run_paddleocr(img: np.ndarray, min_confidence: float = 0.0) -> List[OCRToken]:
    """
    Run PaddleOCR on preprocessed image and extract tokens.

    Args:
        img: Preprocessed image (grayscale or BGR)
        min_confidence: Minimum confidence threshold to include token

    Returns:
        List of OCRToken objects with detected text

    Note:
        PaddleOCR v3.3+ returns dict with keys:
        - rec_texts: List of recognized strings
        - rec_scores: List of confidence scores (0.0 to 1.0)
        - rec_polys: List of bounding polygons (4 corner points)
    """
    ocr = get_ocr_instance()

    try:
        # Run PaddleOCR prediction
        result = ocr.predict(img)

        if not result or not result[0]:
            logger.warning("PaddleOCR returned no results")
            return []

        ocr_result = result[0]

        # Extract results from PaddleOCR dict
        rec_texts = ocr_result.get("rec_texts", [])
        rec_scores = ocr_result.get("rec_scores", [])
        rec_polys = ocr_result.get("rec_polys", [])

        # Build token list
        tokens = []
        for i, text in enumerate(rec_texts):
            # Get confidence (default to 0.0 if missing)
            confidence = rec_scores[i] if i < len(rec_scores) else 0.0

            # Skip if below confidence threshold
            if confidence < min_confidence:
                continue

            # Skip empty/whitespace-only text
            text_clean = text.strip()
            if not text_clean:
                continue

            # Get bounding polygon
            bbox = rec_polys[i] if i < len(rec_polys) else [[0, 0], [0, 0], [0, 0], [0, 0]]

            # Calculate center points for grouping
            try:
                x_coords = [pt[0] for pt in bbox]
                y_coords = [pt[1] for pt in bbox]
                x_center = float(sum(x_coords) / len(x_coords))
                y_center = float(sum(y_coords) / len(y_coords))
            except Exception as e:
                logger.warning(f"Failed to calculate center for token '{text}': {e}")
                x_center, y_center = 0.0, 0.0

            # Create token
            token = OCRToken(
                text=text_clean.upper(),  # Normalize to uppercase
                confidence=float(confidence),
                bbox=bbox,
                y_center=y_center,
                x_center=x_center
            )
            tokens.append(token)

        logger.info(f"PaddleOCR extracted {len(tokens)} tokens (min_conf={min_confidence:.2f})")
        return tokens

    except Exception as e:
        logger.error(f"PaddleOCR execution failed: {e}")
        return []


# ============================================================================
# LINE GROUPING
# ============================================================================

def group_tokens_by_line(tokens: List[OCRToken]) -> List[GroupedLine]:
    """
    Group tokens into lines based on Y-coordinate proximity.

    Algorithm:
    1. Sort tokens by Y-coordinate (top to bottom)
    2. Group tokens with similar Y values (within tolerance)
    3. Sort tokens within each line by X-coordinate (left to right)
    4. Merge tokens into single text string per line

    Args:
        tokens: List of OCRToken objects

    Returns:
        List of GroupedLine objects, sorted top to bottom
    """
    if not tokens:
        return []

    # Sort tokens by Y position (top to bottom)
    sorted_tokens = sorted(tokens, key=lambda t: t.y_center)

    # Group into lines
    lines: List[List[OCRToken]] = []
    tolerance = ProcessingParams.LINE_GROUP_Y_TOLERANCE

    for token in sorted_tokens:
        # Check if token belongs to existing line
        placed = False
        for line in lines:
            line_y = sum(t.y_center for t in line) / len(line)
            if abs(token.y_center - line_y) <= tolerance:
                line.append(token)
                placed = True
                break

        # Create new line if not placed
        if not placed:
            lines.append([token])

    # Convert to GroupedLine objects
    grouped_lines = []
    for line_num, line_tokens in enumerate(lines):
        # Sort tokens left to right
        line_tokens.sort(key=lambda t: t.x_center)

        # Merge text with spaces
        merged_text = " ".join(t.text for t in line_tokens)

        # Calculate average confidence
        avg_conf = sum(t.confidence for t in line_tokens) / len(line_tokens)

        # Calculate line Y position
        y_pos = sum(t.y_center for t in line_tokens) / len(line_tokens)

        grouped_line = GroupedLine(
            line_number=line_num,
            tokens=line_tokens,
            merged_text=merged_text,
            avg_confidence=avg_conf,
            y_position=y_pos
        )
        grouped_lines.append(grouped_line)

    logger.info(f"Grouped {len(tokens)} tokens into {len(grouped_lines)} lines")
    return grouped_lines


# ============================================================================
# MULTI-LINE PART CODE MERGING
# ============================================================================

def try_merge_lines(
    lines: List[GroupedLine],
    min_confidence: float = ConfidenceThresholds.PART_CODE
) -> Optional[Dict[str, Any]]:
    """
    Attempt to intelligently merge multi-line text into a part code.

    Strategy:
    1. Try pattern matching (e.g., STM32 + alphanumeric forms)
    2. Fall back to smart concatenation (both lines alphanumeric + high confidence)
    3. If uncertain, return None (keep lines separate)

    Args:
        lines: List of GroupedLine objects
        min_confidence: Minimum confidence required for merging

    Returns:
        Dict with merge result or None if no merge recommended
    """
    if len(lines) < 2:
        return None  # Need at least 2 lines to merge

    # Try merging first two lines (most common case)
    line1 = lines[0]
    line2 = lines[1]

    # Check confidence requirements
    if line1.avg_confidence < min_confidence or line2.avg_confidence < min_confidence:
        logger.debug(f"Merge skipped: confidence too low ({line1.avg_confidence:.2f}, {line2.avg_confidence:.2f})")
        return None

    # Remove spaces for concatenation
    text1 = line1.merged_text.replace(" ", "")
    text2 = line2.merged_text.replace(" ", "")

    # Strategy 1: Pattern matching
    combined = text1 + text2
    matched, pattern_name = matches_known_pattern(combined)

    if matched:
        logger.info(f"Pattern match success: '{combined}' → {pattern_name}")
        return {
            "part_code": combined,
            "confidence": (line1.avg_confidence + line2.avg_confidence) / 2,
            "method": "pattern_match",
            "pattern": pattern_name,
            "source_lines": [0, 1],
            "original_texts": [text1, text2]
        }

    # Strategy 2: Smart concatenation (both alphanumeric, reasonable length)
    if (
        is_valid_part_code_format(text1, min_length=4) and
        is_valid_part_code_format(text2, min_length=4) and
        len(combined) >= ProcessingParams.MIN_PART_CODE_LENGTH
    ):
        logger.info(f"Smart concat success: '{text1}' + '{text2}' → '{combined}'")
        return {
            "part_code": combined,
            "confidence": (line1.avg_confidence + line2.avg_confidence) / 2,
            "method": "smart_concat",
            "pattern": None,
            "source_lines": [0, 1],
            "original_texts": [text1, text2]
        }

    # Strategy 3: No merge recommended
    logger.debug(f"No merge: '{text1}' + '{text2}' doesn't match patterns or criteria")
    return None


def extract_additional_fields(lines: List[GroupedLine]) -> Dict[str, Any]:
    """
    Extract secondary fields from remaining lines (lot code, date, country, etc.).

    Args:
        lines: List of GroupedLine objects (excluding part code lines)

    Returns:
        Dict with extracted fields
    """
    fields = {}

    for line in lines:
        text = line.merged_text.replace(" ", "")
        conf = line.avg_confidence

        # Lot code heuristic: Alphanumeric, 5-8 chars, high confidence
        if (
            5 <= len(text) <= 8 and
            text.isalnum() and
            any(c.isalpha() for c in text) and
            any(c.isdigit() for c in text) and
            conf >= ConfidenceThresholds.LOT_CODE
        ):
            if "lot_code" not in fields:
                fields["lot_code"] = text
                fields["lot_code_confidence"] = conf

        # Date code heuristic: 4 digits (e.g., YYWW)
        elif (
            len(text) == 4 and
            text.isdigit() and
            conf >= ConfidenceThresholds.DATE_CODE
        ):
            if "date_code" not in fields:
                fields["date_code"] = text
                fields["date_code_confidence"] = conf

        # Country code heuristic: 2-3 alpha chars
        elif (
            2 <= len(text) <= 3 and
            text.isalpha() and
            conf >= ConfidenceThresholds.COUNTRY
        ):
            if "country" not in fields:
                fields["country"] = text
                fields["country_confidence"] = conf

    return fields

# ============================================================================
# MULTI-PASS OCR EXECUTION
# ============================================================================

def run_ocr_multi_pass(
    img: np.ndarray,
    psm: int = 11  # Ignored (kept for backward compatibility)
) -> Dict[str, Any]:
    """
    Run multi-pass OCR with intelligent parsing and field extraction.

    Pipeline:
    1. Preprocess with adaptive thresholding
    2. Run PaddleOCR with full alphanumeric
    3. Group tokens into lines
    4. Try multi-line merging (pattern + smart concat)
    5. Extract secondary fields (lot, date, country)
    6. Optional fallback passes (numeric-only, alpha-only)
    """
    results = {}
    processing_notes = []

    # ========================================================================
    # PASS 1: Full Alphanumeric (Primary)
    # ========================================================================

    logger.info("Starting PASS 1: Full Alphanumeric")

    # Preprocess with adaptive thresholding
    binary_adaptive = preprocess(img, use_adaptive=True)

    # Run PaddleOCR
    tokens = run_paddleocr(binary_adaptive, min_confidence=ConfidenceThresholds.MANUFACTURER)

    if tokens:
        # Group into lines
        grouped_lines = group_tokens_by_line(tokens)

        # Combine all text
        all_text = " ".join(line.merged_text for line in grouped_lines)
        avg_conf = sum(line.avg_confidence for line in grouped_lines) / len(grouped_lines)

        results["full_alphanumeric"] = {
            "text": all_text,
            "confidence": avg_conf
        }

        # Store raw data
        results["raw_tokens"] = [
            {
                "text": t.text,
                "confidence": t.confidence,
                "bbox": t.bbox,
                "y": t.y_center,
                "x": t.x_center
            }
            for t in tokens
        ]

        results["grouped_lines"] = [
            {
                "line": line.line_number,
                "text": line.merged_text,
                "confidence": line.avg_confidence,
                "y_position": line.y_position
            }
            for line in grouped_lines
        ]

        # ====================================================================
        # INTELLIGENT PARSING
        # ====================================================================

        parsed_fields = {}

        # Try multi-line merging
        merge_result = try_merge_lines(grouped_lines, min_confidence=ConfidenceThresholds.PART_CODE)

        if merge_result:
            # Successful merge
            parsed_fields["part_code"] = merge_result["part_code"]
            parsed_fields["part_code_confidence"] = merge_result["confidence"]
            parsed_fields["part_code_method"] = merge_result["method"]
            parsed_fields["part_code_pattern"] = merge_result.get("pattern")
            parsed_fields["part_code_lines"] = merge_result["original_texts"]

            processing_notes.append(
                f"Part code merged: {' + '.join(merge_result['original_texts'])} "
                f"→ {merge_result['part_code']} (method: {merge_result['method']})"
            )

            # Get manufacturer prefix
            prefix = get_manufacturer_prefix(merge_result["part_code"])
            if prefix:
                parsed_fields["manufacturer_prefix"] = prefix

            # Extract additional fields from remaining lines
            remaining_lines = grouped_lines[2:]  # Skip first 2 (used for part code)
            additional = extract_additional_fields(remaining_lines)
            parsed_fields.update(additional)

        else:
            # No merge - treat first line as part code
            if grouped_lines:
                first_line = grouped_lines[0]
                parsed_fields["part_code"] = first_line.merged_text.replace(" ", "")
                parsed_fields["part_code_confidence"] = first_line.avg_confidence
                parsed_fields["part_code_method"] = "single_line"
                parsed_fields["part_code_lines"] = [first_line.merged_text]

                processing_notes.append(f"Part code single line: {first_line.merged_text}")

                # Get manufacturer prefix
                prefix = get_manufacturer_prefix(parsed_fields["part_code"])
                if prefix:
                    parsed_fields["manufacturer_prefix"] = prefix

                # Extract additional fields from remaining lines
                remaining_lines = grouped_lines[1:]
                additional = extract_additional_fields(remaining_lines)
                parsed_fields.update(additional)

        results["parsed_fields"] = parsed_fields

    else:
        logger.warning("PASS 1 extracted no tokens")
        results["full_alphanumeric"] = {"text": "", "confidence": 0.0}
        results["raw_tokens"] = []
        results["grouped_lines"] = []
        results["parsed_fields"] = {}

    # ========================================================================
    # PASS 2: Numeric-Only (Fallback for lot/date codes)
    # ========================================================================

    logger.info("Starting PASS 2: Numeric-Only")

    # Try Otsu thresholding for numeric extraction
    binary_otsu = preprocess(img, use_adaptive=False)
    tokens_numeric = run_paddleocr(binary_otsu, min_confidence=ConfidenceThresholds.LOT_CODE)

    # Filter to numeric only
    numeric_tokens = [t for t in tokens_numeric if t.text.isdigit()]

    if numeric_tokens:
        numeric_text = " ".join(t.text for t in numeric_tokens)
        numeric_conf = sum(t.confidence for t in numeric_tokens) / len(numeric_tokens)
        results["numeric_only"] = {
            "text": numeric_text,
            "confidence": numeric_conf
        }
    else:
        results["numeric_only"] = {"text": "", "confidence": 0.0}

    # ========================================================================
    # PASS 3: Alpha-Only (Fallback for manufacturer marks)
    # ========================================================================

    logger.info("Starting PASS 3: Alpha-Only")

    # Filter to alpha only
    alpha_tokens = [t for t in tokens if t.text.isalpha()]

    if alpha_tokens:
        alpha_text = " ".join(t.text for t in alpha_tokens)
        alpha_conf = sum(t.confidence for t in alpha_tokens) / len(alpha_tokens)
        results["alpha_only"] = {
            "text": alpha_text,
            "confidence": alpha_conf
        }
    else:
        results["alpha_only"] = {"text": "", "confidence": 0.0}

    # ========================================================================
    # OVERALL CONFIDENCE
    # ========================================================================

    confidences = [
        results["full_alphanumeric"]["confidence"],
        results.get("parsed_fields", {}).get("part_code_confidence", 0.0)
    ]
    confidences = [c for c in confidences if c > 0]

    if confidences:
        overall_conf = sum(confidences) / len(confidences)
    else:
        overall_conf = 0.0

    results["overall_confidence"] = overall_conf
    results["processing_notes"] = processing_notes

    # Log summary
    logger.info(f"OCR Complete: {len(tokens)} tokens, {len(grouped_lines)} lines, "
                f"overall_conf={overall_conf:.2f}")

    return results


# ============================================================================
# BACKWARD-COMPATIBLE SINGLE-PASS FUNCTION
# ============================================================================

def run_ocr(
    img: np.ndarray,
    psm: int = 11,  # Ignored (kept for backward compatibility)
    whitelist: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"  # Ignored
) -> Tuple[str, float]:
    """
    Run OCR and return simple (text, confidence) tuple.

    Args:
        img: Input BGR image
        psm: Ignored
        whitelist: Ignored

    Returns:
        (extracted_text, average_confidence)
    """
    # Run full multi-pass pipeline
    results = run_ocr_multi_pass(img, psm=psm)

    # Extract part code if available, otherwise use full text
    parsed = results.get("parsed_fields", {})

    if "part_code" in parsed:
        text = parsed["part_code"]
        confidence = parsed.get("part_code_confidence", 0.0)
    else:
        text = results.get("full_alphanumeric", {}).get("text", "")
        confidence = results.get("full_alphanumeric", {}).get("confidence", 0.0)

    return text, confidence


# ============================================================================
# UTILITY FUNCTION (Kept for compatibility)
# ============================================================================

def parse_ocr_output(data: dict) -> str:
    """
    Parse OCR output dict (legacy Tesseract format).

    Deprecated: Kept for backward compatibility only.
    """
    logger.warning("parse_ocr_output() is deprecated (Tesseract removed)")
    return ""


# ============================================================================
# MODULE TESTING
# ============================================================================

if __name__ == "__main__":
    import sys

    print("="*60)
    print("PaddleOCR Module Test")
    print("SIH 25162 - AOI IC Verification")
    print("Author: Saif (CommitSaif11) | Mentor: Zoe 💙")
    print("="*60)

    # Test image path
    if len(sys.argv) > 1:
        test_image_path = sys.argv[1]
    else:
        test_image_path = r"C:\Users\hp\Desktop\SIH25162 Final Project\backend\generated. png"

    print(f"\nLoading image: {test_image_path}")

    test_img = cv2.imread(test_image_path)
    if test_img is None:
        print("❌ Failed to load image!")
        sys.exit(1)

    print(f"✅ Image loaded: {test_img.shape}")

    # Test simple interface
    print("\n" + "="*60)
    print("TEST 1: Simple run_ocr()")
    print("="*60)
    text, conf = run_ocr(test_img)
    print(f"Text: {text}")
    print(f"Confidence: {conf:.3f}")

    # Test detailed interface
    print("\n" + "="*60)
    print("TEST 2: Detailed run_ocr_multi_pass()")
    print("="*60)
    results = run_ocr_multi_pass(test_img)

    print("\n📋 Full Alphanumeric:")
    print(f"  Text: {results['full_alphanumeric']['text']}")
    print(f"  Confidence: {results['full_alphanumeric']['confidence']:.3f}")

    print("\n📋 Parsed Fields:")
    for key, value in results.get("parsed_fields", {}).items():
        print(f"  {key}: {value}")

    print("\n📋 Grouped Lines:")
    for line in results.get("grouped_lines", []):
        print(f"  Line {line['line']}: {line['text']:<30} (conf: {line['confidence']:.3f})")

    print("\n📋 Processing Notes:")
    for note in results.get("processing_notes", []):
        print(f"  - {note}")

    print(f"\n✅ Overall Confidence: {results['overall_confidence']:.3f}")
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)