"""
RegEx-Based Verification Algorithm
Direct pattern matching when part_id is known
"""
import re
import logging
from typing import Dict, Optional, Any
from engine.kb_index import KBIndex, CompiledPatterns
from engine.kb_loader import KBEntry
from .scoring import (
    VerificationResult,
    validate_date_code,
    calculate_verdict,
    normalize_ocr_text,
    correct_ocr_confusion
)

log = logging.getLogger(__name__)

def _aggressive_normalize(text: str) -> str:
    """
    Strong normalization to help regex match:
    - Uppercase
    - Collapse whitespace
    - Remove common separators: '-', '_'
    """
    t = (text or "").upper()
    t = re.sub(r'[\-\_]', '', t)      # remove hyphen/underscore
    t = re.sub(r'\s+', ' ', t).strip()  # collapse spaces
    return t

def verify_with_regex_logic(
    ocr_results: Dict[str, Dict[str, Any]],
    part_id: str,
    kb_index: KBIndex
) -> VerificationResult:
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

    kb_entry = next(e for e in kb_index.entries if e.part_id == part_id)
    compiled_patterns = kb_index.regex_map[part_id]

    # Normalize OCR texts
    raw_alphanum = ocr_results["full_alphanumeric"]["text"]
    alphanum_text = normalize_ocr_text(raw_alphanum)
    alphanum_text_norm = _aggressive_normalize(alphanum_text)

    numeric_text_raw = ocr_results["numeric_only"]["text"]
    numeric_text = correct_ocr_confusion(numeric_text_raw, context="numeric")

    # DEBUG logs
    log.info(f"[VERIFY regex] part_id={part_id}")
    log.info(f"[VERIFY regex] alphanum_raw='{raw_alphanum}'")
    log.info(f"[VERIFY regex] alphanum_norm='{alphanum_text_norm}'")
    log.info(f"[VERIFY regex] numeric_raw='{numeric_text_raw}' -> '{numeric_text}'")

    # Extract fields using regex patterns against aggressively normalized text
    part_match = compiled_patterns.part_code.search(alphanum_text_norm)
    lot_match = compiled_patterns.lot_code.search(alphanum_text_norm)
    date_match = compiled_patterns.date_code.search(numeric_text)

    extracted_fields = {
        "part_code": part_match.group(0) if part_match else None,
        "date_code": None,
        "lot_code": lot_match.group(0) if lot_match else None,
        "logo_hint": None,
        "date_validation": None
    }

    if date_match:
        date_code = date_match.group(0)
        # Normalize O->0 in date code before validation
        date_code = date_code.replace('O', '0')
        extracted_fields["date_code"] = date_code
        extracted_fields["date_validation"] = validate_date_code(date_code)

    # Logo hint
    if kb_entry.logo_hint and kb_entry.logo_hint.strip():
        logo_pattern = re.compile(re.escape(kb_entry.logo_hint), re.IGNORECASE)
        if logo_pattern.search(alphanum_text_norm):
            extracted_fields["logo_hint"] = kb_entry.logo_hint

    matches = {
        "part_code_match": extracted_fields["part_code"] is not None,
        "date_code_match": extracted_fields["date_code"] is not None,
        "lot_code_match": extracted_fields["lot_code"] is not None,
        "logo_hint_match": extracted_fields["logo_hint"] is not None
    }

    avg_ocr_conf = (
        ocr_results["full_alphanumeric"]["confidence"] +
        ocr_results["numeric_only"]["confidence"]
    ) / 2.0

    verdict, confidence, flags = calculate_verdict(
        matches=matches,
        ocr_confidence=avg_ocr_conf,
        date_validation=extracted_fields["date_validation"],
        logo_found=matches["logo_hint_match"]
    )

    oem_info = {
        "oem": kb_entry.oem,
        "part_number": kb_entry.part_number,
        "package": kb_entry.package
    }

    return VerificationResult(
        verdict=verdict,
        confidence_score=confidence,
        algorithm_used="regex",
        matches=matches,
        extracted_fields=extracted_fields,
        oem_info=oem_info,
        flags=flags,
        weighted_score=None
    )