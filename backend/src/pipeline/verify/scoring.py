"""
Scoring and Verdict Calculation Logic
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)

"""

import datetime
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

# Weighted scoring as per Saif's decision
MATCH_WEIGHTS = {
    "part_code": 0.60,   # Most critical - identifies the IC
    "date_code": 0.25,   # Important - validates manufacturing
    "lot_code": 0.15     # Least critical - batch identification
}

# Logo bonus (small boost for brand verification)
LOGO_BONUS = 0.05

# Industry standard ambiguity threshold (0.20 score difference)
AMBIGUITY_THRESHOLD = 0.20


@dataclass
class VerificationResult:
    """
    Standardized verification output for Saif's API endpoints
    """
    verdict: str  # "GENUINE", "FAKE", "UNCERTAIN", "MULTIPLE_CANDIDATES"
    confidence_score: float  # 0.0 to 1.0
    algorithm_used: str  # "regex" or "aho_corasick"
    
    matches: Dict[str, bool] = field(default_factory=dict)
    extracted_fields: Dict[str, Optional[str]] = field(default_factory=dict)
    oem_info: Dict[str, str] = field(default_factory=dict)
    
    # Optional fields for advanced scenarios
    flags: List[str] = field(default_factory=list)
    candidate_parts: Optional[List[Dict[str, Any]]] = None
    requires_admin_review: bool = False
    
    # Metadata
    weighted_score: Optional[float] = None
    match_validity: Optional[str] = None


def validate_date_code(date_code: str) -> Dict[str, Any]:
    """
    Validate IC manufacturing date code (YYWW format)
    
    Args:
        date_code: 4-digit date code (e.g., "2347" = 2023 Week 47)
    
    Returns:
        Validation result with flags for any issues
    
    Note for Saif:
        Future dates = instant FAKE verdict
    """
    if not re.match(r'^\d{4}$', date_code):
        return {
            "valid": False,
            "year": None,
            "week": None,
            "flags": ["INVALID_FORMAT"]
        }
    
    year_part = int(date_code[:2])
    week_part = int(date_code[2:])
    
    # Convert YY to YYYY (assume 2000-2099)
    full_year = 2000 + year_part
    
    # Get current date info
    now = datetime.datetime.now()
    current_year = now.year
    current_week = now.isocalendar()[1]
    
    flags = []
    
    # Critical Check 1: Future date (instant FAKE as per Saif's requirement)
    if full_year > current_year:
        flags.append("FUTURE_YEAR")
    elif full_year == current_year and week_part > current_week:
        flags.append("FUTURE_WEEK")
    
    # Check 2: Valid week range (1-53)
    if week_part < 1 or week_part > 53:
        flags.append("INVALID_WEEK")
    
    # Special case: Week 00
    if week_part == 0:
        flags.append("WEEK_ZERO_INVALID")
    
    # Check 3: Very old IC (might be refurbished/remarked)
    if full_year < current_year - 20:
        flags.append("VERY_OLD_IC")
    
    valid = len([f for f in flags if f not in ["VERY_OLD_IC"]]) == 0
    
    return {
        "valid": valid,
        "year": full_year,
        "week": week_part,
        "flags": flags
    }


def calculate_weighted_score(matches: Dict[str, bool]) -> float:
    """
    Calculate weighted match score using Saif's approved weights
    
    Args:
        matches: Dictionary of match results
    
    Returns:
        Weighted score from 0.0 to 1.0
    """
    score = 0.0
    
    if matches.get("part_code_match", False):
        score += MATCH_WEIGHTS["part_code"]
    
    if matches.get("date_code_match", False):
        score += MATCH_WEIGHTS["date_code"]
    
    if matches.get("lot_code_match", False):
        score += MATCH_WEIGHTS["lot_code"]
    
    return score


def calculate_match_validity(matches: Dict[str, bool]) -> str:
    """
    Determine if match set provides sufficient evidence
    
    Args:
        matches: Dictionary of match results
    
    Returns:
        Validity classification
    
    Note for Saif:
        Prevents false positives from weak evidence (e.g., logo-only matches)
    """
    part_match = matches.get("part_code_match", False)
    date_match = matches.get("date_code_match", False)
    lot_match = matches.get("lot_code_match", False)
    logo_match = matches.get("logo_hint_match", False)
    
    # Scenario 1: Part code matched = Strong evidence
    if part_match:
        return "STRONG_EVIDENCE"
    
    # Scenario 2: Logo + Date + Lot (no part) = Acceptable combined evidence
    if logo_match and date_match and lot_match:
        return "COMBINED_EVIDENCE"
    
    # Scenario 3: Only lot code = Insufficient (too generic)
    if lot_match and not (part_match or date_match):
        return "INSUFFICIENT_EVIDENCE"
    
    # Scenario 4: Only logo = Weak (many ICs share manufacturers)
    if logo_match and not (part_match or date_match or lot_match):
        return "WEAK_EVIDENCE"
    
    # Scenario 5: Date + Lot (no part, no logo) = Marginal
    if date_match and lot_match and not part_match:
        return "MARGINAL_EVIDENCE"
    
    return "NO_EVIDENCE"


def calculate_verdict(
    matches: Dict[str, bool],
    ocr_confidence: float,
    date_validation: Optional[Dict[str, Any]] = None,
    logo_found: bool = False
) -> tuple[str, float, List[str]]:
    """
    Calculate final verdict and confidence score
    
    Args:
        matches: Pattern match results
        ocr_confidence: OCR quality (0.0 to 1.0)
        date_validation: Date code validation result
        logo_found: Whether logo hint was detected
    
    Returns:
        (verdict, confidence_score, flags)
    
    Note for Saif:
        This implements your weighted scoring + instant FAKE for future dates
    """
    flags = []
    
    # CRITICAL: Future date check (instant FAKE as per Saif's requirement)
    if date_validation and ("FUTURE_YEAR" in date_validation["flags"] or 
                           "FUTURE_WEEK" in date_validation["flags"]):
        return ("FAKE", 0.20, ["IMPOSSIBLE_FUTURE_DATE"])
    
    # Calculate weighted score
    weighted_score = calculate_weighted_score(matches)
    
    # Check match validity
    validity = calculate_match_validity(matches)
    
    # Handle insufficient evidence cases
    if validity in ["INSUFFICIENT_EVIDENCE", "WEAK_EVIDENCE", "NO_EVIDENCE"]:
        flags.append(f"MATCH_VALIDITY_{validity}")
        return ("UNCERTAIN", max(weighted_score * 0.5, 0.15), flags)
    
    # Base confidence from weighted score
    base_confidence = weighted_score
    
    # Apply logo bonus if found
    if logo_found:
        base_confidence += LOGO_BONUS
        flags.append("LOGO_VERIFIED")
    
    # Apply OCR confidence modifier
    if ocr_confidence < 0.50:
        base_confidence *= 0.85  # Penalize poor OCR quality
        flags.append("LOW_OCR_QUALITY")
    elif ocr_confidence < 0.70:
        base_confidence *= 0.95  # Slight penalty
        flags.append("MODERATE_OCR_QUALITY")

    # If date was captured but format is unknown (e.g., 3-digit fallback), annotate without penalizing to FAKE
    if date_validation and "UNKNOWN_DATE_FORMAT" in date_validation.get("flags", []):
        flags.append("UNKNOWN_DATE_FORMAT")

    # Safe, small bonuses for strong signals
    if matches.get("part_code_match") and logo_found and ocr_confidence > 0.80:
        base_confidence += 0.05
        flags.append("STRONG_PART_LOGO_EVIDENCE")

    if matches.get("lot_code_match"):
        base_confidence += 0.05
        # Keep a consistent flag name; also added in regex path when heuristics picked it
        if "LOT_HEURISTIC_MATCH" not in flags:
            flags.append("LOT_HEURISTIC_MATCH")
    
    # Cap confidence at 1.0
    final_confidence = min(base_confidence, 1.0)
    
    # Determine verdict based on final confidence
    # Industry standard thresholds (as per Saif's preference)
    if final_confidence >= 0.85:
        verdict = "GENUINE"
    elif final_confidence >= 0.50:
        verdict = "UNCERTAIN"
        flags.append("REQUIRES_MANUAL_INSPECTION")
    else:
        verdict = "FAKE"
    
    return (verdict, final_confidence, flags)


def normalize_ocr_text(text: str) -> str:
    """
    Normalize OCR text for better pattern matching
    
    Handles:
    - Extra whitespace removal
    - Split part numbers (e.g., "STM32F030 C8T6" → "STM32F030C8T6")
    - Uppercase conversion
    
    Args:
        text: Raw OCR output
    
    Returns:
        Normalized text
    
    Note for Saif:
        Fixes OCR split/multiline issues you identified
    """
    # Remove extra whitespace between alphanumerics
    # "STM32F030 C8T6" → "STM32F030C8T6"
    normalized = re.sub(r'(\w)\s+(\w)', r'\1\2', text)
    
    # Convert to uppercase
    normalized = normalized.upper()
    
    # Remove excessive spaces
    normalized = ' '.join(normalized.split())
    
    return normalized


def correct_ocr_confusion(text: str, context: str = "alphanumeric") -> str:
    """
    Correct common OCR character confusions
    
    Common mistakes:
    - O ↔ 0 (letter O vs zero)
    - I ↔ 1 (letter I vs one)
    - B ↔ 8 (letter B vs eight)
    - S ↔ 5 (letter S vs five)
    
    Args:
        text: OCR output
        context: "numeric", "alpha", or "alphanumeric"
    
    Returns:
        Corrected text
    
    Note for Saif:
        Applied automatically as per your decision
    """
    if context == "numeric":
        # In numeric context, letters should be numbers
        text = text.replace('O', '0')
        text = text.replace('I', '1')
        text = text.replace('S', '5')
        text = text.replace('B', '8')
        text = text.replace('Z', '2')
    
    elif context == "alpha":
        # In alpha context, numbers should be letters
        text = text.replace('0', 'O')
        text = text.replace('1', 'I')
        text = text.replace('5', 'S')
        text = text.replace('8', 'B')
        text = text.replace('2', 'Z')
    
    # For alphanumeric context, we keep as-is
    # (regex patterns handle both interpretations)
    
    return text