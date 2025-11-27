"""
RegEx-Based Verification Algorithm
Direct pattern matching when part_id is known
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)
Mentor: Zoe 💙
"""

import re
from typing import Dict, Optional, Any
from engine.kb_index import KBIndex, CompiledPatterns
from engine.kb_loader import KBEntry
from . scoring import (
    VerificationResult,
    validate_date_code,
    calculate_verdict,
    normalize_ocr_text,
    correct_ocr_confusion
)


def extract_fields_with_regex(
    text: str,
    numeric_text: str,
    compiled_patterns: CompiledPatterns,
    kb_entry: KBEntry
) -> Dict[str, Optional[str]]:
    """
    Extract IC marking fields using regex patterns
    
    Args:
        text: Normalized alphanumeric OCR text
        numeric_text: Numeric-only OCR text (for date codes)
        compiled_patterns: Compiled regex patterns for this IC
        kb_entry: KB entry for logo hint checking
    
    Returns:
        Dictionary of extracted fields
    
    Note for Saif:
        Uses multi-pass OCR results for better accuracy
    """
    extracted = {
        "part_code": None,
        "date_code": None,
        "lot_code": None,
        "logo_hint": None,
        "date_validation": None
    }
    
    # Extract part code from alphanumeric text
    part_match = compiled_patterns.part_code.search(text)
    if part_match:
        extracted["part_code"] = part_match.group(0)
    
    # Extract date code from numeric-only text (more accurate)
    date_match = compiled_patterns.date_code.search(numeric_text)
    if date_match:
        date_code = date_match.group(0)
        extracted["date_code"] = date_code
        
        # Validate date code
        extracted["date_validation"] = validate_date_code(date_code)
    
    # Extract lot code from alphanumeric text
    lot_match = compiled_patterns.lot_code.search(text)
    if lot_match:
        extracted["lot_code"] = lot_match.group(0)
    
    # Check for logo hint
    if kb_entry.logo_hint and kb_entry.logo_hint.strip():
        logo_pattern = re.compile(re.escape(kb_entry.logo_hint), re.IGNORECASE)
        if logo_pattern.search(text):
            extracted["logo_hint"] = kb_entry.logo_hint
    
    return extracted


def verify_with_regex_logic(
    ocr_results: Dict[str, Dict[str, Any]],
    part_id: str,
    kb_index: KBIndex
) -> VerificationResult:
    """
    Main RegEx verification algorithm
    
    Args:
        ocr_results: Multi-pass OCR results
        part_id: User-specified IC part identifier
        kb_index: Loaded KB index
    
    Returns:
        VerificationResult with verdict and details
    
    Workflow for Saif:
        1.  Normalize and correct OCR text
        2.  Get compiled patterns for part_id
        3. Extract fields using regex
        4. Calculate verdict with weighted scoring
    """
    # Validate part_id exists in KB
    if part_id not in kb_index.regex_map:
        return VerificationResult(
            verdict="ERROR",
            confidence_score=0.0,
            algorithm_used="regex",
            flags=["UNKNOWN_PART_ID"],
            matches={},
            extracted_fields={}
        )
    
    # Get KB entry and compiled patterns
    kb_entry = next(e for e in kb_index.entries if e.part_id == part_id)
    compiled_patterns = kb_index.regex_map[part_id]
    
    # Normalize OCR texts (Saif's split-text fix)
    alphanum_text = normalize_ocr_text(ocr_results["full_alphanumeric"]["text"])
    
    # Correct OCR confusions (automatic as per Saif's decision)
    numeric_text = correct_ocr_confusion(
        ocr_results["numeric_only"]["text"],
        context="numeric"
    )
    alpha_text = correct_ocr_confusion(
        ocr_results["alpha_only"]["text"],
        context="alpha"
    )
    
    # Extract fields using regex patterns
    extracted_fields = extract_fields_with_regex(
        alphanum_text,
        numeric_text,
        compiled_patterns,
        kb_entry
    )
    
    # Build match results
    matches = {
        "part_code_match": extracted_fields["part_code"] is not None,
        "date_code_match": extracted_fields["date_code"] is not None,
        "lot_code_match": extracted_fields["lot_code"] is not None,
        "logo_hint_match": extracted_fields["logo_hint"] is not None
    }
    
    # Get average OCR confidence
    avg_ocr_conf = (
        ocr_results["full_alphanumeric"]["confidence"] +
        ocr_results["numeric_only"]["confidence"]
    ) / 2.0
    
    # Calculate verdict (with Saif's weighted scoring)
    verdict, confidence, flags = calculate_verdict(
        matches=matches,
        ocr_confidence=avg_ocr_conf,
        date_validation=extracted_fields["date_validation"],
        logo_found=matches["logo_hint_match"]
    )
    
    # Build OEM info
    oem_info = {
        "oem": kb_entry.oem,
        "part_number": kb_entry.part_number,
        "package": kb_entry.package
    }
    
    # Return complete result
    return VerificationResult(
        verdict=verdict,
        confidence_score=confidence,
        algorithm_used="regex",
        matches=matches,
        extracted_fields=extracted_fields,
        oem_info=oem_info,
        flags=flags,
        weighted_score=None  # Will be added in scoring
    )