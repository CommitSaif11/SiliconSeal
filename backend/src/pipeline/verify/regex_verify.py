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
    t = re.sub(r'[\-\_]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def _strip_word_boundaries(pattern: str) -> str:
    """
    Remove word boundaries and anchors from a regex pattern
    to allow matching inside concatenated alphanumeric strings.
    """
    return pattern.replace(r"\b", "").replace("^", "").replace("$", "")

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

    # Cleaned alphanumeric-only string for relaxed matching
    alphanum_only = ''.join(c for c in alphanum_text_norm if c.isalnum())

    # Keep numeric context for other uses, but date will be matched on alphanum_text_norm
    numeric_text_raw = ocr_results["numeric_only"]["text"]
    numeric_text = correct_ocr_confusion(numeric_text_raw, context="numeric")

    # DEBUG logs
    log.info(f"[VERIFY regex] part_id={part_id}")
    log.info(f"[VERIFY regex] alphanum_raw='{raw_alphanum}'")
    log.info(f"[VERIFY regex] alphanum_norm='{alphanum_text_norm}'")
    log.info(f"[VERIFY regex] alphanum_only='{alphanum_only}'")
    log.info(f"[VERIFY regex] numeric_raw='{numeric_text_raw}' -> '{numeric_text}'")

    # First try strict matching on normalized text
    part_match = compiled_patterns.part_code.search(alphanum_text_norm)
    # Lot/date initial regex tries on normalized alphanumeric text
    lot_match = compiled_patterns.lot_code.search(alphanum_text_norm)
    # IMPORTANT: match date on alphanumeric text (keeps boundaries/spaces), not on concatenated numerics
    date_match = compiled_patterns.date_code.search(alphanum_text_norm)

    # If part code didn’t match, try relaxed matching:
    # strip word boundaries and search against alphanumeric-only string
    if not part_match:
        try:
            pattern_str = compiled_patterns.part_code.pattern
            relaxed_pattern = _strip_word_boundaries(pattern_str)
            log.info(f"[VERIFY regex] relaxed part_code pattern='{relaxed_pattern}'")
            part_relaxed = re.search(relaxed_pattern, alphanum_only, re.IGNORECASE)
        except Exception as e:
            log.warning(f"[VERIFY regex] relaxed matching error: {e}")
            part_relaxed = None

        if part_relaxed:
            part_match = part_relaxed

    # Lot code heuristics: collect and select best candidate from full text and grouped lines
    lot_candidates = []
    try:
        lot_candidates += compiled_patterns.lot_code.findall(alphanum_text_norm)
    except Exception:
        pass

    grouped = ocr_results.get("grouped_lines", []) or []
    for g in grouped:
        try:
            line_text = " ".join(g.get("texts", [])).upper().strip()
            lot_candidates += compiled_patterns.lot_code.findall(line_text)
        except Exception:
            continue

    # Deduplicate candidates
    lot_candidates = list({c for c in lot_candidates})

    def _score_lot(token: str) -> int:
        t = token.upper().strip()
        score = 0
        length = len(t)
        has_alpha = any(c.isalpha() for c in t)
        has_digit = any(c.isdigit() for c in t)

        # Exclusions and penalties
        if length <= 2:
            return -3  # too short (e.g., "VQ")
        if not has_digit:
            return -2  # purely alphabetic (e.g., "PHL")

        # Preferences
        if 4 <= length <= 6:
            score += 3
        if has_alpha and has_digit:
            score += 2

        # Avoid picking the part code itself
        if part_match and t == part_match.group(0).upper():
            score -= 5

        return score

    selected_lot = None
    if lot_candidates:
        scored = sorted(
            [(c, _score_lot(c)) for c in lot_candidates],
            key=lambda x: (x[1], len(x[0])),
            reverse=True
        )
        if scored and scored[0][1] > 0:
            selected_lot = scored[0][0]
            log.info(f"[VERIFY regex] selected_lot='{selected_lot}' from candidates={lot_candidates}")

    # Build extracted fields
    extracted_fields = {
        "part_code": part_match.group(0) if part_match else None,
        "date_code": None,
        "lot_code": lot_match.group(0) if lot_match else (selected_lot if selected_lot else None),
        "logo_hint": None,
        "date_validation": None
    }

    # Date extraction and validation (allow fallback formats; annotate unknown format)
    if date_match:
        date_code = date_match.group(0).replace('O', '0')
        extracted_fields["date_code"] = date_code
        if re.match(r'^\d{4}$', date_code):
            extracted_fields["date_validation"] = validate_date_code(date_code)
        else:
            # Non-YYWW fallback captured (e.g., 3-digit) — mark unknown format
            extracted_fields["date_validation"] = {
                "valid": False,
                "year": None,
                "week": None,
                "flags": ["UNKNOWN_DATE_FORMAT"]
            }

    # Logo hint
    if kb_entry.logo_hint and kb_entry.logo_hint.strip():
        logo_pattern = re.compile(re.escape(kb_entry.logo_hint), re.IGNORECASE)
        if logo_pattern.search(alphanum_text_norm):
            extracted_fields["logo_hint"] = kb_entry.logo_hint

   # Only count 4-digit YYWW as a true date match
    date_valid = bool(
        extracted_fields.get("date_validation")
        and extracted_fields["date_validation"].get("valid")
    )

    matches = {
        "part_code_match": extracted_fields["part_code"] is not None,
        "date_code_match": date_valid,
        "lot_code_match": extracted_fields["lot_code"] is not None,
        "logo_hint_match": extracted_fields["logo_hint"] is not None,
    }

    # Average OCR confidence from two passes (as before)
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

    # If lot was selected via heuristic (not direct regex on full text), annotate
    if not lot_match and extracted_fields["lot_code"]:
        flags.append("LOT_HEURISTIC_MATCH")

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