"""
OCR Module - Enhanced Multi-Pass Tesseract Text Extraction
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
    Enhanced preprocessing for IC chip OCR
    
    Optimized for:
    - Laser-etched text
    - Low contrast markings
    - Multi-line text
    - Industrial IC images
    
    Author: Saif (CommitSaif11)
    Mentor: Zoe 💙
    """
    # Convert BGR to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Step 1: CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Step 2: Mild denoising
    denoised = cv2. fastNlMeansDenoising(enhanced, None, h=10, templateWindowSize=7, searchWindowSize=21)
    
    # Step 3: Sharpening
    gaussian = cv2.GaussianBlur(denoised, (0, 0), 2.0)
    sharpened = cv2.addWeighted(denoised, 1.5, gaussian, -0.5, 0)
    
    # Step 4: Morphological cleanup
    kernel = cv2.getStructuringElement(cv2. MORPH_RECT, (2, 2))
    morph = cv2.morphologyEx(sharpened, cv2. MORPH_CLOSE, kernel)
    
    # Step 5: Thresholding
    if use_adaptive:
        binary = cv2.adaptiveThreshold(
            morph,
            255,
            cv2. ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2. THRESH_BINARY,
            25,
            10
        )
    else:
        _, binary = cv2.threshold(
            morph,
            0,
            255,
            cv2. THRESH_BINARY + cv2. THRESH_OTSU
        )
    
    # Step 6: Auto-invert if needed
    white_pixels = np.sum(binary == 255)
    black_pixels = np.sum(binary == 0)
    
    if black_pixels > white_pixels:
        binary = cv2.bitwise_not(binary)
    
    # Step 7: Remove tiny noise
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area < 10:
            binary[labels == i] = 0
    
    return binary


def run_ocr_single_pass(
    img: np.ndarray, 
    psm: int, 
    whitelist: str
) -> Tuple[str, float]:
    """Run single-pass Tesseract OCR"""
    custom_config = f"--oem 3 --psm {psm} -c tessedit_char_whitelist={whitelist}"
    
    data = pytesseract.image_to_data(
        img,
        config=custom_config,
        output_type=pytesseract. Output.DICT
    )
    
    extracted_text = parse_ocr_output(data)
    
    confidences = []
    for i, conf in enumerate(data['conf']):
        if conf != -1 and data['text'][i].strip():
            confidences.append(float(conf))
    
    if confidences:
        avg_conf = sum(confidences) / len(confidences) / 100.0
    else:
        avg_conf = 0.0
    
    return extracted_text, avg_conf


def run_ocr_multi_pass(
    img: np.ndarray,
    psm: int = 11  # Changed to PSM 11 for IC chips
) -> Dict[str, Dict[str, any]]:
    """
    Run multi-pass OCR with dual thresholding
    
    PSM 11 = Sparse text (best for IC markings)
    """
    results = {}
    
    # Preprocess with both methods
    binary_adaptive = preprocess(img, use_adaptive=True)
    binary_otsu = preprocess(img, use_adaptive=False)
    
    # Pass 1: Full alphanumeric (try both, pick best)
    text_adp, conf_adp = run_ocr_single_pass(binary_adaptive, psm=psm, whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    text_otsu, conf_otsu = run_ocr_single_pass(binary_otsu, psm=psm, whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    
    if conf_adp > conf_otsu:
        results["full_alphanumeric"] = {"text": text_adp, "confidence": conf_adp}
    else:
        results["full_alphanumeric"] = {"text": text_otsu, "confidence": conf_otsu}
    
    # Pass 2: Numeric only
    text_num, conf_num = run_ocr_single_pass(binary_adaptive, psm=psm, whitelist="0123456789")
    results["numeric_only"] = {"text": text_num, "confidence": conf_num}
    
    # Pass 3: Alpha only
    text_alpha, conf_alpha = run_ocr_single_pass(binary_adaptive, psm=psm, whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    results["alpha_only"] = {"text": text_alpha, "confidence": conf_alpha}
    
    return results


def run_ocr(
    img: np.ndarray, 
    psm: int = 11,  # Changed default
    whitelist: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
) -> Tuple[str, float]:
    """Backward compatible single-pass OCR"""
    binary = preprocess(img, use_adaptive=True)
    return run_ocr_single_pass(binary, psm, whitelist)


def parse_ocr_output(data: dict) -> str:
    """Parse and clean Tesseract output"""
    words = []
    for i, text in enumerate(data['text']):
        cleaned = text.strip()
        if cleaned:
            words.append(cleaned. upper())
    
    final_text = " ".join(words)
    return final_text