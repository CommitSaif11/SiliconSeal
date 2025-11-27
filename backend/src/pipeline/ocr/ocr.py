"""
OCR Module - Multi-Pass Tesseract Text Extraction
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)
Mentor: Zoe 💙
"""

import cv2
import numpy as np
import pytesseract
from typing import Tuple, Dict, Optional

# Configure Tesseract executable path for Saif's Windows installation
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def preprocess(img: np.ndarray, use_adaptive: bool = True) -> np.ndarray:
    """
    Preprocess image for optimal OCR results
    
    Args:
        img: Input image (BGR format from OpenCV)
        use_adaptive: Use adaptive thresholding if True, else Otsu
    
    Returns:
        Preprocessed binary image ready for Tesseract
    
    Note for Saif:
        This improves OCR accuracy on IC markings significantly
    """
    # Convert BGR to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply bilateral filter to reduce noise while preserving edges
    # This helps with IC marking text clarity
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Normalize intensity to improve contrast
    # This handles varying lighting conditions in industrial settings
    normalized = cv2. normalize(filtered, None, 0, 255, cv2. NORM_MINMAX)
    
    # Apply thresholding based on Saif's preference
    if use_adaptive:
        # Adaptive thresholding works better for uneven lighting
        # Common in factory floor camera setups
        binary = cv2.adaptiveThreshold(
            normalized,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2. THRESH_BINARY,
            11,  # Block size
            2    # Constant subtracted from mean
        )
    else:
        # Otsu's thresholding for uniform lighting conditions
        _, binary = cv2.threshold(
            normalized,
            0,
            255,
            cv2. THRESH_BINARY + cv2.THRESH_OTSU
        )
    
    return binary


def run_ocr_single_pass(
    img: np.ndarray, 
    psm: int, 
    whitelist: str
) -> Tuple[str, float]:
    """
    Run single-pass Tesseract OCR with specific whitelist
    
    Args:
        img: Preprocessed binary image
        psm: Page Segmentation Mode
        whitelist: Character whitelist for this pass
    
    Returns:
        Tuple of (extracted_text, average_confidence)
    """
    # Configure Tesseract with Saif's specified parameters
    custom_config = f"--oem 3 --psm {psm} -c tessedit_char_whitelist={whitelist}"
    
    # Run Tesseract OCR and get detailed output data
    data = pytesseract.image_to_data(
        img,
        config=custom_config,
        output_type=pytesseract. Output.DICT
    )
    
    # Parse the OCR output for Saif
    extracted_text = parse_ocr_output(data)
    
    # Calculate average confidence from valid detections
    confidences = []
    for i, conf in enumerate(data['conf']):
        # Filter out invalid confidence values (-1 means no detection)
        if conf != -1 and data['text'][i]. strip():
            confidences.append(float(conf))
    
    # Compute average confidence normalized to 0. 0-1.0 range
    if confidences:
        avg_conf = sum(confidences) / len(confidences) / 100.0
    else:
        avg_conf = 0.0
    
    return extracted_text, avg_conf


def run_ocr_multi_pass(
    img: np.ndarray,
    psm: int = 6
) -> Dict[str, Dict[str, any]]:
    """
    Run multi-pass OCR with field-specific whitelists (OPTION B)
    
    This is Saif's chosen approach for maximum accuracy! 
    
    Args:
        img: Preprocessed binary image (full IC marking area)
        psm: Page Segmentation Mode (6=uniform block, 7=single line)
    
    Returns:
        Dictionary containing results from all passes:
        {
            "full_alphanumeric": {
                "text": "STM32F030C8T6 2347 A3B5C",
                "confidence": 0. 87
            },
            "numeric_only": {
                "text": "2347",
                "confidence": 0.92
            },
            "alpha_only": {
                "text": "STMFCT ABC",
                "confidence": 0.78
            }
        }
    
    Note for Saif:
        Each pass uses a different character whitelist for better accuracy
    """
    results = {}
    
    # Pass 1: Full alphanumeric (for part codes and lot codes)
    text_alphanum, conf_alphanum = run_ocr_single_pass(
        img,
        psm=psm,
        whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )
    results["full_alphanumeric"] = {
        "text": text_alphanum,
        "confidence": conf_alphanum
    }
    
    # Pass 2: Numeric only (for date codes - prevents letter misreads)
    text_numeric, conf_numeric = run_ocr_single_pass(
        img,
        psm=psm,
        whitelist="0123456789"
    )
    results["numeric_only"] = {
        "text": text_numeric,
        "confidence": conf_numeric
    }
    
    # Pass 3: Alpha only (for logo hints and OEM names)
    text_alpha, conf_alpha = run_ocr_single_pass(
        img,
        psm=psm,
        whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )
    results["alpha_only"] = {
        "text": text_alpha,
        "confidence": conf_alpha
    }
    
    return results


def run_ocr(
    img: np.ndarray, 
    psm: int = 6, 
    whitelist: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
) -> Tuple[str, float]:
    """
    Main OCR function (backward compatible with single-pass mode)
    
    Args:
        img: Preprocessed binary image
        psm: Page Segmentation Mode
        whitelist: Character whitelist (for single-pass mode)
    
    Returns:
        Tuple of (extracted_text, average_confidence)
    
    Note for Saif:
        This is kept for backward compatibility. 
        Use run_ocr_multi_pass() for better accuracy! 
    """
    return run_ocr_single_pass(img, psm, whitelist)


def parse_ocr_output(data: dict) -> str:
    """
    Parse Tesseract output data and clean extracted text
    
    Args:
        data: Dictionary from pytesseract.image_to_data
    
    Returns:
        Cleaned and formatted text string
    
    Note for Saif:
        Removes noise and combines words properly for IC marking verification
    """
    # Extract all valid text words
    words = []
    for i, text in enumerate(data['text']):
        # Remove empty strings and whitespace-only entries
        cleaned = text.strip()
        if cleaned:
            # Convert to uppercase for consistent matching
            words.append(cleaned.upper())
    
    # Combine words with single space separator
    final_text = " ".join(words)
    
    return final_text